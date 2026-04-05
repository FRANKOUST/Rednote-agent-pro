import json
from pathlib import Path


def test_sample_eval_fixture_exists() -> None:
    payload = json.loads(Path("fixtures/real_like_samples.json").read_text(encoding="utf-8"))
    assert len(payload) >= 2
