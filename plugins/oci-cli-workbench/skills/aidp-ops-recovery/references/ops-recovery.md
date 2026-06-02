# Ops Recovery

## Common recovery families

- Cancel active job runs before redeploying or re-running.
- Reset isolated runtimes when the runtime state is stale or wedged.
- Clean up unused computes only after confirming they are not the current target.
- Prefer `uv run codex-oci aidp compute stop|delete|cleanup` when the wrapper already exposes the needed compute action.
- Watch long migrations with periodic status writes and optional Slack notification.

## Order of operations

1. Gather runtime status.
2. Cancel the conflicting or stale runs.
3. Clean the specific blocked resource.
4. Re-validate the environment.
5. Hand off to deploy or acceptance only after the workspace is stable again.

## Notification rule

- Slack notification is optional and must be explicitly requested by the user.
