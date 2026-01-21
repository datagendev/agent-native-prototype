---
title: "Webhook Registration Service"
description: "Backend service for deploying GitHub repos as webhook-triggered Claude agents"
category: "architecture"
tags: ["webhook", "github", "claude-sdk", "fastapi", "backend"]
created: 2026-01-15
updated: 2026-01-15
status: "draft"
priority: "high"
---

# Webhook Registration Service - Planning Document

## Overview

A backend service that allows users to:
1. Connect their GitHub account
2. Select a repository containing Claude agents (in `.Claude/agents/`)
3. Deploy individual agents as webhook endpoints
4. Trigger agents via HTTP POST to the webhook URL
5. Receive results via callback URL

## User Journey

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              User Journey                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. CONNECT          2. SELECT           3. DEPLOY          4. USE          │
│  ───────────         ─────────           ─────────          ─────           │
│                                                                              │
│  ┌──────────┐       ┌──────────┐       ┌──────────┐       ┌──────────┐     │
│  │  GitHub  │       │  Pick    │       │  Deploy  │       │  POST to │     │
│  │  OAuth   │──────▶│  Repo    │──────▶│  Agent   │──────▶│  Webhook │     │
│  │  Login   │       │          │       │          │       │  URL     │     │
│  └──────────┘       └──────────┘       └──────────┘       └──────────┘     │
│       │                  │                  │                  │            │
│       ▼                  ▼                  ▼                  ▼            │
│  User authed        Repo cloned        Webhook URL        Agent runs,      │
│  with GitHub        to R2 storage,     generated:         result POSTed    │
│                     agents discovered  /hook/{slug}       to callback      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Webhook URL format | `https://app.fly.dev/hook/{random_slug}` | Opaque, not guessable |
| Signature verification | None | Simplicity; security via obscurity of slug |
| Result delivery | Callback URL | Async-friendly, no polling needed |
| Rate limiting | Per webhook + per user | Prevent abuse at both levels |
| Repo storage | Full git clone to R2 | Enables future features (branching, diffs) |
| Sync strategy | Manual sync to latest main | User controls when to update |

## Tech Stack

| Component | Service | Why |
|-----------|---------|-----|
| **Database** | Neon (managed Postgres) | Serverless, scales to zero, branching |
| **Hosting** | Fly.io | Easy deployment, global edge, good for Python |
| **Job Queue** | Upstash Redis | Serverless Redis, pay-per-request |
| **Repo Storage** | Cloudflare R2 | S3-compatible, no egress fees |
| **Auth** | GitHub OAuth App | Simple, users already have GitHub |
| **Agent Runtime** | Claude Agent SDK | Official SDK for running agents |

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              System Architecture                             │
└─────────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────────┐
                           │   GitHub OAuth  │
                           └────────┬────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
┌─────────────────────────────────────┐   ┌─────────────────────┐
│         FastAPI Application         │   │   GitHub API        │
│                                     │   │   (repo list,       │
│  ┌───────┐ ┌───────┐ ┌───────────┐ │   │    clone access)    │
│  │ Auth  │ │ Repos │ │  Agents   │ │   └─────────────────────┘
│  │Router │ │Router │ │  Router   │ │
│  └───────┘ └───────┘ └───────────┘ │
│                                     │
│  ┌───────┐ ┌───────┐ ┌───────────┐ │
│  │Webhook│ │ Hooks │ │   Jobs    │ │
│  │Router │ │Router │ │  Router   │ │
│  └───────┘ └───────┘ └───────────┘ │
│         (private)  (public)        │
└──────────────┬─────────────────────┘
               │
    ┌──────────┼──────────┬────────────────┐
    │          │          │                │
    ▼          ▼          ▼                ▼
┌────────┐ ┌────────┐ ┌────────┐    ┌─────────────┐
│  Neon  │ │Upstash │ │   R2   │    │   Worker    │
│Postgres│ │ Redis  │ │Storage │    │  Process    │
└────────┘ └────────┘ └────────┘    └──────┬──────┘
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │ Claude SDK  │
                                    │  (Anthropic)│
                                    └─────────────┘
```

## Database Schema

### Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    users    │       │    repos    │       │   agents    │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │──┐    │ id (PK)     │──┐    │ id (PK)     │
│ github_id   │  │    │ user_id(FK) │◀─┘    │ repo_id(FK) │◀─┘
│ username    │  │    │ github_repo │       │ file_path   │
│ access_token│  └───▶│ storage_path│       │ agent_name  │
│ created_at  │       │ last_synced │       │ is_deployed │
└─────────────┘       └─────────────┘       └──────┬──────┘
                                                   │
                      ┌─────────────┐              │
                      │  webhooks   │              │
                      ├─────────────┤              │
                      │ id (PK)     │              │
                      │ agent_id(FK)│◀─────────────┘
                      │ webhook_slug│
                      │ callback_url│       ┌─────────────┐
                      │ is_active   │       │    jobs     │
                      └──────┬──────┘       ├─────────────┤
                             │              │ id (PK)     │
                             └─────────────▶│ webhook_id  │
                                            │ status      │
                                            │ payload     │
                                            │ result      │
                                            └─────────────┘
```

### SQL Definitions

```sql
-- Users (GitHub authenticated)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    github_id BIGINT UNIQUE NOT NULL,
    github_username VARCHAR(255) NOT NULL,
    github_access_token TEXT NOT NULL,  -- encrypted at rest
    email VARCHAR(255),
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Connected repositories
CREATE TABLE repos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    github_repo_id BIGINT NOT NULL,
    github_repo_full_name VARCHAR(255) NOT NULL,  -- "owner/repo"
    github_repo_url TEXT NOT NULL,
    default_branch VARCHAR(255) DEFAULT 'main',
    storage_bucket TEXT,  -- R2 bucket name
    storage_path TEXT,    -- path within bucket
    last_synced_at TIMESTAMPTZ,
    last_synced_commit VARCHAR(40),
    sync_status VARCHAR(20) DEFAULT 'pending',  -- pending, syncing, synced, failed
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, github_repo_id)
);

-- Discovered agents from .Claude/agents/
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repo_id UUID NOT NULL REFERENCES repos(id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,      -- ".Claude/agents/sales-outreach.md"
    agent_name VARCHAR(255) NOT NULL,     -- "sales-outreach" (derived from filename)
    description TEXT,                      -- parsed from agent file frontmatter
    is_deployed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(repo_id, file_path)
);

-- Webhook URLs mapped to deployed agents
CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE UNIQUE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,  -- denormalized for rate limiting
    webhook_slug VARCHAR(64) UNIQUE NOT NULL,
    callback_url TEXT,                    -- POST results here when job completes
    is_active BOOLEAN DEFAULT TRUE,

    -- Rate limiting config
    rate_limit_per_minute INT DEFAULT 10,
    rate_limit_per_hour INT DEFAULT 100,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Job execution history
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID REFERENCES webhooks(id) ON DELETE SET NULL,
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,  -- preserve even if webhook deleted

    status VARCHAR(20) DEFAULT 'pending',  -- pending, queued, running, completed, failed

    -- Request data
    payload JSONB,                         -- incoming webhook payload
    callback_url TEXT,                     -- can override webhook's callback_url per-request
    request_headers JSONB,                 -- stored for debugging

    -- Response data
    result JSONB,                          -- agent output
    error TEXT,                            -- error message if failed
    callback_status VARCHAR(20),           -- pending, sent, failed
    callback_response_code INT,

    -- Timing
    queued_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Rate limiting tracking (sliding window)
CREATE TABLE rate_limit_windows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID REFERENCES webhooks(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    window_type VARCHAR(10) NOT NULL,     -- 'minute' or 'hour'
    window_start TIMESTAMPTZ NOT NULL,
    request_count INT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Either webhook_id or user_id must be set, creates separate tracking
    UNIQUE(webhook_id, window_type, window_start),
    UNIQUE(user_id, window_type, window_start)
);

-- Indexes for performance
CREATE INDEX idx_repos_user_id ON repos(user_id);
CREATE INDEX idx_repos_sync_status ON repos(sync_status);
CREATE INDEX idx_agents_repo_id ON agents(repo_id);
CREATE INDEX idx_agents_is_deployed ON agents(is_deployed);
CREATE INDEX idx_webhooks_slug ON webhooks(webhook_slug);
CREATE INDEX idx_webhooks_user_id ON webhooks(user_id);
CREATE INDEX idx_jobs_webhook_id ON jobs(webhook_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX idx_rate_limit_windows_webhook ON rate_limit_windows(webhook_id, window_type, window_start);
CREATE INDEX idx_rate_limit_windows_user ON rate_limit_windows(user_id, window_type, window_start);
```

## API Specification

### Authentication

All endpoints except `/hook/*` and `/health` require authentication via Bearer token (JWT) or session cookie.

### Endpoints

#### Health Check
```
GET /health
Response: { "status": "ok", "version": "1.0.0" }
```

#### Auth Routes (`/auth`)

```
GET /auth/github
  Description: Redirect to GitHub OAuth authorization
  Response: 302 redirect to GitHub

GET /auth/github/callback
  Description: GitHub OAuth callback
  Query params: code, state
  Response: 302 redirect to frontend with session cookie set

GET /auth/me
  Description: Get current authenticated user
  Response: {
    "id": "uuid",
    "github_username": "string",
    "email": "string",
    "avatar_url": "string"
  }

POST /auth/logout
  Description: Clear session
  Response: { "success": true }
```

#### Repo Routes (`/repos`)

```
GET /repos/available
  Description: List user's GitHub repos (from GitHub API, not yet connected)
  Response: {
    "repos": [
      {
        "github_repo_id": 123456,
        "full_name": "owner/repo",
        "description": "...",
        "default_branch": "main",
        "private": false
      }
    ]
  }

GET /repos
  Description: List connected repos
  Response: {
    "repos": [
      {
        "id": "uuid",
        "github_repo_full_name": "owner/repo",
        "sync_status": "synced",
        "last_synced_at": "2026-01-15T...",
        "agent_count": 3
      }
    ]
  }

POST /repos/connect
  Description: Connect a repo (clone + discover agents)
  Body: {
    "github_repo_id": 123456,
    "github_repo_full_name": "owner/repo"
  }
  Response: {
    "repo": { ... },
    "agents": [ ... ]  // discovered agents
  }

GET /repos/{repo_id}
  Description: Get repo details
  Response: {
    "id": "uuid",
    "github_repo_full_name": "owner/repo",
    "sync_status": "synced",
    "last_synced_at": "...",
    "last_synced_commit": "abc123",
    "agents": [ ... ]
  }

POST /repos/{repo_id}/sync
  Description: Manual sync to latest main
  Response: {
    "status": "syncing",
    "message": "Sync started"
  }

DELETE /repos/{repo_id}
  Description: Disconnect repo (deletes agents, webhooks, storage)
  Response: { "success": true }
```

#### Agent Routes (`/agents`)

```
GET /repos/{repo_id}/agents
  Description: List agents in a repo
  Response: {
    "agents": [
      {
        "id": "uuid",
        "file_path": ".Claude/agents/sales-outreach.md",
        "agent_name": "sales-outreach",
        "description": "...",
        "is_deployed": true,
        "webhook_url": "https://app.fly.dev/hook/abc123"  // if deployed
      }
    ]
  }

POST /agents/{agent_id}/deploy
  Description: Deploy agent (create webhook)
  Body: {
    "callback_url": "https://example.com/webhook-callback"  // optional
  }
  Response: {
    "webhook_id": "uuid",
    "webhook_url": "https://app.fly.dev/hook/abc123",
    "webhook_slug": "abc123"
  }

PATCH /agents/{agent_id}/webhook
  Description: Update webhook settings
  Body: {
    "callback_url": "https://...",
    "is_active": true,
    "rate_limit_per_minute": 10
  }
  Response: { "webhook": { ... } }

DELETE /agents/{agent_id}/deploy
  Description: Undeploy agent (delete webhook)
  Response: { "success": true }
```

#### Webhook Routes (`/webhooks`)

```
GET /webhooks
  Description: List all user's webhooks
  Response: {
    "webhooks": [
      {
        "id": "uuid",
        "webhook_url": "https://app.fly.dev/hook/abc123",
        "agent_name": "sales-outreach",
        "repo_name": "owner/repo",
        "is_active": true,
        "callback_url": "...",
        "job_count_24h": 42
      }
    ]
  }

GET /webhooks/{webhook_id}
  Description: Get webhook details
  Response: {
    "id": "uuid",
    "webhook_url": "...",
    "webhook_slug": "abc123",
    "agent": { ... },
    "callback_url": "...",
    "is_active": true,
    "rate_limits": {
      "per_minute": 10,
      "per_hour": 100
    },
    "stats": {
      "total_jobs": 150,
      "jobs_24h": 42,
      "success_rate": 0.95
    }
  }
```

#### Public Webhook Ingress (`/hook`)

```
POST /hook/{webhook_slug}
  Description: Trigger agent execution
  Headers:
    X-Callback-URL: https://... (optional, overrides webhook's callback_url)
  Body: (any JSON - passed as prompt context to agent)
  Response: {
    "job_id": "uuid",
    "status": "queued"
  }
  Errors:
    404: Webhook not found
    429: Rate limit exceeded
    503: Service unavailable
```

#### Job Routes (`/jobs`)

```
GET /jobs
  Description: List jobs (paginated, filterable)
  Query params:
    webhook_id: filter by webhook
    status: filter by status
    limit: default 50
    offset: default 0
  Response: {
    "jobs": [ ... ],
    "total": 150,
    "limit": 50,
    "offset": 0
  }

GET /jobs/{job_id}
  Description: Get job details
  Response: {
    "id": "uuid",
    "status": "completed",
    "webhook_id": "...",
    "agent_name": "sales-outreach",
    "payload": { ... },
    "result": { ... },
    "error": null,
    "callback_status": "sent",
    "created_at": "...",
    "started_at": "...",
    "completed_at": "..."
  }
```

## Key Flows

### Flow 1: Connect Repository

```
┌────────┐          ┌─────────┐          ┌────────┐          ┌─────┐
│ Client │          │   API   │          │ GitHub │          │ R2  │
└───┬────┘          └────┬────┘          └───┬────┘          └──┬──┘
    │                    │                   │                  │
    │ POST /repos/connect│                   │                  │
    │ {github_repo_id}   │                   │                  │
    │───────────────────▶│                   │                  │
    │                    │                   │                  │
    │                    │ GET /repos/{id}   │                  │
    │                    │──────────────────▶│                  │
    │                    │                   │                  │
    │                    │ clone_url, branch │                  │
    │                    │◀──────────────────│                  │
    │                    │                   │                  │
    │                    │ git clone (via token)               │
    │                    │──────────────────▶│                  │
    │                    │                   │                  │
    │                    │ repo contents     │                  │
    │                    │◀──────────────────│                  │
    │                    │                   │                  │
    │                    │ Upload to R2                        │
    │                    │─────────────────────────────────────▶│
    │                    │                   │                  │
    │                    │ Parse .Claude/agents/               │
    │                    │ Create agent records                │
    │                    │                   │                  │
    │ { repo, agents }   │                   │                  │
    │◀───────────────────│                   │                  │
    │                    │                   │                  │
```

### Flow 2: Webhook Triggered

```
┌──────────┐     ┌─────────┐     ┌───────┐     ┌────────┐     ┌──────────┐
│ External │     │   API   │     │ Redis │     │ Worker │     │ Callback │
│ Service  │     │         │     │       │     │        │     │   URL    │
└────┬─────┘     └────┬────┘     └───┬───┘     └───┬────┘     └────┬─────┘
     │                │              │             │               │
     │ POST /hook/abc │              │             │               │
     │ {payload}      │              │             │               │
     │───────────────▶│              │             │               │
     │                │              │             │               │
     │                │ Check rate   │             │               │
     │                │ limits       │             │               │
     │                │              │             │               │
     │                │ Create job   │             │               │
     │                │ (pending)    │             │               │
     │                │              │             │               │
     │                │ LPUSH job_id │             │               │
     │                │─────────────▶│             │               │
     │                │              │             │               │
     │ {job_id,       │              │             │               │
     │  status:queued}│              │             │               │
     │◀───────────────│              │             │               │
     │                │              │             │               │
     │                │              │ BRPOP      │               │
     │                │              │◀────────────│               │
     │                │              │             │               │
     │                │              │ job_id     │               │
     │                │              │────────────▶│               │
     │                │              │             │               │
     │                │              │             │ Load agent    │
     │                │              │             │ from R2       │
     │                │              │             │               │
     │                │              │             │ Run Claude    │
     │                │              │             │ Agent SDK     │
     │                │              │             │               │
     │                │              │             │ Update job    │
     │                │              │             │ (completed)   │
     │                │              │             │               │
     │                │              │             │ POST result   │
     │                │              │             │──────────────▶│
     │                │              │             │               │
     │                │              │             │ 200 OK        │
     │                │              │             │◀──────────────│
     │                │              │             │               │
```

### Flow 3: Manual Sync

```
┌────────┐          ┌─────────┐          ┌────────┐          ┌─────┐
│ Client │          │   API   │          │ GitHub │          │ R2  │
└───┬────┘          └────┬────┘          └───┬────┘          └──┬──┘
    │                    │                   │                  │
    │ POST /repos/{id}/sync                  │                  │
    │───────────────────▶│                   │                  │
    │                    │                   │                  │
    │ {status: syncing}  │                   │                  │
    │◀───────────────────│                   │                  │
    │                    │                   │                  │
    │                    │ git fetch origin main               │
    │                    │──────────────────▶│                  │
    │                    │                   │                  │
    │                    │ latest commit     │                  │
    │                    │◀──────────────────│                  │
    │                    │                   │                  │
    │                    │ Compare commits   │                  │
    │                    │ (skip if same)    │                  │
    │                    │                   │                  │
    │                    │ git pull          │                  │
    │                    │──────────────────▶│                  │
    │                    │                   │                  │
    │                    │ Update R2         │                  │
    │                    │─────────────────────────────────────▶│
    │                    │                   │                  │
    │                    │ Re-parse .Claude/agents/            │
    │                    │ Update agent records                │
    │                    │ (add new, mark removed)             │
    │                    │                   │                  │
```

## Project Structure

```
services/webhook-service/
├── PLANNING.md                    # This document
├── README.md                      # Setup and usage instructions
│
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Settings from env vars
│   ├── database.py                # Neon/SQLAlchemy setup
│   ├── dependencies.py            # FastAPI dependencies (auth, db session)
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── repo.py
│   │   ├── agent.py
│   │   ├── webhook.py
│   │   ├── job.py
│   │   └── rate_limit.py
│   │
│   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── repo.py
│   │   ├── agent.py
│   │   ├── webhook.py
│   │   └── job.py
│   │
│   ├── routers/                   # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py                # /auth/*
│   │   ├── repos.py               # /repos/*
│   │   ├── agents.py              # /agents/*
│   │   ├── webhooks.py            # /webhooks/*
│   │   ├── hooks.py               # /hook/* (public ingress)
│   │   └── jobs.py                # /jobs/*
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── github.py              # GitHub API client
│   │   ├── storage.py             # R2/S3 operations
│   │   ├── repo_sync.py           # Git clone/sync logic
│   │   ├── agent_discovery.py     # Parse .Claude/agents/
│   │   ├── agent_runner.py        # Claude SDK execution
│   │   ├── rate_limiter.py        # Rate limiting logic
│   │   ├── callback.py            # Callback URL poster
│   │   └── queue.py               # Redis queue operations
│   │
│   └── worker/                    # Background job processor
│       ├── __init__.py
│       ├── main.py                # Worker entry point
│       └── processor.py           # Job processing logic
│
├── alembic/                       # Database migrations
│   ├── env.py
│   ├── versions/
│   └── alembic.ini
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── test_auth.py
│   ├── test_repos.py
│   ├── test_agents.py
│   ├── test_webhooks.py
│   ├── test_hooks.py
│   └── test_jobs.py
│
├── scripts/
│   └── seed_data.py               # Development seed data
│
├── Dockerfile                     # Multi-stage build
├── docker-compose.yml             # Local development
├── fly.toml                       # Fly.io deployment config
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Dev dependencies (pytest, etc.)
├── .env.example                   # Environment variables template
└── pyproject.toml                 # Python project config
```

## Implementation Phases

### Phase 1: Foundation
- [ ] Project setup (FastAPI, SQLAlchemy, Alembic)
- [ ] Config management (Pydantic settings)
- [ ] Database models and migrations
- [ ] Health check endpoint
- [ ] Docker setup for local development

### Phase 2: Authentication
- [ ] GitHub OAuth flow
- [ ] JWT token generation
- [ ] Session management
- [ ] Auth middleware

### Phase 3: Repository Management
- [ ] GitHub API integration (list repos)
- [ ] R2 storage setup
- [ ] Git clone to R2
- [ ] Agent discovery (parse .Claude/agents/)
- [ ] Manual sync endpoint

### Phase 4: Webhook System
- [ ] Webhook creation (slug generation)
- [ ] Webhook CRUD endpoints
- [ ] Public webhook ingress endpoint
- [ ] Rate limiting implementation

### Phase 5: Job Processing
- [ ] Redis queue setup (Upstash)
- [ ] Worker process
- [ ] Claude Agent SDK integration
- [ ] Callback URL posting
- [ ] Job status tracking

### Phase 6: Production Readiness
- [ ] Error handling and logging
- [ ] Monitoring and metrics
- [ ] Fly.io deployment
- [ ] CI/CD pipeline
- [ ] Documentation

## Environment Variables

```bash
# Application
APP_ENV=development  # development, staging, production
APP_SECRET_KEY=your-secret-key-for-jwt
APP_URL=https://your-app.fly.dev

# Database (Neon)
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Redis (Upstash)
REDIS_URL=rediss://user:pass@host:port

# GitHub OAuth
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret
GITHUB_REDIRECT_URI=https://your-app.fly.dev/auth/github/callback

# Cloudflare R2
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=webhook-service-repos

# Claude SDK
ANTHROPIC_API_KEY=your-anthropic-api-key

# Rate Limits (defaults)
DEFAULT_RATE_LIMIT_PER_MINUTE=10
DEFAULT_RATE_LIMIT_PER_HOUR=100
USER_RATE_LIMIT_PER_MINUTE=50
USER_RATE_LIMIT_PER_HOUR=500
```

## Security Considerations

1. **Token Encryption**: GitHub access tokens stored encrypted at rest (using Fernet)
2. **Webhook Slugs**: Generated using `secrets.token_urlsafe(32)` - 256 bits of entropy
3. **Rate Limiting**: Prevents abuse, applied at webhook and user levels
4. **Input Validation**: All inputs validated via Pydantic schemas
5. **SQL Injection**: Prevented by SQLAlchemy ORM
6. **CORS**: Restricted to known frontend origins
7. **HTTPS Only**: Enforced in production

## Future Considerations

1. **GitHub App**: Migrate from OAuth App to GitHub App for push webhooks
2. **Agent Versioning**: Track agent versions, allow rollback
3. **Team Support**: Multiple users per organization
4. **Usage Analytics**: Detailed usage metrics and dashboards
5. **Agent Marketplace**: Share/discover public agents
6. **Custom Domains**: Allow users to use their own webhook domains
