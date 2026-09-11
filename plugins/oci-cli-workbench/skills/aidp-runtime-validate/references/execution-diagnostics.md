# Execution diagnostics and streaming recovery

Use this reference for slow, failed, stuck, or inconsistently cancelled AIDP jobs. Diagnosis is read-only. A diagnostic request does not authorize running notebooks, restarting compute, resetting state, or sending Slack messages.

## Collect evidence before choosing a cause

1. Resolve the explicit case's region, platform, workspace, job, run, and compute. Never reuse another project's default OCIDs or a manifest with unexpanded `${...}` values. Verify the selected OCI profile and key-file existence without printing credentials. Prefer the workbench wrapper; when its API version or endpoint is incompatible, reuse the project's signed AIDP client for documented read operations.
2. Read the reported Slack thread and search for the exact error signatures in other accessible threads. Preserve permalinks and distinguish an engineer's explanation, an unverified workaround, and an unresolved report. A matching error is evidence of a symptom, not proof of the same root cause. Use current official Oracle documentation alongside Slack.
3. Export job-run details, job definition, current compute settings, driver/executor logs, and metrics for a bounded UTC interval around the event. Retain request IDs and correlation IDs in restricted case evidence. Keep credentials, customer code, paths, and full OCIDs out of reusable plugin content.
4. Follow `opc-next-page` for job lists and logs; if a time or output bound stops retrieval, record the pages/rows collected and label the result partial. An empty result from a failed request or unsupported metric name is not a healthy result.
5. Record current compute configuration separately from historical configuration. A worker count observed now cannot explain a past run without matching historical evidence.

Official references: [monitor compute](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aidug/monitor-compute.html), [monitor jobs](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aidug/monitor-jobs.html), [manage compute](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aidug/manage-compute.html).

## Separate original execution, repairs, and cancellation

`taskRunSummaryMap` can contain historical and current task attempts. Select the latest task attempts with `taskToTaskRunMap`; inspect `repairHistory` independently. An absent or inconsistent map means the scope is unknown or incomplete. Do not count historical failed tasks as failures of a successful repair, or compare an end-to-end run duration with only the last repair's duration.

Use the bundled offline utility on explicitly selected exported **job-run detail** files:

```text
python scripts/summarize_aidp_runs.py run-detail-1.json run-detail-2.json --output attempt-summary.json
python scripts/test_summarize_aidp_runs.py
```

Paths above are relative to this skill directory. The utility accepts an OCI response envelope or a JobRun object. It makes no cloud calls. It emits hashed identifiers, task names, states, valid timestamp durations, repair counts, parameter/definition hashes, and fixed error-signature labels. It omits raw errors, source, and parameter values. Task names remain case metadata: review output before sharing. The output must be a new file; existing output files and input exports are never overwritten. Null/invalid timestamps remain unknown. `reported_wall_seconds` uses the run object's reported start/end timestamps without assuming whether they cover an original run or a repair. Wall time includes orchestration and cancellation delays; it is not Spark execution time. Input exports must be bounded because the utility reads them into memory.

Before declaring a performance regression, compare the same immutable input inventory (count, bytes, identity/version), notebook code, task graph, parameters, compute settings, and concurrency. Matching output hashes or task counts alone do not establish equivalence. A successful repaired run is not an unrepaired baseline. A higher configured `maxConcurrentRuns` does not prove runs actually overlapped.

## Classify the first failure

| Observation | Supported conclusion | Next discriminating evidence |
| --- | --- | --- |
| `Errno 107: Transport endpoint is not connected` or `Errno 103: Software caused connection abort` on `/Volumes/...` | The mounted-volume access path failed. It does not prove a missing bucket, IAM defect, or a specific mount-daemon failure. | First failing syscall, synchronized failures across tasks, mount/runtime logs, memory pressure and runtime restarts. |
| `WORKFLOW_0015`, `GetCommandStatus`, command not found in execution context | Workflow command tracking failed. The job status can diverge from underlying execution. | Exact command, context and request IDs; task history; driver logs before the tracking error. |
| `Failed to cancel task run execution` | Cancellation did not complete normally. A repair may coexist with evidence of unresolved previous work. | Terminal state and runtime confirmation before replaying append writes or repairing. |
| `IllegalArgumentException: Wrong basePath` | Spark rejected the relationship between the supplied base and leaf paths; this can be a deterministic code defect. | Inspect URI schemes, authorities, normalized path components and partition boundaries before treating it as Volume downtime. |
| Host memory near its limit | Memory pressure is observed. Low JVM heap or GC can still coexist with high Python/native/cache memory. | Host/container RSS, Python/native allocations, driver/executor split, restart events, exit 137 and `OOMKilled`. Memory utilization alone does not prove OOM. |
| Kubernetes `deletecollection pods` forbidden while compute is shutting down | Potential teardown noise; do not immediately propose new IAM/RBAC grants. | Establish whether the error precedes the primary failure or occurs during cleanup; obtain service-owner interpretation. |
| `VolumePathDoesNotExistException` during path or `_spark_metadata` probing | The application checked a path that did not exist at that instant. | Verify whether this was an expected existence probe or the actual failing read/write before diagnosing data loss. |

Correlate metrics at the same time and aggregation. Label a five-minute mean as a mean, not an instantaneous peak. Do not sum mean values of a failed-task counter or equate that counter with failed workflows. Driver bottlenecks are not resolved merely by adding workers. For supported Spark tuning, use Oracle's [Spark optimization skill](https://github.com/oracle-samples/oracle-aidp-samples/blob/main/ai/claude-code-plugins/oracle-ai-data-platform-workbench-engineer-agent/skills/aidp-spark-optimization/SKILL.md).

## Distinguish path construction from a runtime restart

Spark 3.5 [partition discovery](https://archive.apache.org/dist/spark/docs/3.5.0/sql-data-sources-parquet.html#partition-discovery) uses `basePath` to determine partition columns. Inspect the actual values passed to the reader and returned by Hadoop, not just the original parameter string.

In one isolated AIDP investigation, Hadoop enumeration returned leaves such as `file:/Volumes/<catalog>/<schema>/<volume>/part=1/data.parquet` while `basePath` remained `/Volumes/<catalog>/<schema>/<volume>`. Applying `FileSystem.makeQualified` through either filesystem did not reconcile them in that runtime. Explicitly using the same `file:` URI form for the mounted local base and its leaves removed the deterministic failure. This is an observed mitigation for that path mismatch, not a universal rewrite rule or an Oracle product fix.

Before applying that change, verify that both paths refer to the same mounted local filesystem; reject other schemes, unexpected authorities, relative paths and parent traversal. Validate containment by path components, not a string prefix that also accepts a sibling directory. Do not convert `oci:`, `hdfs:` or other remote URIs to `file:`. Check one leaf, partition-column preservation and full result parity in an isolated output before recommending the smallest shared path-construction fix.

Separately, correlate Spark application ID changes and driver/container start times with host memory, JVM heap, Python/native memory and the first task failure. A changed application ID while orchestration still reports `RUNNING` supports a runtime/context replacement, but not its cause. Higher driver memory can be a validated mitigation; it is not proof of an OOM or a product defect without the corresponding event or trace. Inspect available driver, executor and service logs before requesting additional evidence from Oracle.

## Authorized isolated experiments

When experiments are already authorized, reuse that scope and budget. Create only owned resources and paths with the agreed suffix (for example `_jg`), preserve source hashes, freeze input identity and parameters, and give every attempt a fresh output. Reject missing parameters, paths outside the experiment roots and accidental reuse of append destinations. Freeze only referenced inputs with bounded streaming copies and an immutable manifest.

Probe the same objects through POSIX listing, Hadoop listing and a small Spark read. Keep total work fixed while changing one variable at a time: listing strategy, driver capacity, task concurrency or workload code. Separate cold starts from subsequent executions, preserve reference timeouts and enforce the authorized external deadline and cluster-hour budget. Capture evidence before cancelling only the owned run; stop only its isolated compute if cancellation exceeds the agreed grace period. Increasing worker count does not by itself remedy a driver bottleneck.

Require repeated success, schema/count/key/duplicate/business-aggregate parity, complete cancellation and comparable timing distributions before accepting a candidate. A single successful retry or faster repaired run is insufficient to establish stability or root cause.

## AMD and ARM: documentation and compatibility

Oracle's [compute documentation](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aidug/manage-compute.html) lists Spark 3.5.0, Delta 3.2.0, Python 3.11, Scala 2.12, Hadoop 3.3.4 and Java 17 for this runtime; verify the deployed versions in each case. The reviewed [Spark 3.5.0 overview](https://archive.apache.org/dist/spark/docs/3.5.0/index.html) and [tuning guide](https://archive.apache.org/dist/spark/docs/3.5.0/tuning.html) do not establish a general AMD-over-ARM or ARM-over-AMD preference. Oracle's [Ampere A1 price/performance study](https://blogs.oracle.com/cloud-infrastructure/price-performance-big-data-workloads-ampere-a1) concerns specific Spark 3.1.2/3.2 workloads on YARN; it does not demonstrate superiority for every AIDP 3.5 workload.

Technical interpretation: retain the validated architecture during incident diagnosis. Consider AMD/x86_64 when native dependencies require it, and ARM64 when JVM, Python wheels, JARs, codecs and connectors are compatible and price/performance warrants a separate evaluation. Diagnose memory, listing, shuffle, skew and workflow logic first. A documentary architecture question does not authorize comparative runs or new ARM clusters, and a Volume error does not establish an architecture-specific cause.

## Monitoring API compatibility

Consult the deployed API version and Oracle's [searchLogs](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aiwap/op-aidataplatforms-aidataplatformid-workspaces-workspacekey-clusters-clusterkey-actions-searchlogs-post.html) and [summarizeMetricsData](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aiwap/op-aidataplatforms-aidataplatformid-workspaces-workspacekey-clusters-clusterkey-actions-summarizemetricsdata-post.html) contracts first. Both are read operations exposed as POST actions on a workspace cluster.

One observed deployment of API `20260430` rejected the documented RFC3339 time strings, accepted epoch milliseconds, and returned data for `MemoryUtilization` while the documented uppercase `MEMORY_UTILIZATION` returned no series. Treat this as a scoped compatibility observation, not a universal schema change or a cause of workload failure.

When the documented request fails with a contract error, perform a bounded read-only compatibility probe, recording the request shape, status and request ID. If necessary, test the known epoch-millisecond representation and observed CamelCase metric names (`MemoryUtilization`, `CpuUtilization`, `GcCpuUtilization`, `JvmHeapUsed`, `TotalFailedTasks`). Require a successful response and validate series metadata, executor dimensions and timestamps before interpretation. Do not automatically retry arbitrary failures or apply this fallback to writes. Preserve both the documented and successful request shapes for service support.

For logs, `messageContains` is documented for events; use the appropriate stream and supported filters. Respect the documented page limit, continue with the returned page token, and label truncated log windows explicitly.

## Streaming: preserve progress and checkpoints

Reuse existing deployment/maintenance helpers when they are available. Project-derived CDC maintenance provides the following reusable invariants; its customer-specific worker names, paths, and tables must not be copied as defaults:

- Build a dry-run plan first, resolve ownership and exact worker scope, and detect checkpoint drift before changing anything.
- Pause continuous scheduling before cancellation so the controller does not immediately restart the worker. Confirm terminal cancellation; a cancelled UI state alone does not resolve a lost-command incident.
- Keep the same job identities and unique persistent checkpoint locations. Never delete/rewrite checkpoints or reseed history as a routine recovery step.
- Limit maintenance to explicitly selected Delta tables, keep temporary resources identifiable, and clean owned temporary resources even when the maintenance step fails. Do not infer that `OPTIMIZE`, `VACUUM`, or `RESTORE` applies to plain Parquet outputs.
- Reactivate the same workers/checkpoints only after validation. This reference is an operator procedure, not a new live maintenance command.
- Prove progress with advancing batch IDs/input offsets, processed-file identity, committed output and checkpoint updates. `RUNNING` alone is insufficient. Use a workload-appropriate observation window; low traffic can legitimately produce no new batch.
- Keep `file_state`, `output_refresh`, `stream_run_state`, and `stream_batch_state` distinct. Require the acceptance playbook's consecutive zero-backlog windows and materialized-result parity before declaring convergence.

Streaming is not a repair for an unhealthy Volume or lost execution context. Introduce it only after stabilizing the runtime and designing replay-safe output semantics. Local temporary storage may suit transient extraction, but never replace durable checkpoints or persistent outputs with it. Review Oracle's [known issues](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aidug/known-issues.html), including supported external-volume access for scheduled jobs, before proposing a storage workaround.

## Deliverable

Produce a timestamped case report that separates confirmed mechanisms, likely contributors, alternatives not established, and the smallest next experiment. Include exact evidence provenance, redaction level, pagination completeness, current versus historical configuration, official documentation and Slack permalinks. State what live changes, if any, were actually performed. Prepare a support escalation draft only when an unresolved service-side question requires Oracle evidence beyond the logs and cluster access already available; do not create one automatically when the code defect and runtime mechanism are sufficiently evidenced. Sending any draft requires explicit authorization.
