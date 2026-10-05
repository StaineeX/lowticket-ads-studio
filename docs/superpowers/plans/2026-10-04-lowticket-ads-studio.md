# LowTicket Ads Studio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local-first MVP that creates, analyzes, and safely prepares low-ticket Meta Ads and Google Ads campaigns with AI-assisted copy and approval-gated operations.

**Architecture:** A FastAPI backend owns domain rules, SQLite persistence, AI/provider ports, CSV imports, recommendations, and the preview/approval safety boundary. A React/Vite frontend consumes the JSON API and presents offer economics, campaign drafts, metrics, recommendations, and approval dialogs. External ad APIs remain behind provider ports; deterministic fake providers make the MVP runnable without credentials.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy, Alembic, SQLite, pytest; Node 20+, React, Vite, TypeScript, Vitest, Testing Library.

**Spec:** `docs/superpowers/specs/2026-10-04-lowticket-ads-studio-design.md`

## Global Constraints

- Local-first runtime; no provider credentials in SQLite.
- New campaigns are always created paused.
- Every write requires a dry-run preview and a single-use approval token.
- Default daily budget ceiling is `target_cpa * 3`.
- No recommendation is auto-applied.
- Deterministic templates work when no AI provider is configured.
- Keep dependencies minimal and use official provider APIs only when a live adapter is added.
- MIT license.

## Review Focus

- Zero or missing price/margin/conversion inputs must return a clear validation error rather than divide by zero — covered in Task 2.
- Imported CSVs with decimal commas, UTF-8 BOM, missing optional columns, or unknown platform must fail safely or normalize predictably — covered in Task 3.
- A modified, expired, or replayed approval token must never call a provider — covered in Task 5.
- Provider failures must produce an audit event and a non-success response — covered in Task 5.
- The UI must not present a live publish action for a campaign draft that is not paused or approved — covered in Task 6.

### Task 1: Repository scaffold and runtime configuration

**Files:**
- Create: `pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/tests/test_health.py`
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `.gitignore`
- Create: `README.md`

**Interfaces:**
- Produces `backend.app.main:app` with `GET /api/health -> {"status":"ok"}`.
- Produces frontend script commands `npm run dev`, `npm run build`, and `npm test`.

- [ ] **Step 1: Write the failing backend health test**

  Create a TestClient test asserting status 200 and the exact JSON `{"status": "ok"}`.

- [ ] **Step 2: Run the focused test**

  Run: `python -m pytest backend/tests/test_health.py -q`
  Expected: FAIL because the backend package does not exist yet.

- [ ] **Step 3: Implement the minimal backend and frontend scaffold**

  Configure FastAPI, CORS for the local Vite origin, environment loading, and a Vite React shell. Do not add provider or database behavior in this task.

- [ ] **Step 4: Run the focused test and frontend build**

  Run: `python -m pytest backend/tests/test_health.py -q` and `npm run build` from `frontend`.
  Expected: PASS and a successful production bundle.

- [ ] **Step 5: Commit**

  `git add .gitignore README.md pyproject.toml backend frontend && git commit -m "chore: scaffold local ads studio"`

### Task 2: Offer economics and campaign validation domain

**Files:**
- Create: `backend/app/domain/economics.py`
- Create: `backend/app/domain/campaigns.py`
- Create: `backend/tests/domain/test_economics.py`
- Create: `backend/tests/domain/test_campaigns.py`

**Interfaces:**
- `calculate_economics(price: Decimal, gross_margin_pct: Decimal, checkout_conversion_pct: Decimal, refund_pct: Decimal) -> EconomicsResult`.
- `break_even_cpa(economics: EconomicsResult) -> Decimal`.
- `break_even_roas(economics: EconomicsResult) -> Decimal`.
- `validate_copy(platform: Platform, copy: CampaignCopy) -> list[ValidationIssue]`.
- `default_budget_ceiling(target_cpa: Decimal) -> Decimal`.

- [ ] **Step 1: Write failing tests for exact economic formulas**

  Assert net revenue is `price * (1 - refund_pct / 100)`, contribution value is net revenue times margin, break-even CPA equals contribution value times checkout conversion, and break-even ROAS equals `price / contribution value`. Assert invalid non-positive price, margin outside 0–100, conversion outside 0–100, and refund outside 0–100 raise `ValueError`.

- [ ] **Step 2: Run economics tests to verify failure**

  Run: `python -m pytest backend/tests/domain/test_economics.py -q`
  Expected: FAIL because the functions are not defined.

- [ ] **Step 3: Implement money-safe domain calculations**

  Use `Decimal`, quantize monetary outputs to two decimal places, and keep percentages as Decimal values. Return a frozen result object containing `net_revenue`, `contribution_value`, `break_even_cpa`, and `break_even_roas`.

- [ ] **Step 4: Write failing tests for platform copy limits and budget ceiling**

  Cover Meta primary text, headline, CTA, Google RSA headlines, and Google descriptions. Assert issues include field name, maximum, and actual length. Assert the budget ceiling is exactly target CPA times three and rejects a non-positive target CPA.

- [ ] **Step 5: Implement campaign validation**

  Use platform-specific limits in one immutable mapping. Keep validation pure and return structured issues rather than raising for ordinary copy violations.

- [ ] **Step 6: Run domain tests**

  Run: `python -m pytest backend/tests/domain -q`
  Expected: PASS.

- [ ] **Step 7: Commit**

  `git add backend/app/domain backend/tests/domain && git commit -m "feat: add low-ticket economics and campaign validation"`

### Task 3: SQLite persistence and CSV metric import

**Files:**
- Create: `backend/app/db.py`
- Create: `backend/app/models.py`
- Create: `backend/app/repositories.py`
- Create: `backend/app/services/metrics_import.py`
- Create: `backend/app/api/offers.py`
- Create: `backend/app/api/metrics.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/services/test_metrics_import.py`
- Create: `backend/tests/api/test_offers.py`

**Interfaces:**
- `MetricImporter.import_csv(content: bytes, platform: Platform) -> ImportResult`.
- `OfferRepository.create(offer: OfferCreate) -> Offer`.
- `OfferRepository.list() -> list[Offer]`.
- `POST /api/offers` and `GET /api/offers`.
- `POST /api/metrics/import` accepting multipart CSV plus `platform`.

- [ ] **Step 1: Write failing repository and import tests**

  Assert an offer survives a create/list round trip in a temporary SQLite database. Assert UTF-8 BOM and decimal comma CSVs normalize to Decimal values. Assert missing campaign identifier or unknown platform returns a 422 response.

- [ ] **Step 2: Run focused tests to verify failure**

  Run: `python -m pytest backend/tests/services/test_metrics_import.py backend/tests/api/test_offers.py -q`
  Expected: FAIL because persistence and routes are not implemented.

- [ ] **Step 3: Implement the database layer**

  Use SQLAlchemy models for offers and metric records, create tables on application startup for the local MVP, and allow a `DATABASE_URL` environment override. Keep credentials out of every model.

- [ ] **Step 4: Implement CSV normalization**

  Detect UTF-8 BOM, normalize semicolon/comma delimiters and decimal commas, map common Meta and Google column names into `MetricRecord`, and reject rows that cannot identify a campaign or date with row-level errors.

- [ ] **Step 5: Implement offer and metric routes**

  Add Pydantic request/response schemas, route validation, and dependency injection for the repository/session. Return import counts and structured row errors.

- [ ] **Step 6: Run focused tests**

  Run: `python -m pytest backend/tests/services/test_metrics_import.py backend/tests/api/test_offers.py -q`
  Expected: PASS.

- [ ] **Step 7: Commit**

  `git add backend/app backend/tests && git commit -m "feat: persist offers and import ad metrics"`

### Task 4: AI campaign brief generation and provider ports

**Files:**
- Create: `backend/app/ai/ports.py`
- Create: `backend/app/ai/templates.py`
- Create: `backend/app/ai/service.py`
- Create: `backend/app/providers/ports.py`
- Create: `backend/app/providers/fake.py`
- Create: `backend/app/api/campaigns.py`
- Create: `backend/tests/ai/test_campaign_generation.py`
- Create: `backend/tests/providers/test_provider_contract.py`

**Interfaces:**
- `AIProvider.generate_campaign_brief(request: CampaignBriefRequest) -> CampaignBrief`.
- `CampaignService.generate_draft(request: CampaignDraftRequest) -> CampaignDraft`.
- `AdProvider.preview_create_campaign(draft: CampaignDraft) -> ProviderPreview`.
- `AdProvider.apply_create_campaign(draft: CampaignDraft) -> ProviderCampaign`.
- `POST /api/campaign-drafts/generate`.

- [ ] **Step 1: Write failing generation and fake-provider contract tests**

  Assert no configured AI provider still returns deterministic copy and creative briefs. Assert generated Google headlines and descriptions pass validation or are reported as issues. Assert the fake provider never applies a campaign through preview.

- [ ] **Step 2: Run focused tests to verify failure**

  Run: `python -m pytest backend/tests/ai backend/tests/providers -q`
  Expected: FAIL because AI, provider ports, and campaign service are not implemented.

- [ ] **Step 3: Implement deterministic templates and AI port**

  Build an offer-aware prompt/request model and deterministic fallback using the offer name, benefit, proof, CTA, audience, and angle. Add an OpenAI-compatible HTTP adapter and an Ollama-compatible configuration path without making either required for startup.

- [ ] **Step 4: Implement campaign draft generation**

  Generate three variants per selected platform, validate every variant, attach economics and budget ceiling, and persist the draft as paused. Keep copy generation separate from provider execution.

- [ ] **Step 5: Implement fake Meta and Google provider adapters**

  Return typed previews and paused provider campaigns. Store calls in memory so tests can assert that no apply call happened before approval.

- [ ] **Step 6: Run focused tests**

  Run: `python -m pytest backend/tests/ai backend/tests/providers -q`
  Expected: PASS.

- [ ] **Step 7: Commit**

  `git add backend/app backend/tests && git commit -m "feat: generate campaign drafts with provider ports"`

### Task 5: Recommendations and approval-gated operations

**Files:**
- Create: `backend/app/services/recommendations.py`
- Create: `backend/app/services/approvals.py`
- Create: `backend/app/api/operations.py`
- Create: `backend/app/api/recommendations.py`
- Create: `backend/app/audit.py`
- Create: `backend/tests/services/test_approvals.py`
- Create: `backend/tests/api/test_operations.py`

**Interfaces:**
- `analyze_metrics(records: list[MetricRecord], economics: EconomicsResult) -> list[Recommendation]`.
- `preview_operation(operation: OperationRequest) -> OperationPreview`.
- `approve_operation(operation_id: str, token: str) -> OperationResult`.

- [ ] **Step 1: Write failing tests for recommendations and approval safety**

  Cover pause recommendation for zero conversions with spend, scale recommendation only when ROAS is above target and CPA is below target, budget ceiling rejection, modified payload rejection, expired token rejection, replay rejection, and provider failure audit logging.

- [ ] **Step 2: Run focused tests to verify failure**

  Run: `python -m pytest backend/tests/services/test_approvals.py backend/tests/api/test_operations.py -q`
  Expected: FAIL because recommendation and approval services are not implemented.

- [ ] **Step 3: Implement recommendation rules**

  Keep rules deterministic and evidence-based: zero-conversion spend proposes pause; CPA above three times target proposes pause; high-ROAS campaigns may propose a bounded budget increase; every item includes evidence and risk.

- [ ] **Step 4: Implement preview tokens and audit events**

  Hash the exact normalized payload, issue a single-use token with a short expiry, enforce the daily ceiling, and append audit events for preview, approval, rejection, and provider failure.

- [ ] **Step 5: Wire operation routes**

  Make preview the only route that can prepare a mutation and approval the only route that can call `apply_*`. Return safe error bodies without exposing credentials.

- [ ] **Step 6: Run focused tests**

  Run: `python -m pytest backend/tests/services/test_approvals.py backend/tests/api/test_operations.py -q`
  Expected: PASS.

- [ ] **Step 7: Commit**

  `git add backend/app backend/tests && git commit -m "feat: add recommendations and approval gates"`

### Task 6: Browser UI for offer, drafts, metrics, and approvals

**Files:**
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/api.ts`
- Create: `frontend/src/types.ts`
- Create: `frontend/src/components/OfferForm.tsx`
- Create: `frontend/src/components/CampaignDraft.tsx`
- Create: `frontend/src/components/RecommendationList.tsx`
- Create: `frontend/src/components/ApprovalDialog.tsx`
- Create: `frontend/src/styles.css`
- Create: `frontend/src/__tests__/App.test.tsx`

**Interfaces:**
- `api.createOffer(input: OfferInput): Promise<Offer>`.
- `api.generateDraft(input: CampaignDraftInput): Promise<CampaignDraft>`.
- `api.previewOperation(input: OperationInput): Promise<OperationPreview>`.
- `api.approveOperation(id: string, token: string): Promise<OperationResult>`.

- [ ] **Step 1: Write failing component tests**

  Assert the offer form displays economics after valid input, campaign drafts show platform validation issues, and the approval button is disabled until a preview exists.

- [ ] **Step 2: Run frontend tests to verify failure**

  Run: `npm test -- --run`
  Expected: FAIL because the frontend components do not exist.

- [ ] **Step 3: Implement the API client and typed components**

  Keep state local to the page, use accessible labels and buttons, display currency and percentages clearly, and make provider/API errors actionable. Do not add a client-side bypass for approval.

- [ ] **Step 4: Add the approval confirmation flow**

  Show proposed budget/status changes, exact provider/platform, risk, and expiry. Only after the user confirms call the approval endpoint; show the resulting audit status.

- [ ] **Step 5: Run frontend tests and build**

  Run: `npm test -- --run` and `npm run build`.
  Expected: PASS and successful production bundle.

- [ ] **Step 6: Commit**

  `git add frontend && git commit -m "feat: add local campaign planning UI"`

### Task 7: Documentation, local smoke test, and release preparation

**Files:**
- Modify: `README.md`
- Create: `.env.example`
- Create: `LICENSE`
- Create: `docker-compose.yml`
- Create: `scripts/smoke.ps1`
- Create: `backend/tests/test_smoke_contract.py`

- [ ] **Step 1: Write the smoke contract test**

  Assert a fresh database can create an offer, calculate economics, generate a deterministic draft, preview a fake-provider operation, and apply it only after approval.

- [ ] **Step 2: Implement deployment and setup documentation**

  Document local Python/Node prerequisites, mock mode, optional AI configuration, optional provider credentials, safety defaults, and the exact commands for running backend, frontend, tests, and smoke verification.

- [ ] **Step 3: Add the smoke script**

  Start the API in a temporary database, call health and the core draft flow, then stop cleanly without touching live ad accounts.

- [ ] **Step 4: Run the full verification suite**

  Run: `python -m pytest -q`, `npm test -- --run`, `npm run build`, and `powershell -ExecutionPolicy Bypass -File scripts/smoke.ps1`.
  Expected: all commands pass from a clean configuration.

- [ ] **Step 5: Review the diff and commit**

  Run `git diff --check` and `git status --short`, then commit with `git commit -m "docs: prepare local MVP release"`.

- [ ] **Step 6: Prepare the GitHub repository**

  Create a new GitHub repository named `lowticket-ads-studio`, add it as `origin`, push the default branch, and verify the remote README and license render correctly. Never include credentials or `.env` files.
