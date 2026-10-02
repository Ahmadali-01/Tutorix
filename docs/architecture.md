# Architecture

Tutorix uses a layered architecture: Next.js frontend talks to a FastAPI backend, which orchestrates LLM agents, RAG retrieval, analytics, prediction, and evaluation services. Data lives in PostgreSQL (relational), Qdrant (vectors), and Redis (cache).

```
Next.js Frontend
      |
      v
FastAPI Backend
  |-- Auth + RBAC (JWT)
  |-- LangGraph Agents --> Gemini LLM
  |-- RAG Service --> Gemini Embeddings --> Qdrant
  |-- Analytics Service --> PostgreSQL
  |-- Prediction Service --> PostgreSQL
  |-- Evaluation Service (RAGAS) --> Gemini LLM
  |-- Function Calling Tools (calculator, time, search, stats)
```

## Components

| Layer | Tech |
|---|---|
| Frontend | Next.js 16, TypeScript, Tailwind |
| Backend | FastAPI, SQLAlchemy, Alembic |
| LLM | Google Gemini |
| Agents | LangGraph |
| Vector DB | Qdrant |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Containers | Docker Compose |
