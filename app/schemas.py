from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PipelineRunRequest(BaseModel):
    keywords: list[str] = Field(min_length=1)
    min_likes: int = 0
    min_favorites: int = 0
    min_comments: int = 0
    auto_publish: bool = False


class DraftReviewRequest(BaseModel):
    review_notes: str = ""


class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: int | str | None = None
    method: str
    params: dict[str, Any] | None = None
