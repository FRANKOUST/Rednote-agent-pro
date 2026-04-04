from __future__ import annotations

import json

import httpx

from app.core.config import get_settings
from app.domain.models import AnalysisPayload, DraftPayload, SourcePostPayload, TopicPayload
from app.infrastructure.providers.llm.openai_safe_stub import OpenAISafeLLMStubProvider


class OpenAILiveLLMProvider:
    name = "openai-live-llm"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.safe = OpenAISafeLLMStubProvider()

    def analyze(self, posts: list[SourcePostPayload]) -> AnalysisPayload:
        prompt = {
            "task": "analyze",
            "posts": [
                {"title": post.title, "content": post.content, "tags": post.tags, "likes": post.likes, "favorites": post.favorites, "comments": post.comments}
                for post in posts
            ],
        }
        try:
            data = self._chat_json(prompt)
            return AnalysisPayload(
                summary=data["summary"],
                top_keywords=data["top_keywords"],
                top_tags=data["top_tags"],
                title_patterns=data["title_patterns"],
                audience_insights=data["audience_insights"],
            )
        except Exception:
            return self.safe.analyze(posts)

    def suggest_topics(self, analysis: AnalysisPayload) -> list[TopicPayload]:
        prompt = {"task": "topics", "analysis": analysis.__dict__}
        try:
            data = self._chat_json(prompt)
            return [TopicPayload(title=item["title"], rationale=item["rationale"], angle=item["angle"]) for item in data["topics"]]
        except Exception:
            return self.safe.suggest_topics(analysis)

    def generate_draft(self, topic: TopicPayload, analysis: AnalysisPayload) -> DraftPayload:
        prompt = {"task": "draft", "topic": topic.__dict__, "analysis": analysis.__dict__}
        try:
            data = self._chat_json(prompt)
            return DraftPayload(
                title=data["title"],
                body=data["body"],
                tags=data["tags"],
                cta=data["cta"],
                image_prompt=data["image_prompt"],
                content_type=data["content_type"],
            )
        except Exception:
            return self.safe.generate_draft(topic, analysis)

    def _chat_json(self, payload: dict) -> dict:
        headers = {"Authorization": f"Bearer {self.settings.openai_api_key}"}
        body = {
            "model": self.settings.openai_model_name,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "You are a Xiaohongshu content system. Return strict JSON only."},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
        }
        with httpx.Client(timeout=30.0) as client:
            response = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)
