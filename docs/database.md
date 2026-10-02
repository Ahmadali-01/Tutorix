# Database Schema

## Core Tables

- **users** — id, email, hashed_password, full_name, is_active
- **roles** — admin, teacher, student, parent, analyst
- **permissions** — permission names
- **user_roles / role_permissions** — join tables

## Course Tables

- **courses** — title, description, teacher_id
- **enrollments** — course_id, student_id
- **modules / lessons** — course structure

## AI & Content Tables

- **documents / document_chunks** — RAG source material
- **questions** — generated question bank
- **assignments / rubrics** — assessment definitions
- **submissions / evaluations / feedback** — grading

## Analytics & Prediction

- **analytics_events** — user_id, course_id, event_type, payload
- **mastery_scores** — per-topic mastery
- **predictions** — risk_level, value, explanation
- **agent_runs / prompt_versions / audit_logs** — AI observability

## Vector Collections (Qdrant)

- **course_materials** — 3072-dim Gemini embeddings
