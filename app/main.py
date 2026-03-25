from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth import routes as auth_routes
from app.models.database import create_tables

app = FastAPI(
    title="CreatorPulse API",
    description="AI-powered social media digest for creators",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    create_tables()

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "CreatorPulse"}