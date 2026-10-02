# Tutorix

**Your AI Education Intelligence Platform**

Tutorix is an AI-powered learning platform that personalizes education, generates questions, evaluates assignments, plans curricula, tracks analytics, and predicts student outcomes — powered by LLMs, RAG, and multi-agent workflows.

## Features

| Module | Description |
|---|---|
| Personalized Learning | RAG-based AI tutor grounded in course materials |
| Question Generation | LLM generates MCQs, short answers, and true/false with explanations |
| Assignment Evaluation | AI grades submissions against rubrics with detailed feedback |
| Curriculum Planning | 4-agent LangGraph workflow for modules, objectives, lessons, assessments |
| Learning Analytics | Real-time event tracking and dashboards |
| Student Prediction | Hybrid rule-based + LLM risk scoring |
| Agent Tools | Function calling for calculator, time, question search, student stats |
| Evaluation Framework | RAGAS-style metrics for RAG quality |

## Tech Stack

- **Frontend:** Next.js 16, TypeScript, Tailwind CSS
- **Backend:** FastAPI, SQLAlchemy, Alembic, Pydantic
- **LLM:** Google Gemini
- **Agents:** LangGraph
- **Vector DB:** Qdrant
- **Database:** PostgreSQL 16
- **Cache:** Redis 7
- **Auth:** JWT + RBAC
- **Containers:** Docker + docker-compose

## Architecture
