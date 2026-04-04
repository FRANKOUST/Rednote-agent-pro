## 1. Application bootstrap

- [ ] 1.1 Maintain a single `create_app()` bootstrap path that initializes settings, persistence, and interface routes.
- [ ] 1.2 Keep local runtime defaults documented and aligned with `.env.example`.

## 2. Package boundaries

- [ ] 2.1 Keep `core`, `domain`, `db`, `application`, `infrastructure`, and `interfaces` responsibilities separated.
- [ ] 2.2 Keep provider lookups centralized through the registry layer.

## 3. Verification

- [ ] 3.1 Keep startup and interface tests green for REST, MCP, and Web entrypoints.
- [ ] 3.2 Revalidate the change whenever new modules are added that could blur package boundaries.
