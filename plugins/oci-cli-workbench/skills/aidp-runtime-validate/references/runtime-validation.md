# Runtime Validation

## Evidence sources

- Uploaded source manifest summary.
- Live source scope built from the current manifest.
- Customer bucket inventory by prefix.
- Target layers: bronze, bronze stream stage when present, silver, gold detail, gold aggregate, control, and compatibility export.
- Control tables: `file_state`, `run_state`, `output_refresh`, `stream_run_state`, and `stream_batch_state`.
- Bronze parquet schema probe for generic columns like `c0`, `c1`, and similar artifacts.
- Master catalog table details from the AIDP or catalog surface.
- Current job and job-run status, plus checkpoint or worker-state context when the streaming lane is active.

## Core questions

- Does the uploaded source manifest match the active live inventory?
- Did the run stay inside the intended reference scope?
- Did bronze and the optional stage layer materialize with a clean schema and expected file identity?
- Did silver, gold, and control layers progress as expected?
- Do `file_state` and `output_refresh` tell a consistent backlog story?
- Do `stream_run_state` and `stream_batch_state` reflect the expected worker progression when streaming is enabled?
- Does the master catalog reflect the medallion layout that the manifest expects?

## Important distinctions

- `reference_scope` is not the same as `customer_bucket_inventory`.
- `processing_complete` is not the same as `coverage_ready_for_reference_scope`.
- `file_state.pending_silver_count` and `file_state.pending_bt_count` are not the same as `output_refresh.pending_bt_outputs` and `output_refresh.pending_agg_outputs`.
- A single zero snapshot is not the same as the required consecutive zero-window evidence for bt backlog convergence.
- `stream_run_state` and `stream_batch_state` explain worker progression, but they do not replace materialized layer evidence.
- A run can be structurally healthy but still be incomplete if the backlog is non-zero.

## Default output style

- Start with control-plane or job status and the observed stage.
- Summarize control-layer readiness and backlog signals next.
- Then explain the main mismatch, if any, using source inventory, layer evidence, schema validation, worker-state evidence, and catalog state.
