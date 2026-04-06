from app.infrastructure.providers.image.openai_compatible import OpenAICompatibleImageProvider


class OpenAILiveImageProvider(OpenAICompatibleImageProvider):
    name = "openai-compatible-image"
