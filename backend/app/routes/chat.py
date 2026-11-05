from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request
from openai import APIError as OpenAIAPIError

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import RAGService

logger = logging.getLogger("temple_heritage.chat")
router = APIRouter()


def get_rag_service(request: Request) -> RAGService:
    service = request.app.state.rag_service
    if service is None:
        raise HTTPException(status_code=503, detail="RAG service is not initialized")
    return service


@router.post("/chat", response_model=ChatResponse)
def chat(request: Request, payload: ChatRequest) -> ChatResponse:
    rag_service = get_rag_service(request)
    try:
        result = rag_service.answer_question(
            question=payload.question,
            language=payload.language,
            temple_id=payload.temple_id,
            history=payload.history,
        )
    except OpenAIAPIError:
        logger.exception("Upstream LLM request failed")
        raise HTTPException(status_code=502, detail="Upstream LLM service temporarily unavailable")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error while processing chat request")
        raise HTTPException(status_code=500, detail="Internal server error while processing the request")
    return ChatResponse(
        answer=result.answer,
        citations=result.citations,
        language=result.language,
        insufficient_evidence=result.insufficient_evidence,
        generation_disabled=result.generation_disabled,
        context_temple_id=getattr(result, "context_temple_id", None),
    )
