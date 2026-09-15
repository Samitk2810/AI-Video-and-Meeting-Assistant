from __future__ import annotations

from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Video and Meeting Assistant API",
    version="1.0.0",
    description="Transcribe, summarize, and query video or meeting recordings.",
)


class AnalyzeRequest(BaseModel):
    source: str = Field(..., min_length=1, description="YouTube URL or local file path")
    language: str = Field(default="english", pattern="^(english|hinglish)$")


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)


class AnalyzeResponse(BaseModel):
    analysis_id: str
    title: str
    summary: str
    action_items: str
    decisions: str
    questions: str


class AskResponse(BaseModel):
    analysis_id: str
    answer: str


_analyses: dict[str, object] = {}
_analyses_lock = Lock()


def _public_result(analysis_id: str, result: dict) -> AnalyzeResponse:
    return AnalyzeResponse(
        analysis_id=analysis_id,
        title=str(result.get("title", "")),
        summary=str(result.get("summary", "")),
        action_items=str(result.get("action_items", "")),
        decisions=str(result.get("decisions", "")),
        questions=str(result.get("questions", "")),
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        from main import run_pipeline

        result = run_pipeline(request.source.strip(), request.language)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    analysis_id = str(uuid4())
    with _analyses_lock:
        _analyses[analysis_id] = result["rag_chain"]

    return _public_result(analysis_id, result)


@app.post("/analyses/{analysis_id}/ask", response_model=AskResponse)
def ask(analysis_id: str, request: AskRequest) -> AskResponse:
    with _analyses_lock:
        rag_chain = _analyses.get(analysis_id)

    if rag_chain is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    try:
        from core.rag_engine import ask_question

        answer = ask_question(rag_chain, request.question.strip())
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    return AskResponse(analysis_id=analysis_id, answer=str(answer))
