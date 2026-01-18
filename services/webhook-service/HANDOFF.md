# Handoff: Webhook Service FastAPI Implementation

**Goal**: Build FastAPI backend that deploys GitHub repos as webhook-triggered Claude agents.

**Done**: Project structure, pyproject.toml, requirements.txt, .env.example, app/config.py, app/core/exceptions/base.py, app/core/mixins/timestamp.py

**Next**: Complete Layer 1 init files, then Layer 2 (database.py, BaseRepository), then all 6 SQLAlchemy models

**Watch out**: Follow DataGen patterns in `DataGen/fastapi/` for async SQLAlchemy; full spec is in `services/webhook-service/PLANNING.md`

---

## User Flow

```
Connect GitHub → Select Repo → Deploy Agent → Get Webhook URL → POST /hook/{slug} → Job queued → Result POSTed to callback
```

## Implementation Progress

| Layer | Status |
|-------|--------|
| 1. Core (config, exceptions, mixins) | 80% done |
| 2. Database (session, BaseRepository) | Not started |
| 3. Models (6 tables) | Not started |
| 4. Schemas | Not started |
| 5. Repositories | Not started |
| 6. Services (rate_limiter, slug_gen) | Not started |
| 7. Routers (webhooks, hooks, jobs) | Not started |
| 8. App assembly | Not started |
| 9. Alembic migrations | Not started |
| 10. Docker + Tests | Not started |

## Key Files

- **Plan**: `/Users/yu-shengkuo/.claude/plans/cozy-cooking-fairy.md`
- **Spec**: `services/webhook-service/PLANNING.md` (full DB schema, API routes, flows)
- **Reference**: `DataGen/fastapi/` (patterns to follow)
