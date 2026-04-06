# DEMO

## Safe demo path

1. Copy `.env.example` to `.env`
2. Keep Scrapling in fixture mode and Feishu CLI in dry-run mode
3. Run `pytest -q`
4. Start the app with `uvicorn app.main:app --reload`
5. Visit `/` and run:
   - a dry pipeline
   - a Scrapling search run
   - a Scrapling detail run
   - a Feishu sync dry-run

## Demo outcomes

- source posts persist
- analysis/topic/draft pipeline completes
- publish still requires manual approval
- sync records and diagnostics are visible
