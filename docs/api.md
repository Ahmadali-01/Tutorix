# API Reference

Base URL: /api/v1

## Auth
- POST /auth/register
- POST /auth/login
- GET /auth/me

## Courses
- POST /courses
- GET /courses
- POST /courses/enroll

## RAG
- POST /rag/upload
- POST /rag/query

## Questions
- POST /questions/generate

## Assignments
- POST /assignments
- POST /assignments/submissions
- POST /assignments/submissions/{id}/evaluate

## Agents
- POST /agents/curriculum/generate
- POST /agents/tools/chat

## Analytics
- GET /analytics/course/{id}
- GET /analytics/student/{id}
- POST /analytics/predict/student/{id}
- POST /analytics/events/log

## Evaluation
- POST /eval/rag
- POST /eval/questions
- POST /eval/evaluation
- POST /eval/prediction

Full interactive docs at /docs (Swagger) and /redoc.
