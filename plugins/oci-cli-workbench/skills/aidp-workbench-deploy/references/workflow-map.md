# Workflow Map

## Canonical notebook layout

- `40_ref/05_ref_lk_antena_cgi.ipynb`
- `40_ref/10_ref_lk_rating_group.ipynb`
- `40_ref/15_ref_lk_trf_tipo_tecnologia.ipynb`
- `40_ref/20_ref_lk_status_trf.ipynb`
- `10_bronze/10_bronze_ingest.ipynb`
- `20_silver/20_silver_transform.ipynb`
- `30_gold/30_gold_aggregate.ipynb`
- `30_gold/35_query_reporte_trafico_datos.ipynb`

## Streaming notebook layout

- `10_bronze/14_bronze_ingest_stream.ipynb`
- `20_silver/24_silver_transform_stream_finalize.ipynb`
- `30_gold/33_gold_bt_stream_finalize.ipynb`
- `30_gold/34_gold_agregate_stream_finalize.ipynb`

## Structure-refresh notebook layout

- `98_jobs/95_reset_trafico_process_date.ipynb`
- `98_jobs/96_refresh_mdln_structures.ipynb`
- `98_jobs/97_refresh_exam_new_col_structures.ipynb`

## Job families

- Ref workflow: the four reference notebooks in sequence.
- Trafico batch workflow: bronze -> silver -> gold aggregate.
- Streaming jobs: separate bronze, silver, bt, and agg finalize jobs.
- Structure-refresh jobs: `mdln`, `reset`, and optional demo refresh jobs.

## Control-state artifacts

- Stage table: `bronze_stream_stage`.
- Core control tables: `file_state`, `run_state`, and `output_refresh`.
- Streaming state tables: `stream_run_state` and `stream_batch_state`.
- Checkpoint artifacts: `checkpoint_base_uri`, `workspace_paths.checkpoints`, `local_fs_paths.checkpoints`, and `volumes.checkpoints`.
- Keep the streaming worker job identities stable so recovery and acceptance flows can reason about them deterministically.

## Canonical deploy sequence

1. Render notebooks from the manifest and runtime overrides.
2. Ensure workspace folders.
3. Ensure the chosen compute or runtime context.
4. Prefer `uv run codex-oci aidp compute ensure --manifest ... --compute-profile batch|streaming` when the wrapper can create or reattach the compute safely.
5. Ensure the checkpoint and control-state expectations match the manifest.
6. Upload notebooks.
7. Replace the relevant jobs while preserving stable worker names.
8. Persist a report under `aidp/reports/`.
9. Optionally launch selected workflows.
