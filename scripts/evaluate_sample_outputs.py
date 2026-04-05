from __future__ import annotations

import json
from pathlib import Path

from app.infrastructure.providers.llm.mock import MockLanguageModelProvider


def main() -> int:
    sample_path = Path("fixtures/real_like_samples.json")
    samples = json.loads(sample_path.read_text(encoding="utf-8"))
    provider = MockLanguageModelProvider()
    posts = []
    for item in samples:
        posts.append(
            type(
                "Post",
                (),
                {
                    "title": item["title"],
                    "content": item["content"],
                    "tags": item["tags"],
                    "likes": item["likes"],
                    "favorites": item["favorites"],
                    "comments": item["comments"],
                },
            )()
        )
    analysis = provider.analyze(posts)
    report = {
        "summary": analysis.summary,
        "top_keywords": analysis.top_keywords,
        "top_tags": analysis.top_tags,
        "title_patterns": analysis.title_patterns,
        "audience_insights": analysis.audience_insights,
    }
    out = Path("fixtures/sample_eval_report.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
