from __future__ import annotations

import json
from dataclasses import asdict
from typing import TypeVar

import httpx

from app.core.config import get_settings
from app.domain.model_schemas import AnalysisResultSchema, DraftResultSchema, TopicSuggestionListSchema
from app.domain.models import AnalysisPayload, DraftPayload, SourcePostPayload, TopicPayload
from app.infrastructure.providers.llm.openai_safe_stub import OpenAICompatibleSafeLLMStubProvider
from app.infrastructure.providers.llm.prompt_templates import build_analysis_prompt, build_draft_prompt, build_topic_prompt

SchemaT = TypeVar("SchemaT")


class OpenAICompatibleLLMProvider:
    name = "openai-compatible-llm"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.safe = OpenAICompatibleSafeLLMStubProvider()
        self.last_run_metadata: dict = {}

    def analyze(self, posts: list[SourcePostPayload]) -> AnalysisPayload:
        prompt = build_analysis_prompt(
            [
                {
                    "title": post.title,
                    "content": post.content,
                    "tags": post.tags,
                    "likes": post.likes,
                    "favorites": post.favorites,
                    "comments": post.comments,
                }
                for post in posts
            ]
        )
        try:
            data = self._invoke_schema("analyze", prompt, AnalysisResultSchema)
            return AnalysisPayload(
                summary=data.summary,
                top_keywords=data.top_keywords,
                top_tags=data.top_tags,
                title_patterns=data.title_patterns,
                audience_insights=data.audience_insights,
            )
        except Exception as exc:
            self.last_run_metadata = {"stage": "analyze", "mode": "fallback", "error": str(exc)}
            return self.safe.analyze(posts)

    def suggest_topics(self, analysis: AnalysisPayload) -> list[TopicPayload]:
        prompt = build_topic_prompt(asdict(analysis))
        try:
            data = self._invoke_schema("topic", prompt, TopicSuggestionListSchema)
            return [TopicPayload(title=item.title, rationale=item.rationale, angle=item.angle) for item in data.topics]
        except Exception as exc:
            self.last_run_metadata = {"stage": "topic", "mode": "fallback", "error": str(exc)}
            return self.safe.suggest_topics(analysis)

    def generate_draft(self, topic: TopicPayload, analysis: AnalysisPayload) -> DraftPayload:
        prompt = build_draft_prompt(asdict(topic), asdict(analysis))
        try:
            data = self._invoke_schema("draft", prompt, DraftResultSchema)
            return DraftPayload(
                title=data.title,
                body=data.body,
                tags=data.tags,
                cta=data.cta,
                image_prompt=data.image_prompt,
                content_type=data.content_type,
            )
        except Exception as exc:
            self.last_run_metadata = {"stage": "draft", "mode": "fallback", "error": str(exc)}
            return self.safe.generate_draft(topic, analysis)

    def health(self) -> dict:
        has_credentials = bool(self.settings.resolved_model_api_key and self.settings.resolved_model_name)
        if not self.settings.enable_real_model_provider:
            return {"status": "ready", "reason": "safe model mode active"}
        if has_credentials:
            return {"status": "ready", "reason": "openai-compatible credentials configured"}
        return {"status": "degraded", "reason": "missing model api key or model name"}

    def diagnostics(self) -> dict:
        return {
            "provider_type": "openai_compatible",
            "base_url": self.settings.resolved_model_base_url,
            "model_name": self.settings.resolved_model_name,
            "temperature": self.settings.model_temperature,
            "last_run": self.last_run_metadata,
        }

    def _invoke_schema(self, stage: str, prompt: dict, schema: type[SchemaT]) -> SchemaT:
        payload = self._chat_json(stage, prompt)
        validated = schema.model_validate(payload)
        self.last_run_metadata = {
            "stage": stage,
            "mode": "live",
            "model": self.settings.resolved_model_name,
            "base_url": self.settings.resolved_model_base_url,
        }
        return validated

    def _chat_json(self, stage: str, payload: dict) -> dict:
        if not self.settings.enable_real_model_provider:
            raise RuntimeError("real model provider disabled")
        if not self.settings.resolved_model_api_key:
            raise RuntimeError("missing model api key")

        headers = {"Authorization": f"Bearer {self.settings.resolved_model_api_key}"}
        body = {
            "model": self.settings.resolved_model_name,
            "temperature": self.settings.model_temperature,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "You are a Xiaohongshu content system. Return strict JSON only."},
                {"role": "user", "content": json.dumps({"stage": stage, "payload": payload}, ensure_ascii=False)},
            ],
        }
        timeout = httpx.Timeout(self.settings.model_timeout_seconds)
        last_error: Exception | None = None
        for _attempt in range(1, self.settings.model_max_retries + 2):
            try:
                with httpx.Client(timeout=timeout) as client:
                    response = client.post(
                        f"{self.settings.resolved_model_base_url}/chat/completions",
                        headers=headers,
                        json=body,
                    )
                    response.raise_for_status()
                    content = response.json()["choices"][0]["message"]["content"]
                return self._parse_content_as_json(content)
            except Exception as exc:
                last_error = exc
        raise RuntimeError(f"model request failed: {last_error}")

    @staticmethod
    def _parse_content_as_json(content: str) -> dict:
        text = (content or "").strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].strip()
        return json.loads(text)
