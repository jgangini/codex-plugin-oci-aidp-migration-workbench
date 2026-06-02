---
name: aidp-batch-stream-acceptance
description: Run or review the state-driven mdln batch + stream acceptance workflow, including cancellation of active runs, refresh and ref preparation, full baselines, reset, streaming worker startup, backlog convergence, finalize, and snapshot comparison. Use when Codex needs to prove parity between batch and streaming behavior, investigate acceptance drift, or execute the curated acceptance playbook against AIDP Workbench.
---

# AIDP Batch Stream Acceptance

## Overview

Use this skill for the heaviest end-to-end validation flow in the AIDP package. It is the place for proving that the streaming path converges to the same business result as the canonical batch baseline while respecting the control-layer state model.

## Prerequisites

- `.oci/` is required because this workflow touches live AIDP runs, jobs, and state.
- `.source/` is optional and only needed when the acceptance write-up must tie results back to the original source evidence.

## Workflow

1. Read `references/acceptance-playbook.md` before touching a live acceptance run.
2. Confirm that the user really wants a live acceptance execution. This flow cancels runs, deploys or launches jobs, and waits on backlog state.
3. Build or review the batch baseline first.
4. Reset the target process date before starting streaming workers.
5. Start workers in the expected order, wait for bt backlog convergence across consecutive windows using `file_state` and `output_refresh`, stop them cleanly, run finalize, wait for aggregate backlog zero, and compare snapshots.

## Rules

- Keep baseline and candidate evidence separate.
- Persist every intermediate report. Acceptance is not reproducible without the snapshots, backlog windows, and output-refresh evidence.
- Do not skip the cancellation and refresh steps when the live environment is dirty.
- Treat non-terminal or inconsistent backlog windows as a reason to keep monitoring rather than declaring success early.
- A single zero snapshot is insufficient. Require the curated consecutive zero-window rule before stopping workers.

## Success condition

Acceptance succeeds only when the final snapshot comparison is equivalent, the bt backlog stays at zero for the required consecutive window, and aggregate backlog reaches zero after finalize.
