# Storage Admin

## Canonical commands

- `uv run codex-oci aidp storage inspect --manifest <path>`
- `uv run codex-oci aidp storage namespace`
- `uv run codex-oci aidp storage buckets list --manifest <path>`
- `uv run codex-oci aidp storage buckets get --manifest <path> --bucket-key bronze`
- `uv run codex-oci aidp storage buckets create --manifest <path> --bucket-key bronze --dry-run`
- `uv run codex-oci aidp storage buckets update --manifest <path> --bucket-key bronze --versioning Enabled --dry-run`
- `uv run codex-oci aidp storage buckets delete --manifest <path> --bucket-key bronze --confirm-name <bucket-name> --dry-run`
- `uv run codex-oci aidp storage objects list --manifest <path> --location-key target:bronze`
- `uv run codex-oci aidp storage objects put --manifest <path> --location-key source-manifest --file .\aidp\reports\source_manifest.json --dry-run`
- `uv run codex-oci aidp storage objects bulk-upload --manifest <path> --location-key ref:lk_demo --src-dir .\lookups --dry-run`
- `uv run codex-oci aidp storage objects delete --manifest <path> --location-key target:bronze --object-name demo.parquet --confirm-object-name demo.parquet --dry-run`

## Location key model

- `source-manifest`: fixed object URI for the uploaded source manifest.
- `compat-export`: compatibility export prefix.
- `target:<key>`: medallion and control prefixes from `target_layer_uris`.
- `ref:<key>`: reference-table prefixes from `ref_table_uris`.
- `lookup:<key>`: lookup object paths from `lookup_paths`. Treat as read-only unless the storage contract changes.
- `source:<system>`: first manifest candidate for a source system. Treat as read-only.
- `streaming:checkpoint-base`: checkpoint base prefix for streaming state.
- `streaming-volume:<key>`: OCI-backed streaming volume location when one is declared. It is mutable only when that volume is marked with `managed: true`.

## Guardrails

- Managed writes should stay inside buckets declared by `bucket_names` or inferred from the manifest's managed targets.
- Source and lookup buckets are inspection-only by default.
- Bucket create, update, and delete stay inside manifest-managed buckets.
- Source-backed streaming volumes are inspection-only unless the manifest explicitly promotes them to managed storage.
- Prefer `--location-key` for standard AIDP paths. Use explicit URIs only when the manifest does not already model the destination.
- Use dry-run before mutating bucket settings or shared storage prefixes.

## Practical defaults

- Bucket create defaults: `NoPublicAccess`, `Standard`, `Disabled` versioning.
- Single-file uploads default to no-overwrite unless `--overwrite` is explicit.
- Bulk uploads default to no-overwrite unless `--overwrite` is explicit.
- Delete flows require exact-name confirmation.
