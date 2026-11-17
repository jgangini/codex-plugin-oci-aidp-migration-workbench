"""Offline, evidence-only assessment of the last three chronological full runs.

Reads a JSON list; never launches jobs, infers missing evidence, or rewrites inputs.
See references/validation-contract.md for the input contract and evidence limits.
"""
import argparse
import json
import math
import re
import statistics
from pathlib import Path

from summarize_aidp_runs import digest


IDENTITIES = ('code_sha256', 'definition_sha256', 'runtime_configuration_sha256',
              'task_configuration_sha256', 'input_manifest_sha256', 'parameters_sha256')


def positive_number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value) and value > 0
    except OverflowError:
        return False


def verdict(runs, field):
    values = [r.get(field) for r in runs]
    if any(value is not None and type(value) is not bool for value in values):
        raise ValueError('Validation evidence must be boolean or null')
    if any(value is False for value in values):
        return 'FAIL'
    return 'PASS' if len(values) == 3 and all(value is True for value in values) else 'PENDING'


def all_equal(runs, field, value):
    return len(runs) == 3 and all(type(r.get(field)) is type(value) and r[field] == value for r in runs)


def same_fingerprint(runs, field):
    values = [r.get(field) for r in runs]
    valid = all(isinstance(v, str) and re.fullmatch(r'[0-9a-f]{64}', v) for v in values)
    return len(runs) == 3 and valid and len(set(values)) == 1


def consecutive_runs(runs):
    sequence = [r.get('sequence') for r in runs]
    valid = all(type(i) is int and i >= 0 for i in sequence)
    return len(runs) == 3 and valid and sequence == list(range(sequence[0], sequence[0] + 3))


def run_checks(last, expected_files):
    attempts = [r.get('attempt') for r in last]
    checks = {
        'three_runs': len(last) == 3,
        'distinct_attempts': all(isinstance(a, str) and a for a in attempts) and len(set(map(str, attempts))) == 3,
        'successful': all_equal(last, 'status', 'SUCCESS'),
        'full_load': all_equal(last, 'files', expected_files),
        'unrepaired': all_equal(last, 'repair_count', 0),
        'no_manual_intervention': all_equal(last, 'manual_interventions', 0),
        'consecutive': consecutive_runs(last),
        'cold_warm_cold': [r.get('cold_start') for r in last] == [True, False, True] and all(type(r.get('cold_start')) is bool for r in last),
    }
    for field in IDENTITIES:
        checks['same_' + field] = same_fingerprint(last, field)
    return checks


def assess(runs, expected_files, max_cv=0.10):
    if type(expected_files) is not int or expected_files <= 0:
        raise ValueError('Expected file count must be a positive integer')
    if not positive_number(max_cv) or max_cv > 1:
        raise ValueError('CV limit must be finite and in (0, 1]')
    if not isinstance(runs, list) or not all(isinstance(r, dict) for r in runs):
        raise ValueError('Expected a chronological list of run evidence')
    last = runs[-3:]
    durations = [r.get('workflow_seconds') for r in last]
    valid_times = len(last) == 3 and all(positive_number(t) for t in durations)
    cv = statistics.pstdev(durations) / statistics.mean(durations) if valid_times else None
    checks = dict(run_checks(last, expected_files), valid_durations=valid_times,
                  cv_within_limit=cv is not None and cv <= max_cv)
    execution = all(checks.values())
    correctness = verdict(last, 'validation_passed')
    operational = verdict(last, 'operational_validation_passed')
    # Launch-time acceptance flags control budgets, not the evidentiary value of a completed run.
    return {
        'execution_stable': execution, 'correctness': correctness, 'operational_validation': operational,
        'accepted': execution and correctness == operational == 'PASS',
        'checks': checks, 'unmet_checks': [k for k, v in checks.items() if not v],
        'run_refs': [digest(r.get('attempt'))[:12] for r in last], 'samples_available': len(runs),
        'minimum_minutes': min(durations) / 60 if valid_times else None,
        'median_minutes': statistics.median(durations) / 60 if valid_times else None,
        'maximum_minutes': max(durations) / 60 if valid_times else None,
        'cv_population': cv, 'cv_limit': max_cv,
        'note': 'Workflow time excludes startup; cost includes all provisioned time. Three samples do not establish an SLA. Evidence flags require independently reviewed reports.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--files', required=True, type=int)
    parser.add_argument('--max-cv', type=float, default=0.10)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        result = assess(json.loads(args.input.read_text(encoding='utf-8-sig')), args.files, args.max_cv)
        encoded = json.dumps(result, indent=2, allow_nan=False)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(encoded)
    except (OSError, ValueError, TypeError) as error:
        parser.exit(2, f'Assessment not completed ({type(error).__name__}); existing files were not overwritten.\n')
    print('Evidence assessed; inspect separate verdicts in the output.')


if __name__ == '__main__':
    main()
