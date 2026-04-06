from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class PipelineRunRequest(BaseModel):
    keywords: list[str] = Field(min_length=1)
    min_likes: int = 0
    min_favorites: int = 0
    min_comments: int = 0
    auto_publish: bool = False
    dry_run: bool = True


class DraftReviewRequest(BaseModel):
    review_notes: str = ""


class CollectorRunRequest(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    note_ids: list[str] = Field(default_factory=list)
    dry_run: bool = True
    max_results: int = 10

    @model_validator(mode="after")
    def ensure_lookup_input(self):
        if not self.keywords and not self.note_ids:
            raise ValueError("keywords or note_ids must be provided")
        return self


class SyncRunRequest(BaseModel):
    entity_type: str
    payload: dict[str, Any]
    dry_run: bool = True


class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: int | str | None = None
    method: str
    params: dict[str, Any] | None = None
