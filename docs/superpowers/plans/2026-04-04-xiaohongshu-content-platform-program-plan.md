# Xiaohongshu Content Platform Program Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the Xiaohongshu content platform as a staged program of OpenSpec changes, from backend foundation to crawler, analysis, content generation, review and publish, Feishu sync, and multi-surface operator access.

**Architecture:** Build on a modular monolith foundation, then layer domain-specific workflow capabilities as independent OpenSpec changes. Keep all entrypoints thin, all external dependencies behind providers, and all long-running work queue-backed and stage-resumable.

**Tech Stack:** FastAPI, SQLAlchemy, PostgreSQL, Celery, Redis, Playwright, LangChain, OpenAI-compatible providers, Feishu Bitable integrations, lightweight web UI

---

## Program Breakdown

### Task 1: Foundation

**Files:**
- Reference: `openspec/changes/bootstrap-xiaohongshu-content-platform/`
- Reference: `docs/superpowers/plans/2026-04-04-bootstrap-xiaohongshu-content-platform.md`

- [ ] **Step 1: Review the foundation change artifacts**

Read:
- `openspec/changes/bootstrap-xiaohongshu-content-platform/proposal.md`
- `openspec/changes/bootstrap-xiaohongshu-content-platform/design.md`
- `openspec/changes/bootstrap-xiaohongshu-content-platform/tasks.md`

- [ ] **Step 2: Execute the foundation implementation plan**

Run the implementation flow from:
- `docs/superpowers/plans/2026-04-04-bootstrap-xiaohongshu-content-platform.md`

- [ ] **Step 3: Verify foundation readiness**

Run:
- `openspec validate bootstrap-xiaohongshu-content-platform`

- [ ] **Step 4: Archive the foundation change after implementation passes**

Run:
- `openspec archive bootstrap-xiaohongshu-content-platform`

- [ ] **Step 5: Commit**

```bash
git add openspec docs app tests
git commit -m "feat: complete platform foundation"
```

### Task 2: Collector track

**Files:**
- Reference: `openspec/changes/add-xiaohongshu-collector/proposal.md`

- [ ] **Step 1: Create collector design and specs**
- [ ] **Step 2: Write collector tasks**
- [ ] **Step 3: Implement and verify crawling, filters, persistence, and diagnostics**
- [ ] **Step 4: Validate and archive the collector change**
- [ ] **Step 5: Commit**

### Task 3: Analysis and topic track

**Files:**
- Reference: `openspec/changes/add-analysis-and-topic-generation/proposal.md`

- [ ] **Step 1: Create analysis design and specs**
- [ ] **Step 2: Write analysis and topic tasks**
- [ ] **Step 3: Implement report generation and topic suggestion workflows**
- [ ] **Step 4: Validate and archive the analysis change**
- [ ] **Step 5: Commit**

### Task 4: Draft and image generation track

**Files:**
- Reference: `openspec/changes/add-draft-and-image-generation/proposal.md`

- [ ] **Step 1: Create generation design and specs**
- [ ] **Step 2: Write draft and image tasks**
- [ ] **Step 3: Implement draft generation, image generation, and generation audit records**
- [ ] **Step 4: Validate and archive the generation change**
- [ ] **Step 5: Commit**

### Task 5: Review and publish track

**Files:**
- Reference: `openspec/changes/add-review-and-publish-flow/proposal.md`

- [ ] **Step 1: Create review and publish design and specs**
- [ ] **Step 2: Write review and publish tasks**
- [ ] **Step 3: Implement review gates, publish routing, and publish auditability**
- [ ] **Step 4: Validate and archive the publish-flow change**
- [ ] **Step 5: Commit**

### Task 6: Collaboration and operator surfaces

**Files:**
- Reference: `openspec/changes/add-feishu-sync/proposal.md`
- Reference: `openspec/changes/add-rest-mcp-and-web-ui/proposal.md`

- [ ] **Step 1: Create Feishu sync design, specs, and tasks**
- [ ] **Step 2: Create REST, MCP, and Web UI design, specs, and tasks**
- [ ] **Step 3: Implement sync and operator entrypoints over shared services**
- [ ] **Step 4: Validate and archive both changes**
- [ ] **Step 5: Commit**
