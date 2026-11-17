# Catalog Governance

## Main governance layers

- Taxonomy and glossary terms for the medallion model.
- Data asset, entities, and attributes for tables and layers.
- Base lineage connecting the medallion entities.

## Required inputs

- `catalog-id`
- `glossary-key` for object and lineage provisioning
- `profile`
- `owner` when the taxonomy flow needs an explicit visible owner

## Operational guidance

- Apply taxonomy before object-level lineage work.
- Keep medallion schemas and control tables consistent with the manifest.
- Register `bronze_stream_stage`, `file_state`, `run_state`, `output_refresh`, `stream_run_state`, and `stream_batch_state` as first-class catalog entities when the workload includes streaming coexistence.
- Keep the logical control schema key `crl` aligned with the resolved physical schema name, whether the target catalog uses `crt` or `control`.
- Persist the taxonomy and object provisioning reports under `aidp/reports/`.
