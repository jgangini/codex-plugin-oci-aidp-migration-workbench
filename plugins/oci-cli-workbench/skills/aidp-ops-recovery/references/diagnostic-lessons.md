# Evidence-driven Spark and Volume diagnosis

These checks consolidate an isolated AIDP Spark 3.5.0 / Hadoop 3.3.4 investigation. They are scoped observations and reusable procedures, not claims that every AIDP region or release has the same behavior. Verify the deployed runtime and official contracts before acting. No customer scripts, run IDs, credentials, or data are included.

## Preserve the experiment

- Export originals and record hashes before and after authorized operations. Copy notebooks, Python tasks and dependencies into each version; redirect imports to that version and preserve task type.
- A suffix is not ownership. Mutations require registered resource IDs, matching ownership metadata and containment in registered workspace/storage roots. Reject parent traversal, encoded paths, missing parameters and reused append destinations.
- Freeze a version after its first run. Changes to code, graph, capacity, concurrency or Spark configuration require another version with an explicit parent. Building from a parent must copy all configuration explicitly; source inheritance alone does not preserve Spark settings.
- Freeze the file manifest, bytes, identities, catalogs, process date and historical initial state. Retain failed/cancelled attempts and fresh outputs per attempt. A small probe cannot certify full-load stability.
- Record hypothesis, planned change, version hashes, effective settings, run/task/command/context/application/request IDs, stage timings, evidence coverage, costs and decision in an append-only chronological log. Corrections are new entries.
- Keep only the agreed number of laboratory computes active. Count startup, validation, failures, idle time and shutdown in the budget; include provisioned capacity and pricing date in cost estimates. Local timeouts do not stop cloud charges. Only explicit user authorization extends the ledger.

## Classify the wait before changing capacity

| Evidence | Mechanism to investigate | Discriminating measurement |
| --- | --- | --- |
| Jobs finish but DataFrame write has not returned | Driver-side publication/commit | SQL commit time; driver threads in FileOutputCommitter and filesystem rename/listStatus; output file count |
| Write returned but Observation.get has not returned | Metrics/listener delivery | Shared queue size, cumulative drops, listener timings, SQL execution IDs and driver stacks |
| Few long writers and many empty tasks | Skew or correlated partition hashes | Per-task shuffle/output, nonempty writer count, spill and hash distribution within each source bucket |
| Host memory pressure or OOMKilled | Container memory, possibly outside JVM heap | RSS, JVM/Python/native/cache split, executor replacement, failed attempts and application lifetime |
| Command/stage tracking errors with complete Spark stages | Observability mapping or context issue | Correlate IDs and timestamps; distinguish missing tracking from actual task failure and row differences |
| Quiet stdout but progressing stages or commits | Monitoring silence | Task progress and storage publication; do not cancel solely for unchanged text |

Measure listing, reading, materialization, transformation, writing, commit and metrics waits separately. Do not sum overlapping stage durations into workflow wall time. Zero Volume input-byte counters do not prove zero reads. Record metric interval, aggregation, executor dimensions and app lifetime; an instantaneous empty queue does not erase earlier drops.

## Storage and paths

- Compare POSIX enumeration, Hadoop recursive listFiles, per-directory listStatus traversal and Spark inputFiles against the same independently frozen manifest. One managed-Volume investigation found incomplete results from the first two interfaces while listStatus traversal matched the manifest; the external source Volume did not reproduce that discrepancy. Do not generalize one interface failure to all reads or all Volumes.
- Traverse directories with a bounded worklist and track completeness. Verify that a reader selected exactly the intended file set before interpreting row counts. Do not enable ignoreMissingFiles/ignoreCorruptFiles to conceal omissions.
- For mounted local paths, compare actual basePath and leaf URI forms. Qualifying a path may still preserve the mismatch in a service filesystem; use the same verified scheme for both. Never convert remote oci:/hdfs: paths to file: as a generic fix. Validate path components, not string prefixes.
- Test mkdirs on an existing owned directory before changing committers. Hadoop specifies success for that case. In the observed runtime, commit algorithm 2 failed with VolumeFileAlreadyExistsException from mkdirs, reproduced even sequentially. Retain the validated algorithm for that environment; do not suppress the exception or recommend algorithm 2 universally.
- Direct Object Storage is a separate compatibility experiment. Physical keys may omit compression extensions and change filename-derived fields. Preserve codec detection, logical filename semantics, schema and exact selected objects.

## Writes, partitions and memory

- Reduce excessive small files only after measuring commit latency. Preserve formats and business partition keys. Compare the extra redistribution cost with downstream reading/commit savings.
- A writer salt must be independent of the upstream bucket hash. Reusing the same key/hash/modulus inside an already partitioned bucket can make the salt constant. Test the conditional distribution, not just the global hash distribution.
- One observed Volume writer buffered output through ByteArrayOutputStream and reached the Java array-size ceiling. This is evidence about that writer implementation, not a universal two-gigabyte Parquet limit. A measured maxRecordsPerFile can mitigate growth; it does not guarantee a byte bound for variable-width rows. Check actual largest files and full-row equivalence.
- A Python one-row control DataFrame may inherit the cluster's large default parallelism. For a typed literal marker, evaluate spark.range(1, numPartitions=1).select(...) to avoid unnecessary Python workers/tasks. Verify schema, write mode, the consumer and duplicate-output rejection.
- Release only the DataFrames persisted by the task, including exception paths, and inspect remaining RDDs before a later run. Do not clear every cache on a shared cluster. A successful retry after executor OOM is not evidence that the OOM mechanism was fixed.
- Size broadcast joins from measured catalog size, not naming conventions. Preserve predicate semantics, including prefix/range matches. Review executed plans, AQE, shuffle and spill before changing partition counts or capacity.

## Orchestration, Observation and lineage

- Consumers reading a shared output directory must wait for all contributing ingestions. Pairwise WorkN -> IngestN is insufficient for that layout. Exercise a producer failure and verify consumers cannot run early. Workflow maxConcurrentRuns=1 is separate from internal task concurrency.
- Use a unique Observation name per instance, including loop iterations. Repeated names in one tested SparkSession reused the first observation's metrics; separate sessions did not show that result. Name uniqueness fixes attribution, not every wait.
- Compare original instrumentation, unique names and a variant without observe/get with independent reconciliation. Never use -1 or an unavailable metric as a successful count.
- The observed shared listener waited on filesystem metadata while building lineage. Increasing queue capacity removed observed drops in one run, but tracking errors persisted. Treat it as a measured mitigation, not proof that all command errors are caused by dropped events. Capture cumulative deltas from the same app and verify the effective SparkContext configuration after an authorized restart.
- Directory reading with an exact pathGlobFilter can reduce the number of source roots examined by a listener. Validate safe unique basenames, glob syntax, full path-set equality, partition discovery and input_file_name semantics. Metadata-only parity is not row parity or a measured end-to-end speedup. Do not enable this optimization by default on untested runtimes.
- Do not patch AIDP JARs, disable lineage/authentication, or copy upstream OpenLineage settings into a vendor build without establishing support and preserving functionality.

## Capture and reconcile monitoring state

- fetchOutput may wrap NOTEBOOK inside APPLICATION_JSON. Decode output channels only; never count notebook source as execution evidence. See the [offline decoder and validation contract](../../aidp-runtime-validate/references/validation-contract.md).
- Concurrent print calls can concatenate JSON events without newlines. Parse with JSONDecoder.raw_decode after an explicit marker. Truncated or unsupported exports remain incomplete; preserve raw responses.
- A Jupyter execute_reply of ok can coexist with an AIDP `Command ID ... failed with ...` message. Preserve that failure signal and correlate the command rather than trusting the wrapper status alone. A generic occurrence of the word failed is insufficient.
- Follow service pagination. For a capped log window without usable pagination, subdivide a bounded interval; deduplicate by event identity, not message text alone. If a minimum interval still reaches the cap, report counts as lower bounds and retain the capped windows. Empty unsuccessful requests are not clean logs.
- Capture Spark UI REST history before stopping compute; retained in-memory jobs/stages may be evicted. Report retention and failed endpoints. Thread dumps and SQL plans may contain private paths or data; keep raw evidence restricted.
- Reconcile an interrupted monitor with the actual service run/command before retrying. Confirm cancellation within the authorized grace period; stop only the registered compute if escalation is authorized. Never assume a local timeout cancelled the run.

## Correctness is separate from timing

Compare aligned schemas, row counts, keys, duplicates, rejected records, business totals and bidirectional exceptAll (preserving multiplicity). Equal traffic totals or equal numbers of distinct keys do not prove equal rows or equal key sets. Distinguish operational repeatability, correctness and observability in the report.

dropDuplicates on a subset can preserve different non-key attributes after a shuffle. Inspect the actual aggregate plan and profile differing rows with null-safe key comparisons. Guard joins against duplicated keys to prevent diagnostic row multiplication. Do not invent a new tie-break rule or relax parity silently; recover the business rule from the source system. A file-layout optimization can expose existing nondeterminism without being the sole cause of all differences.

Reuse a prior complete, unrepaired run if it satisfies the frozen comparison contract; retain its original launch metadata and record the qualification decision. Do not combine different configurations just because their durations are close. Report minimum, median, maximum and population CV; three similar runs do not establish a production SLA. A telemetry warning alone does not invalidate observed timing, while its operational impact still requires an explicit verdict.

## Official sources and integration

Reviewed 2026-09-16:

- [Oracle compute runtime](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aidug/manage-compute.html) and [compute monitoring](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aidug/monitor-compute.html).
- [Spark 3.5 performance tuning](https://archive.apache.org/dist/spark/docs/3.5.0/sql-performance-tuning.html), [configuration](https://archive.apache.org/dist/spark/docs/3.5.0/configuration.html) and [monitoring](https://archive.apache.org/dist/spark/docs/3.5.0/monitoring.html).
- [Spark file-source options](https://raw.githubusercontent.com/apache/spark/v3.5.0/docs/sql-data-sources-generic-options.md), [First aggregate](https://raw.githubusercontent.com/apache/spark/v3.5.0/sql/catalyst/src/main/scala/org/apache/spark/sql/catalyst/expressions/aggregate/First.scala), [Observation implementation](https://github.com/apache/spark/blob/v3.5.0/sql/core/src/main/scala/org/apache/spark/sql/Observation.scala).
- [Hadoop 3.3.4 filesystem contract](https://hadoop.apache.org/docs/r3.3.4/hadoop-project-dist/hadoop-common/filesystem/filesystem.html).
- [Oracle Workbench Engineer Agent](https://github.com/oracle-samples/oracle-aidp-samples/tree/main/ai/claude-code-plugins/oracle-ai-data-platform-workbench-engineer-agent): use its debugging, optimization, pipelines and Volumes skills when installed. Record upstream version/commit and license for any separately installed adapter. This release links to Oracle's agent; it does not bundle or relabel Oracle's code. Verify REST and notebook-session API versions separately, profile, target and temporary notebook ownership before running its helpers.

Consult the case's authorized Slack threads for exact signatures; retain permalinks privately and verify recommendations against official sources. Never send messages as a side effect of diagnosis. Escalate to Oracle only when an unresolved service-side question requires evidence beyond available cluster/log access. The campaign that informed these checks had incomplete full-result reconciliation at the release evidence cutoff; no claim of a universally fixed or certified workload is made.
