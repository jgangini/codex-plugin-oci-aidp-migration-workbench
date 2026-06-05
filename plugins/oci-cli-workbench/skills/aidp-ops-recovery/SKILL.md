---
name: aidp-ops-recovery
description: Recover, cancel, clean up, or monitor AIDP operations, including active job-run cancellation, isolated runtime reset, compute cleanup, safe platform-retirement boundaries, and optional Slack notification through the existing local automation skill when the user explicitly requests it. Use when Codex needs to intervene in stuck or long-running AIDP flows, clean the environment before redeploying, or watch a live migration safely.
---

# AIDP Ops Recovery

## Overview

Use this skill when the environment is already in motion and needs operator-style intervention. Diagnose first, then choose the smallest safe recovery step.

## Prerequisites

- `.oci/` is required because recovery and monitoring target live OCI and AIDP resources.
- `.source/` is not required for recovery work.

## Workflow

1. Read `references/ops-recovery.md` before mutating live AIDP resources.
2. Start with read-only status gathering whenever possible.
3. Cancel active job runs before deleting or resetting runtimes, computes, or downstream state.
4. Prefer `uv run codex-oci aidp compute stop|delete|cleanup` for compute lifecycle work when the wrapper exposes the needed action.
5. Keep AIDP platform retirement outside automated wrapper cleanup. If the user intends to retire a platform, document the governance approval, impact check, and manual operator action separately from plugin cleanup.
6. Use cleanup flows only after verifying the resource is not still the intended active target.
7. Trigger Slack or external notifications only when the user explicitly asks for them.

## Rules

- Prefer the least destructive recovery step that unblocks the workflow.
- Persist status and cleanup reports under `aidp/reports/`.
- Explain exactly what is being cancelled or cleaned before doing it.
- Keep `aidp compute cleanup` read-only until the user explicitly wants `--apply`.
- Do not automate AIDP platform deletion from this plugin; platform retirement can affect critical shared services and must remain an explicit operator-governed action.
- Keep recovery and redeploy flows separate in the write-up so the user can audit what changed.
