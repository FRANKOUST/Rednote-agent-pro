from __future__ import annotations

import json
from dataclasses import asdict
from typing import TypeVar

import httpx

from app.core.config import get_settings
from app.domain.model_schemas import AnalysisResultSchema, DraftResultSchema, ImagePlanSchema, TopicSuggestionListSchema
from app.domain.models import AnalysisPayload, DraftPayload, ImagePlanPayload, SourcePostPayload, TopicPayload
from app.infrastructure.providers.llm.openai_safe_stub import OpenAICompatibleSafeLLMStubProvider
from app.infrastructure.providers.llm.prompt_templates import build_prompt_request, get_prompt_template

SchemaT = TypeVar("SchemaT")


class OpenAICompatibleLLMProvider:
    name = "openai-compatible-llm"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.safe = OpenAICompatibleSafeLLMStubProvider()
        self.last_run_metadata: dict = {}

    def analyze(self, posts: list[SourcePostPayload]) -> AnalysisPayload:
        prompt = build_prompt_request(
            "analyze",
            posts=[
                {
                    "title": post.title,
                    "content": post.content,
                    "tags": post.tags,
                    "likes": post.likes,
                    "favorites": post.favorites,
                    "comments": post.comments,
                    "published_at": post.published_at,
                    "content_type": post.content_type,
                }
                for post in posts
            ],
            request_context={"post_count": len(posts)},
        )
        try:
            data = self._invoke_schema("analyze", prompt, AnalysisResultSchema)
            return AnalysisPayload(**data.model_dump())
        except Exception as exc:
            self.last_run_metadata = {"stage": "analyze", "mode": "fallback", "error": str(exc)}
            return self.safe.analyze(posts)

    def suggest_topics(self, analysis: AnalysisPayload) -> list[TopicPayload]:
        prompt = build_prompt_request("topic", analysis=asdict(analysis), request_context={})
        try:
            data = self._invoke_schema("topic", prompt, TopicSuggestionListSchema)
            return [TopicPayload(**item.model_dump(), angle=item.title) for item in data.topics]
        except Exception as exc:
            self.last_run_metadata = {"stage": "topic", "mode": "fallback", "error": str(exc)}
            return self.safe.suggest_topics(analysis)

    def generate_draft(self, topic: TopicPayload, analysis: AnalysisPayload) -> DraftPayload:
        prompt = build_prompt_request("draft", topic=asdict(topic), analysis=asdict(analysis), request_context={})
        try:
            data = self._invoke_schema("draft", prompt, DraftResultSchema)
            return DraftPayload(**data.model_dump())
        except Exception as exc:
            self.last_run_metadata = {"stage": "draft", "mode": "fallback", "error": str(exc)}
            return self.safe.generate_draft(topic, analysis)

    def plan_image(self, draft: DraftPayload, analysis: AnalysisPayload | None = None) -> ImagePlanPayload:
        prompt = build_prompt_request("image", draft=asdict(draft), analysis=asdict(analysis) if analysis else {}, request_context={})
        try:
            data = self._invoke_schema("image", prompt, ImagePlanSchema)
            return ImagePlanPayload(**data.model_dump())
        except Exception as exc:
            self.last_run_metadata = {"stage": "image", "mode": "fallback", "error": str(exc)}
            return self.safe.plan_image(draft, analysis)

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
        template = get_prompt_template(stage)
        self.last_run_metadata = {
            "stage": stage,
            "mode": "live",
            "template_id": template.template_id,
            "template_version": template.version,
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
