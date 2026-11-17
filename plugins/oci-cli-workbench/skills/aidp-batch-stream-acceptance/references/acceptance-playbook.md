# Acceptance Playbook

## Canonical sequence

1. Cancel active runs that can contaminate the workspace.
2. Refresh mdln structures.
3. Run the `ref` workflow.
4. Build the batch full baseline for the required dates.
5. Capture the baseline snapshot for the stream comparison date.
6. Reset the stream process date and confirm the control layer is clean enough for a new convergence window.
7. Deploy streaming jobs and checkpoint expectations.
8. Start bronze, silver, and bt workers.
9. Wait for bt backlog zero across consecutive windows using `file_state.pending_silver_count`, `file_state.pending_bt_count`, and `output_refresh.pending_bt_outputs`.
10. Stop stream workers cleanly once the bt zero window holds.
11. Run agg finalize.
12. Wait until `output_refresh.pending_agg_outputs` reaches zero and capture the last backlog evidence window.
13. Capture the candidate snapshot and compare it to the baseline.

## Curated operational defaults

- Choose baseline dates that exercise warm-up, replay, and comparison behavior for the target pipeline.
- Pick at least one explicit comparison date whose batch baseline is already stable before starting streaming acceptance.
- Stream worker jobs: bronze, silver, bt, and agg finalize are separate jobs.

## Operational reminders

- The acceptance flow is mutating and long-running.
- Keep the generated reports because later runtime validation and handoff depend on them.
- Save the backlog windows, output-refresh record maps, and final snapshot comparison together.
- A timeout is not equivalent to failure analysis; keep the backlog evidence and explain where convergence stopped.
