# Reproducible validation contract

Use this contract with [execution diagnostics](execution-diagnostics.md) and the [Spark/Volume lessons](../../aidp-ops-recovery/references/diagnostic-lessons.md). Tools below use only Python's standard library, consume explicitly selected local exports, and never call OCI, change compute, deploy a job or send a message. The calling project's authorization, scope and budget remain authoritative.

## Decode actual task output

From this skill directory:

```text
python scripts/decode_task_output.py task-output.json --marker AIDP_DIAGNOSTIC:: --output decoded-output.json
```

Supported shapes: OCI response envelopes, AIDP TEXT_PLAIN / NOTEBOOK / APPLICATION_JSON output blocks, notebook cells with outputs, and kernel exports with an outputs list. Notebook source and raw parameter values are never inspected. Text strings and text-fragment arrays are accepted. Concatenated marked JSON objects are decoded without assuming line boundaries. Text is not implicitly unescaped a second time, which could corrupt literal paths.

The output contains marked events, output length, the specific command-failure signature signal, and a coverage note. Events can contain private case values; this is a restricted local artifact, not a redaction tool. Unknown schemas, unsupported channels, excessive nesting, malformed/truncated event JSON and failed HTTP envelopes are rejected. No events is not proof of success. Preserve raw exports and separately inspect task state/errorTrace and Spark progress.

## Assess comparable runs

```text
python scripts/assess_repeatability.py series.json --files 100 --max-cv 0.10 --output repeatability.json
```

`--files` is the case's agreed full-load file count, not a sample or a built-in AIDP limit. `series.json` is a chronological JSON list of reviewed per-attempt evidence objects. All fields below are required for qualification except the two validation booleans, which can be null or absent while pending:

| Field | Contract |
| --- | --- |
| attempt | Unique attempt identity; the output hashes it. |
| sequence | Nonnegative integer from the complete campaign workflow ledger; do not renumber after dropping failed or different-version runs. |
| status | SUCCESS for qualification, with every required workflow task complete. |
| repair_count / manual_interventions | Integer zero; establish from API repair history and the chronological log. Missing values are unknown. |
| files | Exact selected full-load file count confirmed against the immutable manifest. |
| workflow_seconds | Positive finite elapsed workflow time, excluding startup; do not sum overlapping tasks. |
| cold_start | Boolean; the last three samples must be true, false, true. |
| code_sha256 | SHA-256 of the deterministic inventory of source/dependency file paths and content hashes. |
| definition_sha256 | Frozen workflow graph/parameters definition fingerprint; exclude volatile API response metadata. |
| runtime_configuration_sha256 | Effective runtime/compute settings, including worker capacity, driver, installed dependencies and SparkContext configuration. |
| task_configuration_sha256 | Effective task Spark SQL and writer settings; monitor-session defaults alone are insufficient. |
| input_manifest_sha256 | Frozen data/catalog inventory and historical initial-state identity. |
| parameters_sha256 | Canonical business-parameter hash including process date. Exclude only per-attempt IDs/output roots and the recorded run-start macro. |
| validation_passed | true only after required schemas, counts, keys, duplicates, rejects, aggregates and bidirectional row reconciliation pass; false for a mismatch, null when incomplete. |
| operational_validation_passed | Reviewed case-specific operational verdict with coverage. Do not derive it simply from absence/presence of ERROR messages. |

All fingerprints must be complete lowercase SHA-256 strings. Supply all attempts from the campaign in order; the tool evaluates only the last three and refuses discontinuous sequence numbers. It cannot discover attempts deliberately omitted from an input file, verify remote hashes, or independently authenticate the supplied flags. Keep evidence paths and the ledger next to the exported series.

The report separates:

- `execution_stable`: three distinct successful unrepaired full runs, identical fingerprints, consecutive sequence, cold/warm/cold and population CV within the selected limit.
- `correctness`: PASS, FAIL or PENDING, independent of duration.
- `operational_validation`: PASS, FAIL or PENDING, independent of row equivalence.
- `accepted`: true only when execution is stable and both independent verdicts pass.

A previously completed diagnostic run may qualify without rewriting its launch flag if all technical evidence is preserved; record the decision before subsequent samples. Similar durations from different versions do not form this series. No fixed two-hour cutoff is imposed. Record the user's current duration target separately and report observed minimum/median/maximum; do not turn three samples into an SLA.

Both CLIs create a new output file exclusively, never overwrite inputs/outputs, and return exit code 2 for invalid input or file errors. Exit code 0 means the assessment was produced, not that its verdict passed. The output parent directory must already exist. Use bounded exports; these utilities load each selected JSON file in memory.

## Ordered SQL and result reconciliation

Create a separate versioned `99_report` directory when the project needs repeatable SQL review. Use ordered names and comments that identify the frozen attempt, input views, query purpose, expected invariant and whether the query performs a full scan:

1. `a_inventory.sql`: schemas and coverage of expected datasets/partitions, not just existing directories.
2. `b_counts.sql`: stage counts and rejected records, with zero/empty branches handled explicitly.
3. `c_business_totals.sql`: business measures, direction/category branches and historical state; preserve precision and null semantics.
4. `d_keys_duplicates.sql`: original business keys and duplicate multiplicity, not invented surrogate keys.
5. `e_bidirectional_diff.sql`: aligned-column EXCEPT ALL in both directions, then bounded profiles of unmatched keys and changed non-key columns.

Bind only registered frozen input/output roots or verified read-only temporary views. Do not embed production paths, concatenate unvalidated identifiers, write tables, or clean directories in report queries. Keep reporting time separate from the measured workflow and include it in cost. Test empty input, category-only input, duplicates across producer batches, skew, failed producer blocking and append-output reuse. Equal totals are supporting evidence, not a substitute for full-row comparison.

## Offline regression checks

```text
python scripts/test_summarize_aidp_runs.py
python scripts/test_diagnostic_evidence.py
```

These synthetic checks cover the reusable helpers, not a live AIDP certification. Live source/target correctness and performance must still be established in the authorized project. No customer fixtures, production credentials or customer SQL are shipped.
