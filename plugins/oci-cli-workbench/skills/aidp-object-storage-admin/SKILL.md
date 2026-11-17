---
name: aidp-object-storage-admin
description: Manage the AIDP Object Storage layer through the local `codex-oci` wrapper, including manifest-aware bucket inspection, bucket create/update/delete, managed-prefix uploads, control-artifact uploads, and safe object cleanup. Use when Codex needs to provision medallion buckets, inspect customer source buckets, upload source manifests or lookup artifacts, or explain the storage boundary for AIDP execution.
---

# AIDP Object Storage Admin

## Overview

Use this skill when the task is about Object Storage as part of the AIDP operating model. Treat storage as the execution substrate for sources, medallion layers, control tables, checkpoints, lookups, and compatibility exports.

## Prerequisites

- `.oci/` is required for live bucket or object inspection and mutation.
- `.source/` is not required for storage administration.
- A manifest is required for manifest-backed bucket or object mutations.

## Workflow

1. Read `references/storage-admin.md` before changing storage state or explaining the storage boundary.
2. Start with `uv run codex-oci aidp storage inspect --manifest <path>` to understand managed buckets, read-only source buckets, and location keys.
3. Use `uv run codex-oci aidp storage buckets ...` for bucket-level operations and `uv run codex-oci aidp storage objects ...` for prefix or object-level operations.
4. Use dry-run first for bucket create/update/delete and for uploads that touch shared medallion prefixes.
5. Prefer manifest-backed `--location-key` values over ad hoc URIs so the operation stays aligned with the portable AIDP contract.

## Rules

- Treat customer source buckets and lookup buckets as read-only unless the user explicitly changes the storage contract.
- Treat source-backed streaming volumes as read-only unless the manifest explicitly marks them with `managed: true`.
- Keep destructive actions strongly confirmed. Bucket deletes require exact bucket-name confirmation, and object deletes require exact object-name confirmation.
- Keep bucket create, update, and delete operations inside manifest-managed AIDP buckets.
- Prefer `source-manifest`, `target:*`, `ref:*`, `compat-export`, and streaming checkpoint locations for managed writes.
- Do not bypass the wrapper with raw `oci os ...` commands when `codex-oci aidp storage ...` covers the operation.
- Keep reports and outputs under `aidp/reports/` when a flow needs persisted evidence.

## Outputs

- A clear mapping of AIDP managed buckets vs read-only source buckets.
- Safe bucket plans or executed bucket mutations.
- Safe object or bulk-upload plans or executed uploads into managed AIDP prefixes.
- A short explanation of how the storage change fits the AIDP manifest and medallion boundary.
