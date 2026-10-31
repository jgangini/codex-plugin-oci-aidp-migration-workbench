# Agent edit/test loop and evidence

Verified against official documentation and Oracle sample source on 2026-10-30.
This is workflow guidance, not a live certification of any tenancy or an
implementation of test/deployment API calls.

## Select the execution surface

| Change | First useful check | What it does not establish |
|---|---|---|
| Pure parsing, dates, budgets, query construction | Local fixtures or editor Play/Run now | Hosted permissions, model behavior or deployment parity |
| One MCP/HTTP/SQL/RAG tool | Tool Test with bounded input | Full conversational routing or all data access |
| Instructions, model/tool selection, memory | Agent Test/Playground, isolated session | Correct production endpoint revision |
| New dependencies or custom tool package | Verify package install path, then test | That every runtime installs dependencies at the same stage |
| Explicit publication request | Deploy candidate then endpoint smoke test | Long-term reliability, exhaustive coverage or load capacity |

Oracle documents attaching AI Compute before testing, propagation of agent
edits on Test, and a Playground with chat, traces and individual executor tests.
Confirm those controls and state on the actual instance. Some surfaces/version
combinations still prepare or deploy a Playground package. Do not promise that
every test is instant or that editing changes an already deployed endpoint.

Run now executes workspace code. Playground/deployment execute a packaged copy
of the entry-file folder and its subfolders. Keep included configuration beside
the agent and resolve it relative to that file; do not rely on parent/sibling
workspace paths. Use supported parameters/session variables for varying values.

Code-editor dependency installation and custom-tool-package installation have
different lifecycles. Agent Creation describes installing dependencies during
editor/test execution; About Agent Tools warns that third-party dependencies of
custom packages require a full deployment before Playground testing. Identify
which mechanism is in use; do not generalize one rule to every agent.

## Readiness and reuse

Record only the target needed for the task: workspace, development agent,
compute attachment/readiness, revision, entry file, dependency versions and
existing deployment. Keep sensitive identifiers in the project's restricted
runtime context, not in plugin examples or public evidence.

Inspect installed official skill provenance/version and live API compatibility.
Prefer its agent-flow/high-code, tools, files, model and compute operations.
Use an existing wrapper only if its actual help/schema supports the operation.
Do not generate guessed deployment enums, endpoints or parameter grids. Treat
unavailable feature readiness as a platform blocker, not a reason to re-create
resources. A local fallback can test the portable logic and MCP client, but
`aidputils`-specific runtime integration still needs an AIDP check.

## Acceptance cases

Choose cases that exercise the requested change, rather than running an entire
migration campaign. For a research agent, useful examples are explicit source
selection; an ambiguous source; timezone-aware today versus rolling 24 hours;
seven-day boundaries; no results; missing or unapproved credentials; provider
failure; spending-limit exhaustion; duplicate evidence; and an MCP timeout with
an uncertain paid start. A follow-up question should reuse eligible prior data
without automatically repeating extraction.

Tool exposure is not a budget ledger. Allowlist tools and enforce bounds in the
execution path. Record provider costs separately from model/compute costs;
unknown costs remain unknown. If cached evidence is used, show its freshness.
Keep untrusted extracted content separate from agent instructions and do not
send a full private catalog when a small selection of approved URLs is enough.

Test one known input without modifying production state. Capture input scope,
code/config revision, result, trace/tool calls, paid run identifiers when any,
and actual cost when reported. Redact secrets and avoid logging raw sensitive
payloads. Reconcile in-flight work before rerunning. Do not infer that all
sources are working because one Actor returned data.

## Publication boundary

"Develop", "edit", "test", "try in Playground" and positive feedback are not
production publication requests. A request to publish must identify, or have
already established, the destination and reviewed candidate. Honor existing
specific authorization; ask only when that scope is materially ambiguous.
Testing that incurs cost or changes cloud resources also needs task scope.

Before deployment: reviewed diff, focused tests, dependency/package check,
credential scope, supported deployment operation, existing deployment state
and rollback revision. After deployment: terminal status, actual served
revision, one representative endpoint conversation/tool test, and bounded
error/trace review. Keep separate verdicts for tests and publication. Never
declare success merely because an API accepted an asynchronous request.

## Official sources and examples

- [Oracle Agent Creation: editor and Agent Testing](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aidug/agent-creation.html).
- [Oracle Agent Tools: individual tests, MCP and custom-package dependencies](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aidug/agent-flow-tools.html).
- [Oracle Agent Deployment: packaged snapshot and endpoint updates](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aidug/agent-flow-deployment.html).
- [Oracle agent updates, 2026-10-28](https://blogs.oracle.com/ai-data-platform/oracle-ai-data-platform-agent-updates).
- [OpenAI skill design and instruction-following review](https://developers.openai.com/plugins/build/skills).
- [OpenAI plugin packaging and local testing](https://developers.openai.com/plugins/build/plugins).

Oracle's `oracle-samples/oracle-aidp-samples` was inspected at commit
`d006f1eb1843e82278b988366a2d20bd1ba983fc` (UPL-1.0):

- [Hello-world code-first agent](https://github.com/oracle-samples/oracle-aidp-samples/blob/d006f1eb1843e82278b988366a2d20bd1ba983fc/ai/agent-flows/code-first/hello-world/hello-world.py): entry class, setup/invoke and runnable sample.
- [MCP bearer-auth sample](https://github.com/oracle-samples/oracle-aidp-samples/blob/d006f1eb1843e82278b988366a2d20bd1ba983fc/ai/agent-flows/code-first/mcp-examples/single-agent-mcp-pat.py): selected-tool schemas, Streamable HTTP, invocation/streaming lifecycle and runtime helpers.

These are references, not shipped implementation. Samples were read, not run;
no Oracle code was copied. Validate imports/lifecycle against the installed
runtime and replace illustrative inline token placeholders with supported
secret bindings. Do not hard-code a sample model, region or empty guardrail
policy as a production default.
