---
name: aidp-runtime-validate
description: Validate live AIDP runtime coverage by comparing the uploaded source manifest, live source scope, customer bucket inventory, target layers, parquet schema quality, job state, master catalog coverage, row-count parity, and evidence metadata. Use when Codex needs to inspect or explain an AIDP run, assess whether a workspace is ready for handoff, or produce a read-only validation summary after deployment or during incident analysis.
---

# AIDP Runtime Validate

## Overview

Use this skill for read-only verification of what an AIDP run actually covered. It is the main bridge between the uploaded source manifest, the customer bucket, target medallion layers, control-state tables, and the observed job or runtime state.

## Prerequisites

- `.oci/` is required for live runtime validation.
- `.source/` is optional and useful only when comparing runtime behavior back to original source evidence.

## Workflow

1. Read `references/runtime-validation.md` before investigating a live run.
2. Resolve the runtime seed first: explicit workspace, job, or jobRun ids win; otherwise reuse the latest launch report if the workflow supports it.
3. Use `uv run codex-oci aidp work-requests list|get ...` when control-plane status or recent asynchronous activity helps anchor the investigation.
4. Compare the uploaded source manifest with the live source scope and the customer bucket inventory.
5. Inspect the materialized bronze, stage, silver, gold, and control outputs before making any claims about readiness, and keep `file_state`, `output_refresh`, `stream_run_state`, and `stream_batch_state` separate in the analysis.
6. For Databricks-to-AIDP migrations, compare Azure Databricks `COUNT(*)`, exported CSV rows, OCI Object Storage downloaded rows, and AIDP Workbench count before accepting parity.
7. Review master catalog tables and coverage assessment last, once the raw object-storage and control-state evidence is clear.

## Rules

- Keep this flow read-only unless the user explicitly pivots into deployment or recovery.
- Sanitize outputs and summaries. Do not dump secrets or full private OCIDs.
- Label each evidence artifact with `source_type`, `capture_method`, `is_real_console`, `redaction_level`, and `accepted_for_report` when the output will feed a report.
- Do not treat API, DOM, CLI, summarized, or generated images as real console screenshots.
- Distinguish clearly between active reference scope, disabled-but-live sources, and historical fallback behavior.
- Distinguish queue backlog from runtime progress. `file_state.pending_*` and `output_refresh.pending_*` answer different questions.
- Treat consecutive zero-backlog windows as stronger evidence than a single zero snapshot when the flow includes streaming coexistence.
- If coverage is incomplete, explain where the mismatch sits: source selection, processing progress, schema quality, or catalog registration.

## Outputs

- Coverage assessment for the active reference scope.
- Observed stage and job status.
- Row-count parity summary across source, transfer, and AIDP validation surfaces when applicable.
- Evidence metadata summary distinguishing real console captures from supporting artifacts.
- Layer-by-layer and control-state evidence for bronze, stage, silver, gold, and control outputs.
- A handoff-quality summary of whether the run is ready or not.
