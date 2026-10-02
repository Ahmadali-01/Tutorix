# Tutorix — Final Presentation

## Slide 1 — Title
Tutorix: AI Education Intelligence Platform
Ahmad Ali

## Slide 2 — Problem
- One-size-fits-all education
- Teachers spend hours grading and planning
- Students lack personalized tutoring
- Schools cannot predict student success early

## Slide 3 — Solution
An AI platform that personalizes learning, generates questions, grades assignments, plans curricula, tracks analytics, and predicts student outcomes.

## Slide 4 — Core Modules
1. Personalized Learning (RAG)
2. Question Generation
3. Assignment Evaluation
4. Curriculum Planning
5. Learning Analytics
6. Student Prediction

## Slide 5 — Architecture
Next.js -> FastAPI -> LangGraph Agents -> Gemini LLM
                     -> RAG -> Gemini Embeddings -> Qdrant
                     -> PostgreSQL + Redis

## Slide 6 — Tech Stack
Frontend: Next.js, TypeScript, Tailwind
Backend: FastAPI, SQLAlchemy, Alembic
LLM: Google Gemini
Agents: LangGraph
Vector DB: Qdrant | DB: PostgreSQL | Cache: Redis

## Slide 7 — AI Techniques
- Retrieval-Augmented Generation (RAG)
- Hybrid Search (semantic + keyword)
- Prompt Engineering
- Multi-Agent Workflows (LangGraph)
- Function Calling
- Hybrid ML + LLM prediction
- RAGAS-style evaluation

## Slide 8 — Demo Highlights
- Ask a question -> grounded answer + sources
- Generate MCQs on any topic
- 4-agent curriculum in 20 seconds
- AI grades assignments with feedback
- Live analytics dashboard
- Student risk prediction with explanation

## Slide 9 — Evaluation Results
RAG quality on course material:
Faithfulness: 1.0
Answer Relevancy: 1.0
Context Precision: 1.0
Overall: 1.0

## Slide 10 — Security
- JWT authentication
- Role-Based Access Control (Admin, Teacher, Student, Parent, Analyst)
- Audited LLM calls and events

## Slide 11 — Deployment
- Docker Compose for local dev
- Services: backend, frontend, postgres, redis, qdrant
- Ready for AWS ECS / Render / Fly.io

## Slide 12 — Future Work
- Voice-based tutoring
- Adaptive learning paths
- Mobile app
- LMS integrations (Moodle, Canvas)

## Thank You
Questions?
