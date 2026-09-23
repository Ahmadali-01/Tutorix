from app.eval.domain_metrics import (
    evaluation_score_sanity,
    prediction_format,
    question_format_validity,
)
from app.eval.ragas_metrics import answer_relevancy, context_precision, faithfulness
from app.rag.generator import generate_answer
from app.rag.retriever import hybrid_search


def evaluate_rag(query: str, course_id: str | None = None, top_k: int = 3) -> dict:
    chunks = hybrid_search(query, course_id=course_id, top_k=top_k)
    context = "\n\n".join(c["text"] for c in chunks) if chunks else ""
    answer = generate_answer(query, chunks)

    faith = faithfulness(context, answer) if chunks else {"score": 0.0, "reason": "no context"}
    relev = answer_relevancy(query, answer)
    prec = context_precision(query, [c["text"] for c in chunks]) if chunks else {"score": 0.0, "reason": "no chunks"}

    scores = [faith.get("score", 0.0), relev.get("score", 0.0), prec.get("score", 0.0)]
    overall = round(sum(scores) / len(scores), 4) if scores else 0.0

    return {
        "query": query,
        "answer": answer,
        "num_chunks": len(chunks),
        "metrics": {
            "faithfulness": faith,
            "answer_relevancy": relev,
            "context_precision": prec,
        },
        "overall_score": overall,
    }


def evaluate_questions(questions: list[dict]) -> dict:
    return question_format_validity(questions)


def evaluate_evaluation(score) -> dict:
    return evaluation_score_sanity(score)


def evaluate_prediction(prediction: dict) -> dict:
    return prediction_format(prediction)
