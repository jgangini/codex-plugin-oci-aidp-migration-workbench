---
name: aidp-source-intake
description: Inspect the local `.source` folder, infer source-platform hints, and turn mixed migration evidence into an AIDP migration or greenfield project plan. Use when Codex needs to start from source SQL, notebooks, exports, scripts, or requirements documents and shape an AIDP project before manifest authoring, bootstrap, or deployment.
---

# AIDP Source Intake

## Overview

Use this skill when the repo is being driven by local source evidence instead of an already-stable AIDP implementation. Treat `.source/` as the working intake root for cross-platform migration or document-driven project creation.

## Prerequisites

- `.source/` must exist at the repo root for source-driven planning.
- `.source/README.md` must be present and non-empty before intake work starts.
- `.oci/` is optional during planning, but required before any live OCI or AIDP validation, bootstrap, deploy, recovery, or storage mutation.

## Workflow

1. Read `references/source-intake.md` before planning a migration or greenfield AIDP project from source artifacts.
2. Start with `uv run codex-oci aidp source inspect` to inventory `.source`, classify artifacts, and infer platform hints.
3. Read `.source/README.md` and the highest-signal artifacts next: SQL, notebooks, documents, exports, and scripts that describe the source behavior.
4. Convert the evidence into an AIDP delivery plan: source systems, medallion layers, reference data, control-state needs, batch-versus-streaming requirements, and expected validation evidence.
5. If `aidp/config/migration_manifest.json` already exists, align the intake findings with it. If it does not, use the intake output to drive the first manifest draft.
6. Only require `.oci/` and live tenant checks after the source-driven plan is coherent enough to validate or mutate OCI or AIDP resources.

## Rules

- Treat `.source/` as local input, not as content to package into the plugin.
- Keep source evidence portable. Summarize or extract reusable patterns; do not vendor customer-specific artifacts into repo docs or bundled skills.
- Accept mixed source formats such as SQL, notebooks, documents, scripts, and exports from any data platform when building the plan.
- Prefer explaining gaps explicitly when `.source` is incomplete instead of guessing hidden source behavior.
- Write intake reports under `aidp/reports/` only when the user asks for persisted evidence.

## Outputs

- A concise AIDP migration or project plan derived from `.source`.
- Identified source-platform hints and the artifacts that matter most.
- A list of missing information, blockers, and the next wrapper or skill flows to use.
