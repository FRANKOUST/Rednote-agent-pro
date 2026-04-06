from app.infrastructure.providers.llm.openai_compatible import OpenAICompatibleLLMProvider


class OpenAILiveLLMProvider(OpenAICompatibleLLMProvider):
    name = "openai-compatible-llm"
