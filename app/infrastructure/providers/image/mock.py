from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.core.config import get_settings
from app.domain.models import DraftPayload, ImagePayload


class MockImageProvider:
    name = "mock-image"

    def generate(self, draft: DraftPayload) -> ImagePayload:
        settings = get_settings()
        filename = f"{uuid4().hex}.svg"
        path = Path(settings.media_dir) / filename
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024">
<rect width="100%" height="100%" fill="#fff7f1"/>
<rect x="72" y="72" width="880" height="880" rx="48" fill="#ffffff" stroke="#ff6b6b" stroke-width="8"/>
<text x="120" y="220" fill="#111111" font-size="48" font-family="Arial">{draft.title}</text>
<text x="120" y="320" fill="#ff6b6b" font-size="28" font-family="Arial">Mock gpt-image-1 poster</text>
</svg>"""
        path.write_text(svg, encoding="utf-8")
        return ImagePayload(path=str(path), prompt=draft.image_prompt, provider=self.name)
