# Manifest Contract

## Core identity

- `region` and `aidp_ocid` identify the AIDP control plane target.
- `reference_dataflow_runs` and `reference_truth` define the audited OCI reference scope.
- `process_date`, `processing_days`, and `load_mode` define the runtime slice.

## Runtime overrides

- `AIDP_PROCESS_DATE` overrides `process_date` and the effective `processing_days`.
- `AIDP_LOAD_MODE` overrides the effective `load_mode`.
- The runtime layer resolves `${process_label}` and `${primary_process_date}` after overrides are applied.
- Keep overrides ephemeral unless the user explicitly wants to edit the manifest.

## Source discovery

- `source_prefixes` describe the preferred live folders.
- `historical_source_prefixes` describe fallback candidates.
- `source_discovery.selection_mode` controls candidate selection behavior.
- `source_discovery.allow_fallback` is the explicit guardrail for historical fallback.
- `allowed_source_buckets` and `disallowed_source_buckets` constrain safe source selection.
- Explicit `source_discovery.candidates` override the default live-then-historical pattern.

## Reference truth

- `active_source_systems` define the intended reference scope for validation and acceptance.
- `disabled_source_systems` are still relevant for coverage checks when live data exists outside the active scope.
- `stage_map` ties audited Data Flow runs to the bronze, silver, and gold reference stages.

## Data layout

- `target_layer_uris` describe bronze, silver, gold, and control outputs.
- `ref_table_uris` and `lookup_paths` support reference-table resolution.
- `source_manifest_uri` is where the built source manifest is uploaded.
- `compat_export_uri` is the compatibility export location when used.
- `master_catalog` defines canonical catalog, schema, and table names.

## Control and state model

- Keep the logical control schema key as `crl` in the portable contract.
- Resolve the physical control schema name through `master_catalog.schemas`; `crt` is the default physical name and `control` is a supported alias.
- When batch and streaming coexist, `target_layer_uris` should cover `bronze_stream_stage`, `file_state`, `run_state`, `output_refresh`, `stream_run_state`, and `stream_batch_state`.
- `master_catalog.tables` should register those stage and control entities explicitly instead of treating them as incidental runtime artifacts.

## Reprocess strategy

- `reprocess_strategy.mode` defines the replay policy.
- `identity_columns` describe the identity used to decide whether an input is the same physical file.
- `business_key_columns` describe the downstream business identity that matters for gold reconciliation.
- `gold_window_days`, `on_same_identity`, `on_changed_identity`, and `on_forced_replay` define how far reprocessing reaches and which replay paths are allowed.

## Validation

- `validation.reference_kind` names the reference-comparison strategy.
- `validation.compare_columns` lists the business metrics that must survive batch-versus-streaming parity checks and runtime validation.

## Write optimization

- `write_optimization` is a per-layer contract.
- Capture `target_file_size_mb`, `estimated_output_ratio`, `min_partitions`, `max_partitions`, and `min_compaction_file_count` only when they materially drive runtime behavior.
- Keep the optimization guidance portable. Record layer intent, not customer-specific tuning folklore.

## Streaming runtime

- `streaming.checkpoint_base_uri` is the durable checkpoint anchor.
- `streaming.workspace_paths.checkpoints`, `streaming.local_fs_paths.checkpoints`, and `streaming.volumes.checkpoints` describe the expected checkpoint mounts or folders.
- `streaming.jobs` should keep stable bronze, silver, bt, and aggregate-finalize job identities.
- `streaming.defaults` belongs in the contract when trigger interval, checkpoint suffix, or file-per-trigger limits are required to interpret behavior.

## Curated operational defaults

- One `process_date` per execution.
- Prefer the audited live source scope when one exists.
- Treat fallback to historical storage as an exception that should be visible in reports.
- Treat stage and control tables as first-class outputs alongside bronze, silver, and gold.
- Require bt backlog zero across consecutive windows using both `file_state` and `output_refresh` before stopping streaming workers.
- Require aggregate backlog zero after finalize before declaring the streaming lane complete.
- Persist build and validation outputs under `aidp/reports/`.
