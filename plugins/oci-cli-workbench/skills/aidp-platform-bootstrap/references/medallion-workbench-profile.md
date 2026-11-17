# Medallion Workbench Profile

## Platform bootstrap sequence

1. Confirm the target compartment and naming.
2. Review `uv run codex-oci aidp platforms create --dry-run ...`.
3. Create the AIDP platform with an explicit default workspace name.
4. Anchor the workspace to the canonical medallion folder layout before uploading notebooks or defining jobs.

## Canonical workspace folders

- `40_ref`
- `10_bronze`
- `20_silver`
- `30_gold`
- `98_jobs`

## Canonical workflow families

- Reference: four lookup notebooks under `40_ref`.
- Batch: bronze ingest, silver transform, and gold aggregate.
- Streaming: bronze, silver finalize, bt finalize, and aggregate finalize as separate workers or jobs.
- Control and refresh: reset plus structure-refresh notebooks under `98_jobs`.

## Control-layer expectations

- Keep the logical control schema key as `crl` in the portable contract.
- Resolve the physical control schema name as `crt` by default or `control` when the target layout requires that alias.
- Keep `file_state`, `run_state`, `output_refresh`, `stream_run_state`, and `stream_batch_state` in the portable baseline.
- Keep `bronze_stream_stage` whenever streaming and batch must coexist over the same medallion layout.
- Treat those tables as part of the medallion contract, not as optional diagnostics.
- Preserve reset and refresh workflows so batch and streaming can coexist without state drift.

## Coexistence rules

- Use separate compute profiles for batch and streaming work.
- Do not mix long-running streaming workers into the same operational lane as ref and batch jobs.
- Require bt backlog zero across consecutive windows using `file_state` and `output_refresh` before stopping stream workers.
- Keep backlog evidence and snapshot comparisons when validating batch versus streaming parity.
- Prefer layout stability over ad hoc experimentation once the shared blueprint is adopted.
