from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import httpx

from app.models.database import get_db, ConnectedAccount, User, create_tables
from app.models.schemas import UserCreate, UserLogin, UserOut, TokenResponse
from app.auth.token_store import encrypt_token, decrypt_token
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ─────────────────────────────────────────
# JWT helpers
# ─────────────────────────────────────────
def create_jwt(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")

def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    token = authorization.split(" ")[1]
    payload = decode_jwt(token)
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ─────────────────────────────────────────
# Auth endpoints
# ─────────────────────────────────────────
@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    create_tables()
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_in.email,
        name=user_in.name,
        hashed_password=pwd_context.hash(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not pwd_context.verify(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt(str(user.id), user.email)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "email": user.email
    }

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user

# ─────────────────────────────────────────
# Google OAuth (YouTube + Gmail)
# ─────────────────────────────────────────
@router.get("/connect/google")
def connect_google():
    if not settings.google_client_id:
        raise HTTPException(status_code=400, detail="Google client ID not configured")
    scopes = " ".join([
        "openid", "email", "profile",
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/youtube.force-ssl",
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send"
    ])
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.google_client_id}"
        f"&redirect_uri={settings.google_redirect_uri}"
        f"&response_type=code"
        f"&scope={scopes}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return RedirectResponse(url)

@router.get("/callback/google")
async def google_callback(code: str, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code"
            }
        )
    token_data = token_resp.json()
    if "error" in token_data:
        raise HTTPException(status_code=400, detail=token_data["error"])

    async with httpx.AsyncClient() as client:
        info_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
    user_info = info_resp.json()

    user = db.query(User).filter(User.email == user_info["email"]).first()
    if not user:
        user = User(email=user_info["email"], name=user_info.get("name", ""))
        db.add(user)
        db.commit()
        db.refresh(user)

    _upsert_connection(db, user.id, "youtube", token_data, user_info["email"])
    _upsert_connection(db, user.id, "gmail",   token_data, user_info["email"])

    jwt_token = create_jwt(str(user.id), user.email)
    return {
        "message": "Google connected successfully",
        "platforms_connected": ["youtube", "gmail"],
        "user_email": user_info["email"],
        "access_token": jwt_token
    }

# ─────────────────────────────────────────
# Instagram OAuth
# ─────────────────────────────────────────
@router.get("/connect/instagram")
def connect_instagram():
    if not settings.meta_client_id:
        raise HTTPException(status_code=400, detail="Meta client ID not configured")
    url = (
        "https://api.instagram.com/oauth/authorize"
        f"?client_id={settings.meta_client_id}"
        f"&redirect_uri={settings.meta_redirect_uri}"
        f"&scope=instagram_basic,instagram_manage_comments,instagram_manage_messages"
        f"&response_type=code"
    )
    return RedirectResponse(url)

@router.get("/callback/instagram")
async def instagram_callback(code: str, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://api.instagram.com/oauth/access_token",
            data={
                "client_id": settings.meta_client_id,
                "client_secret": settings.meta_client_secret,
                "grant_type": "authorization_code",
                "redirect_uri": settings.meta_redirect_uri,
                "code": code
            }
        )
    token_data = token_resp.json()
    if "error" in token_data or "error_type" in token_data:
        raise HTTPException(status_code=400, detail=str(token_data))

    user_id_ig = str(token_data.get("user_id", ""))

    async with httpx.AsyncClient() as client:
        profile_resp = await client.get(
            f"https://graph.instagram.com/{user_id_ig}",
            params={
                "fields": "id,username",
                "access_token": token_data["access_token"]
            }
        )
    profile = profile_resp.json()

    user = db.query(User).filter(
        User.id == token_data.get("user_id")
    ).first()
    if not user:
        user = User(email=f"{profile.get('username')}@instagram.placeholder")
        db.add(user)
        db.commit()
        db.refresh(user)

    _upsert_connection(db, user.id, "instagram", token_data, profile.get("username", ""))
    jwt_token = create_jwt(str(user.id), user.email)
    return {
        "message": "Instagram connected successfully",
        "username": profile.get("username"),
        "access_token": jwt_token
    }

# ─────────────────────────────────────────
# TikTok OAuth
# ─────────────────────────────────────────
@router.get("/connect/tiktok")
def connect_tiktok():
    if not settings.tiktok_client_key:
        raise HTTPException(status_code=400, detail="TikTok client key not configured")
    url = (
        "https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={settings.tiktok_client_key}"
        f"&redirect_uri={settings.tiktok_redirect_uri}"
        f"&scope=user.info.basic,video.list,comment.list"
        f"&response_type=code"
    )
    return RedirectResponse(url)

@router.get("/callback/tiktok")
async def tiktok_callback(code: str, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://open.tiktokapis.com/v2/oauth/token/",
            data={
                "client_key": settings.tiktok_client_key,
                "client_secret": settings.tiktok_client_secret,
                "grant_type": "authorization_code",
                "redirect_uri": settings.tiktok_redirect_uri,
                "code": code
            }
        )
    token_data = token_resp.json()
    if "error" in token_data:
        raise HTTPException(status_code=400, detail=str(token_data))

    user = User(email=f"tiktok_{token_data.get('open_id')}@tiktok.placeholder")
    db.add(user)
    db.commit()
    db.refresh(user)

    _upsert_connection(db, user.id, "tiktok", {
        "access_token": token_data.get("access_token"),
        "refresh_token": token_data.get("refresh_token"),
        "expires_in": token_data.get("expires_in")
    }, token_data.get("open_id", ""))

    jwt_token = create_jwt(str(user.id), user.email)
    return {
        "message": "TikTok connected successfully",
        "access_token": jwt_token
    }

# ─────────────────────────────────────────
# List connections
# ─────────────────────────────────────────
@router.get("/connections")
def get_connections(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    accounts = db.query(ConnectedAccount).filter(
        ConnectedAccount.user_id == current_user.id
    ).all()
    return [
        {
            "platform": a.platform,
            "username": a.platform_username,
            "connected_at": a.created_at
        }
        for a in accounts
    ]

# ─────────────────────────────────────────
# Shared helper — save/update token in DB
# ─────────────────────────────────────────
def _upsert_connection(db, user_id, platform: str, token_data: dict, username: str):
    existing = db.query(ConnectedAccount).filter_by(
        user_id=user_id, platform=platform
    ).first()
    expires_at = None
    if token_data.get("expires_in"):
        expires_at = datetime.utcnow() + timedelta(seconds=int(token_data["expires_in"]))

    if existing:
        existing.access_token  = encrypt_token(token_data["access_token"])
        if token_data.get("refresh_token"):
            existing.refresh_token = encrypt_token(token_data["refresh_token"])
        existing.expires_at    = expires_at
        existing.updated_at    = datetime.utcnow()
    else:
        account = ConnectedAccount(
            user_id=user_id,
            platform=platform,
            access_token=encrypt_token(token_data["access_token"]),
            refresh_token=encrypt_token(token_data["refresh_token"]) if token_data.get("refresh_token") else None,
            expires_at=expires_at,
            platform_username=username
        )
        db.add(account)
    db.commit()