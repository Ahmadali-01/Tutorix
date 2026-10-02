# Deployment Guide

## Local (Docker)

```bash
git clone https://github.com/YOUR_USERNAME/Tutorix.git
cd Tutorix
cp backend/.env.example backend/.env
# add GEMINI_API_KEY
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.db.seed
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Required in backend/.env:
- GEMINI_API_KEY
- DATABASE_URL
- QDRANT_URL
- REDIS_URL
- SECRET_KEY

## Production

- Build images: docker compose build
- Push to registry
- Deploy to AWS ECS / Render / Fly.io
- Use managed Postgres, Redis, Qdrant Cloud
