import json


def question_format_validity(questions: list[dict]) -> dict:
    if not questions:
        return {"score": 0.0, "valid": 0, "total": 0}

    valid = 0
    for q in questions:
        if not q.get("prompt"):
            continue
        answer = q.get("answer")
        options = q.get("options")
        if options is None:
            # short_answer / true_false must still have an answer
            if answer:
                valid += 1
        else:
            if answer and answer in options:
                valid += 1

    return {
        "score": round(valid / len(questions), 4),
        "valid": valid,
        "total": len(questions),
    }


def evaluation_score_sanity(score) -> dict:
    try:
        s = float(score)
    except (TypeError, ValueError):
        return {"score": 0.0, "in_range": False, "value": None}
    in_range = 0.0 <= s <= 100.0
    return {"score": 1.0 if in_range else 0.0, "in_range": in_range, "value": s}


def prediction_format(prediction: dict) -> dict:
    required = ["risk_level", "predicted_score", "explanation"]
    missing = [k for k in required if k not in prediction]
    return {
        "score": 1.0 if not missing else 0.0,
        "missing_fields": missing,
    }
