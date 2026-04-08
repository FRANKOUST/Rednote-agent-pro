from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.models import PIPELINE_STAGES


class PipelineRunRequest(BaseModel):
    keywords: list[str] = Field(min_length=1)
    topic_words: list[str] = Field(default_factory=list)
    min_likes: int = 0
    min_favorites: int = 0
    min_comments: int = 0
    auto_publish: bool = False
    dry_run: bool = True
    run_mode: Literal["full", "step"] = "full"


class StageRunRequest(BaseModel):
    dry_run: bool = True
    overrides: dict[str, Any] = Field(default_factory=dict)


class DraftReviewRequest(BaseModel):
    review_notes: str = ""


class PublishSendRequest(BaseModel):
    dry_run: bool = True


class SyncActionRequest(BaseModel):
    dry_run: bool = True


class CollectorRunRequest(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    note_ids: list[str] = Field(default_factory=list)
    topic_words: list[str] = Field(default_factory=list)
    dry_run: bool = True
    max_results: int = 10
    collection_type: str = "search"
    min_likes: int = 0
    min_favorites: int = 0
    min_comments: int = 0

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


class PipelineStageName(BaseModel):
    stage: str

    @model_validator(mode="after")
    def validate_stage(self):
        if self.stage not in PIPELINE_STAGES:
            raise ValueError(f"Unknown stage: {self.stage}")
        return self
