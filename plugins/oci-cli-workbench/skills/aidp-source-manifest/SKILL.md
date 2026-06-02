---
name: aidp-source-manifest
description: Validate and build the AIDP `migration_manifest` contract for medallion workloads, including `process_date` and `load_mode` overrides, source-discovery policy, live-vs-fallback source selection, master catalog normalization, and source manifest report generation. Use when Codex needs to inspect or repair `aidp/config/migration_manifest.json`, explain how runtime overrides resolve, dry-run source coverage before deployment, or prepare the uploaded source manifest for AIDP Workbench execution.
---

# AIDP Source Manifest

## Overview

Use this skill when the user is shaping or validating the AIDP manifest layer before any live deployment. Treat the manifest as the source of truth for source discovery, process-date scoping, medallion targets, catalog naming, control-layer registration, replay policy, and uploaded source manifest generation.

## Prerequisites

- `aidp/config/migration_manifest.json` or an explicit `--manifest` path is required.
- `.source/` is recommended when the manifest is being derived from source evidence, but not required for manifest-only inspection.
- `.oci/` is not required for dry-run manifest inspection and shaping.

## Workflow

1. Read `references/manifest-contract.md` before changing manifest structure or explaining runtime behavior.
2. Run `uv run codex-oci aidp manifest inspect --manifest <path>` when you need a portable resolved summary before editing or explaining the contract.
3. Validate the contract first: confirm the manifest has the expected AIDP identity, source-discovery, reference-truth, target-layer, master-catalog, control-state, validation, and write-optimization sections.
4. Resolve runtime overrides next: treat `AIDP_PROCESS_DATE` and `AIDP_LOAD_MODE` as runtime state unless the user explicitly wants persistent manifest edits.
5. Dry-run source discovery before any deploy flow: explain which source systems are active, whether fallback is allowed, which bucket or pattern will win, and whether the manifest summary exposes the expected `control_layer`, `reprocess_strategy`, `validation`, and `write_optimization` sections.
6. Keep the uploaded source manifest and the live bucket inventory aligned. If they diverge, or if stage or control tables are missing from the normalized catalog contract, fix the manifest logic first instead of papering over the mismatch in downstream steps.

## Rules

- Prefer live-source selection over historical fallback unless the manifest policy explicitly allows fallback.
- Preserve the audited reference scope. If the active reference truth is PGW-only, do not silently expand to SGSN or SGW.
- Keep one `process_date` per execution. Do not broaden to multi-date runs unless the user is deliberately redesigning the contract.
- Treat `crl` as the logical control schema key. If the physical schema name is `crt` or `control`, document that as an alias rather than inventing a second logical control layer.
- Do not print secrets from `.oci/` or expand full private OCIDs in summaries.
- Write reports under `aidp/reports/` when a build or validation flow asks for an output file.

## Outputs

- A validated understanding of the manifest contract and runtime overrides.
- A portable summary of stage tables, control tables, replay policy, validation metrics, and per-layer write guidance.
- A recommendation on whether the current source selection is safe for deployment.
- If requested, a source-manifest build or dry-run summary ready for AIDP deployment steps.
