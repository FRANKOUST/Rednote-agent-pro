from __future__ import annotations

from pydantic import BaseModel, Field


class AnalysisResultSchema(BaseModel):
    summary: str = Field(min_length=1)
    top_keywords: list[str] = Field(default_factory=list)
    top_tags: list[str] = Field(default_factory=list)
    title_patterns: list[str] = Field(default_factory=list)
    audience_insights: list[str] = Field(default_factory=list)


class TopicSuggestionItemSchema(BaseModel):
    title: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    angle: str = Field(min_length=1)


class TopicSuggestionListSchema(BaseModel):
    topics: list[TopicSuggestionItemSchema] = Field(min_length=1)


class DraftResultSchema(BaseModel):
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)
    tags: list[str] = Field(min_length=1)
    cta: str = Field(min_length=1)
    image_prompt: str = Field(min_length=1)
    content_type: str = Field(min_length=1)
