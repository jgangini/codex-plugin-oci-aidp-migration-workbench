---
name: aidp-platform-bootstrap
description: Bootstrap a new AIDP platform and align it with the repo's portable medallion blueprint, including explicit platform creation, default workspace naming, control-layer expectations, and batch-versus-streaming coexistence boundaries. Use when Codex needs to start from no AIDP platform, validate the target layout before deployment, or explain the minimum reusable AIDP baseline for this plugin.
---

# AIDP Platform Bootstrap

## Overview

Use this skill when the user needs to stand up or plan a new AIDP platform before notebook sync, job deployment, or runtime validation. This skill is about the reusable AIDP baseline for the plugin, not customer-specific implementation details.

## Prerequisites

- `.oci/` is required for live AIDP platform inspection or creation.
- `.source/` is optional and only needed when the platform shape is being driven from source evidence.

## Workflow

1. Read `references/medallion-workbench-profile.md` before proposing names, workspace layout, or job families.
2. Inspect the manifest and tenancy context first. If a manifest already contains `aidp_ocid`, treat new platform creation as an explicit drift decision.
3. Use `uv run codex-oci aidp platforms create --dry-run ...` to review the planned OCI CLI call before any live mutation.
4. Use `uv run codex-oci aidp blueprint medallion` to anchor the workspace folders, stage tables, control tables, control-schema defaults, and coexistence rules.
5. Only after the platform exists should follow-on work move into manifest shaping, workspace deploy, validation, acceptance, or recovery flows.

## Rules

- Keep platform creation opt-in. Dry-run first unless the user clearly wants the live create.
- Require explicit `--display-name` and `--default-workspace-name`.
- Keep the portable baseline centered on OCI CLI and AIDP only. Do not pull OAC-specific handoff steps into this plugin.
- Treat control-layer tables, stage tables, and streaming coexistence as first-class design inputs, not late additions.

## Outputs

- A safe create plan or a completed AIDP platform creation result.
- A portable medallion workspace recommendation for the new platform.
- A clear handoff into manifest, deploy, validation, or acceptance work.
