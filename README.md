# CreatorPulse 🎯

> AI-powered social media digest for creators and celebrities.
> Instead of reading thousands of comments every day — get one smart daily summary.

---

## What is CreatorPulse?

If you are a creator, celebrity, or influencer with thousands of followers,
you know it is impossible to read every comment, DM, and mention you receive every day.

**CreatorPulse solves this.**

You connect your social media accounts once.
Every day, our AI reads all your comments and messages,
and sends you one clean summary — what your fans are saying,
what questions they are asking, and how they are feeling about your content.

---

## How it works

1. **Connect your accounts** — Instagram, YouTube, Gmail, TikTok
2. **We fetch your comments and messages** every day automatically
3. **AI reads everything** and writes you a short summary
4. **You get a daily digest** by email — what matters, nothing that doesn't

---

## Features

- Daily AI-generated digest of all your comments across platforms
- Sentiment analysis — are fans happy, neutral, or upset today?
- Topic detection — what are fans talking about most?
- Smart reply suggestions — AI drafts responses to top comments
- Superfan detection — identifies your most loyal followers
- Crisis alerts — notifies you if negative comments spike suddenly
- Works across Instagram, YouTube, Gmail, TikTok, Facebook

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| Cache & Queue | Redis + Celery |
| AI Summarization | LangChain + GPT-4o |
| Auth | OAuth 2.0 per platform |
| Deployment | Docker + Railway |

---

## How to run it yourself

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/creatorpulse.git
cd creatorpulse
```

### 2. Set up your environment
```bash
cp .env.example .env
```

Open `.env` and fill in your own API keys:

| Key | Where to get it |
|---|---|
| `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` | https://console.cloud.google.com |
| `META_CLIENT_ID` + `META_CLIENT_SECRET` | https://developers.facebook.com |
| `TIKTOK_CLIENT_KEY` + `TIKTOK_CLIENT_SECRET` | https://developers.tiktok.com |
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| `SENDGRID_API_KEY` | https://app.sendgrid.com |

### 3. Run with Docker
```bash
docker compose up --build
```

### 4. Open the API
```
http://localhost:8000/docs
```

You will see the full interactive API documentation where you can test every endpoint.

---

## API Endpoints

| Method | Endpoint | What it does |
|---|---|---|
| POST | `/auth/register` | Create a new account |
| POST | `/auth/login` | Login and get your token |
| GET | `/auth/connect/google` | Connect YouTube + Gmail |
| GET | `/auth/connect/instagram` | Connect Instagram |
| GET | `/auth/connect/tiktok` | Connect TikTok |
| GET | `/auth/connections` | See your connected accounts |
| GET | `/health` | Check if the API is running |

---

## Project Structure
```
creatorpulse/
├── app/
│   ├── auth/          # OAuth login for each platform
│   ├── platforms/     # Data fetchers (YouTube, Gmail, Instagram, TikTok)
│   ├── ai/            # AI summarization with LangChain + GPT-4o
│   ├── jobs/          # Celery background tasks (nightly digest)
│   ├── models/        # Database models and schemas
│   ├── core/          # App config and settings
│   └── main.py        # FastAPI app entry point
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example       # Copy this to .env and fill in your keys
└── README.md
```

---

## Roadmap

- [x] Project scaffold and Docker setup
- [x] Database models (users, connected accounts, digests)
- [x] OAuth 2.0 for Google (YouTube + Gmail)
- [x] OAuth 2.0 for Instagram and TikTok
- [ ] YouTube comment fetcher
- [ ] Gmail inbox fetcher
- [ ] Instagram comment fetcher
- [ ] AI summarization chain (LangChain + GPT-4o)
- [ ] Daily digest email (SendGrid)
- [ ] React frontend dashboard
- [ ] Deploy to Railway

---

## Contributing

Pull requests are welcome. If you want to add a new platform integration
or improve the AI summarization, feel free to open an issue first to discuss.

---

## License

MIT — free to use, modify, and distribute.

---

Built by [Suresh](https://github.com/suresh15kk)