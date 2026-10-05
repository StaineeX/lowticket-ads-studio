# LowTicket Ads Studio Design

## Goal

Build a local-first web application for creating, analyzing, and safely preparing low-ticket Meta Ads and Google Ads campaigns, with AI-assisted copy and creative generation and explicit approval before any live mutation.

## Intended user and success criteria

The first user is a solo marketer or small operator running low-ticket offers. The MVP is successful when it can:

- capture an offer and basic unit economics;
- generate platform-constrained campaign copy and creative briefs;
- calculate break-even CPA and ROAS;
- ingest exported Meta/Google performance data;
- produce bounded pause, budget, and test recommendations;
- create paused campaign drafts through provider adapters;
- require a preview plus explicit approval before applying a live change;
- run locally with SQLite and keep provider credentials out of the database.

## Scope

### In scope

- React/Vite browser UI with a Python/FastAPI backend.
- SQLite persistence for offers, campaign drafts, imported metrics, recommendations, approvals, and audit events.
- AI provider abstraction supporting OpenAI-compatible endpoints, Gemini, Groq, OpenRouter, and Ollama-compatible local endpoints.
- Meta and Google provider interfaces with mock implementations for local development and tests.
- CSV import for Meta Ads Manager and Google Ads exports.
- Low-ticket economics: price, gross margin, checkout conversion, refund rate, target CPA, break-even CPA, and break-even ROAS.
- Campaign brief generation, copy variants, creative briefs, and platform character-limit validation.
- Draft-first campaign mutations with preview, approval token, budget ceilings, and paused-by-default creation.

### Out of scope for the MVP

- Multi-user accounts, billing, agency workspaces, or hosted OAuth broker.
- Automatic unsupervised spend changes.
- Browser automation or scraping logged-in ad dashboards.
- Guaranteed performance prediction.
- Video generation or asset hosting.

## Architecture

The frontend calls a versioned FastAPI JSON API. Domain services contain offer economics, campaign planning, validation, recommendations, and approval logic. Provider adapters are isolated behind interfaces so the MVP can run entirely against deterministic fakes and later connect to official APIs without changing the domain layer.

The default runtime is local: SQLite file, local API process, and browser UI. AI calls are optional and go through one provider interface. Ollama-compatible endpoints are supported for local inference; if no AI provider is configured, deterministic templates still generate a usable draft.

## Core domain model

- `Offer`: name, landing URL, currency, price, gross margin percentage, checkout conversion rate, refund rate, target CPA, target ROAS.
- `CampaignDraft`: platform, objective, offer id, budget, status, audience hypothesis, copy variants, creative briefs, and validation results.
- `MetricRecord`: platform, campaign/ad identifiers, date, spend, impressions, clicks, conversions, revenue.
- `Recommendation`: type, rationale, evidence, proposed change, risk level, and lifecycle status.
- `Approval`: operation id, exact payload hash, preview, expiry, approver, and applied/rejected state.
- `AuditEvent`: timestamp, actor, provider, operation, payload summary, result, and error details.

## Safety rules

- Provider credentials are read from environment variables or a local ignored file, never persisted in SQLite.
- All writes are dry-run previews first.
- Approval tokens are single-use, short-lived, and bound to the exact payload.
- New campaigns are created paused.
- A configurable daily budget ceiling defaults to the offer's target CPA multiplied by 3.
- No recommendation is auto-applied.
- Provider failures are recorded without marking an operation successful.

## API surface

- `POST /api/offers` and `GET /api/offers`
- `POST /api/offers/{id}/economics`
- `POST /api/campaign-drafts/generate`
- `POST /api/campaign-drafts/validate`
- `POST /api/metrics/import`
- `POST /api/recommendations/analyze`
- `POST /api/operations/preview`
- `POST /api/operations/{id}/approve`
- `GET /api/audit`
- `GET /api/health`

## Testing and verification

- Domain tests cover economics, currency-safe calculations, validation limits, recommendations, and approval-token replay/expiry.
- API tests cover request validation, CSV import, provider failures, and approval flow.
- Provider contract tests use fakes and assert that campaign creation is paused and mutations are never sent before approval.
- Frontend tests cover the offer form, campaign draft rendering, validation errors, and approval confirmation.
- Final verification runs backend tests, frontend tests, type checks, and a local smoke test from clean configuration.

## Implementation choices

- Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy, Alembic, SQLite, pytest.
- Node 20+, React, Vite, TypeScript, Vitest, Testing Library.
- Keep dependencies minimal and prefer standard library helpers for CSV, hashing, and time handling where practical.
- MIT license for the repository.
