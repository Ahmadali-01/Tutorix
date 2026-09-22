import ast
import operator as op
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.analytics import AnalyticsEvent
from app.models.assignment import Evaluation, Question, Submission

# -------- Safe calculator --------

_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
}


def _eval_node(node):
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("Unsupported expression")


def calculator(expression: str) -> str:
    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval_node(tree.body)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"


# -------- Current time --------

def current_time() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


# -------- Search questions in DB --------

def search_questions(db: Session, keyword: str, limit: int = 5) -> list:
    rows = (
        db.query(Question)
        .filter(Question.prompt.ilike(f"%{keyword}%"))
        .limit(limit)
        .all()
    )
    return [
        {"id": str(r.id), "prompt": r.prompt, "difficulty": r.difficulty}
        for r in rows
    ]


# -------- Get student stats --------

def get_student_stats(db: Session, student_id: str) -> dict:
    events = db.query(AnalyticsEvent).filter(AnalyticsEvent.user_id == student_id).count()
    submissions = db.query(Submission).filter(Submission.student_id == student_id).all()
    submission_ids = [s.id for s in submissions]
    scores = []
    if submission_ids:
        evals = db.query(Evaluation).filter(Evaluation.submission_id.in_(submission_ids)).all()
        scores = [float(e.score) for e in evals if e.score is not None]
    avg_score = round(sum(scores) / len(scores), 2) if scores else None
    return {
        "student_id": student_id,
        "total_events": events,
        "submissions": len(submissions),
        "avg_score": avg_score,
    }


# -------- Tool dispatcher --------

TOOL_NAMES = ["calculator", "current_time", "search_questions", "get_student_stats"]


def call_tool(name: str, args: dict, db: Session) -> str:
    import json
    try:
        if name == "calculator":
            return calculator(args.get("expression", ""))
        if name == "current_time":
            return current_time()
        if name == "search_questions":
            rows = search_questions(db, args.get("keyword", ""), args.get("limit", 5))
            return json.dumps(rows)
        if name == "get_student_stats":
            return json.dumps(get_student_stats(db, args.get("student_id", "")))
        return f"Unknown tool: {name}"
    except Exception as e:
        return f"Tool error: {e}"
