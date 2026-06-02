---
name: aidp-workbench-deploy
description: Render notebooks, sync them into AIDP Workbench, ensure runtime context, and create or run ref, batch, streaming, and structure-refresh jobs for the medallion workflow. Use when Codex needs to prepare or repair an AIDP workspace layout, upload notebooks, replace jobs, launch selected workflows, or explain how the AIDP deploy path is mapped into workspaces, tasks, and reports.
---

# AIDP Workbench Deploy

## Overview

Use this skill for the live deployment path from local notebook rendering to AIDP workspace and job orchestration. Treat workspace folders, jobs, job runs, compute or runtime context, stage tables, and checkpoint artifacts as live tenancy resources.

## Prerequisites

- `.oci/` is required because this skill operates on live OCI and AIDP resources.
- `.source/` is optional; use it when the deploy is still being shaped from source evidence instead of an already-stable manifest.

## Workflow

1. Read `references/workflow-map.md` before changing notebook layout, job names, or deploy sequencing.
2. Validate the manifest and runtime context first: region, AIDP target, workspace name, process date, load mode, and required runtime ids.
3. Use `uv run codex-oci aidp compute ensure --manifest ... --compute-profile batch|streaming` whenever the compute context must be created or reattached through the local wrapper.
4. Render notebooks locally before touching the workspace.
5. Sync notebooks into the correct workspace layout and ensure the target folders, checkpoint folders, and volume expectations exist for the chosen workflow.
6. Replace jobs intentionally. Keep job names stable unless the user explicitly wants a rename, especially for bronze, silver, bt, and aggregate-finalize streaming workers.
7. Launch workflows only when the user explicitly asks for a live run. Creating or updating jobs is already a mutating step; running them is a second, higher-risk step.

## Flow Families

- Ref + batch deploy: render core medallion notebooks, upload them, and create or run the `ref` and `trafico` workflows.
- Streaming deploy: upload the streaming notebooks, preserve `bronze_stream_stage` and control-state expectations, and manage the bronze, silver, bt, and agg jobs separately.
- Structure refresh: handle `reset` and structure-refresh notebooks and jobs without mixing them into the regular batch path.
- Demo or experiment flows: keep them isolated from the canonical production-like medallion workflow unless the user explicitly wants them.

## Rules

- Keep every live mutation opt-in.
- Persist report JSON outputs so later validation and ops flows can reuse them.
- Do not hide workspace, job, or cluster replacement from the user.
- Prefer `uv run codex-oci aidp compute ...` for compute inspection and lifecycle actions instead of ad hoc raw requests when the wrapper already exposes the needed operation.
- Prefer the canonical medallion layout from the repo over ad hoc workspace folder structures.
- Keep checkpoint, stage-table, and control-table assumptions aligned with the manifest before declaring a deploy healthy.
