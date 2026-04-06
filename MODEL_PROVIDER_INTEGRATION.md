# MODEL PROVIDER Integration

## Providers

- `openai_compatible`
- `custom_model_router`
- `mock`

## Stages covered

- analyze
- topic suggestion
- draft generation
- image generation can optionally use the same OpenAI-compatible configuration family

## Guardrails

- every live response is parsed as JSON and validated with pydantic schemas
- invalid or unavailable live output falls back to the safe stub/mock path
- base URL, API key, model, timeout, retries, and temperature are env-driven

## Key envs

- `XHS_DEFAULT_MODEL_PROVIDER`
- `XHS_MODEL_API_KEY`
- `XHS_MODEL_BASE_URL`
- `XHS_MODEL_NAME`
- `XHS_MODEL_TIMEOUT_SECONDS`
- `XHS_MODEL_MAX_RETRIES`
- `XHS_MODEL_TEMPERATURE`

## Real validation blocker

Provide one working OpenAI-compatible endpoint and key to verify the live path end-to-end.
