ANALYSIS_PROMPT_VERSION = "analysis.v1"
TOPIC_PROMPT_VERSION = "topics.v1"
DRAFT_PROMPT_VERSION = "draft.v1"


def build_analysis_prompt(posts: list[dict]) -> dict:
    return {"version": ANALYSIS_PROMPT_VERSION, "task": "analyze", "posts": posts}


def build_topic_prompt(analysis: dict) -> dict:
    return {"version": TOPIC_PROMPT_VERSION, "task": "topics", "analysis": analysis}


def build_draft_prompt(topic: dict, analysis: dict) -> dict:
    return {"version": DRAFT_PROMPT_VERSION, "task": "draft", "topic": topic, "analysis": analysis}
