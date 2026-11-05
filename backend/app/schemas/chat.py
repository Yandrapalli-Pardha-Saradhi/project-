from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.config import SUPPORTED_LANGUAGES


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1000)
    context_temple_id: Optional[str] = Field(default=None, max_length=100)

    @field_validator("content")
    @classmethod
    def _strip_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("conversation message must not be empty")
        return value


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1, max_length=1000,
        description="User question about Indian temples or heritage sites",
    )
    language: str = Field(
        default="en",
        description="Answer language: en (English), te (Telugu), ta (Tamil), or hi (Hindi)",
    )
    temple_id: Optional[str] = Field(
        default=None, max_length=100, description="Optional temple identifier to scope retrieval"
    )
    history: List[ConversationMessage] = Field(
        default_factory=list,
        max_length=8,
        description="Up to four completed user/assistant turns for this conversation",
    )

    @field_validator("question")
    @classmethod
    def _strip_question(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("question must not be empty")
        return v

    @field_validator("language")
    @classmethod
    def _validate_language(cls, v: str) -> str:
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{v}'. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
            )
        return v

    @field_validator("history")
    @classmethod
    def _validate_history(cls, messages: List[ConversationMessage]) -> List[ConversationMessage]:
        if len(messages) % 2:
            raise ValueError("history must contain complete user/assistant turns")
        for index, message in enumerate(messages):
            expected = "user" if index % 2 == 0 else "assistant"
            if message.role != expected:
                raise ValueError("history must alternate user and assistant messages")
        return messages


class Citation(BaseModel):
    source_id: str
    source_title: str
    source_url: str
    publisher: Optional[str] = None
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    language: str
    insufficient_evidence: bool
    generation_disabled: bool
    context_temple_id: Optional[str] = None
