"""Synthetic offline regression checks: run with Python, no external dependencies."""
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from assess_repeatability import IDENTITIES, assess
from decode_task_output import decode, task_texts


def rejects(function, *args):
    try:
        function(*args)
    except (ValueError, TypeError):
        return
    raise AssertionError('Invalid evidence was accepted')


base = {field: 'a' * 64 for field in IDENTITIES}
base.update(status='SUCCESS', files=100, repair_count=0, manual_interventions=0,
            workflow_seconds=9000, validation_passed=True, operational_validation_passed=True)
runs = [dict(base, attempt=f'private-run-{i}', sequence=i, cold_start=cold, acceptance=False)
        for i, cold in enumerate([True, False, True])]
result = assess(runs, 100)
assert result['accepted'] and result['execution_stable'] and result['median_minutes'] == 150
assert 'private-run' not in json.dumps(result)
assert not assess(runs[:2], 100)['execution_stable']
different = copy.deepcopy(runs)
different[1]['validation_passed'] = False
result = assess(different, 100)
assert result['execution_stable'] and result['correctness'] == 'FAIL' and not result['accepted']
different[1]['validation_passed'] = None
different[1]['operational_validation_passed'] = False
result = assess(different, 100)
assert result['execution_stable'] and result['correctness'] == 'PENDING'
assert result['operational_validation'] == 'FAIL' and not result['accepted']
for field in IDENTITIES:
    changed = copy.deepcopy(runs); changed[1][field] = 'b' * 64
    assert not assess(changed, 100)['execution_stable']
for field, value in [('files', 99), ('files', True), ('repair_count', 1), ('repair_count', None),
                     ('manual_interventions', 1), ('sequence', 7), ('sequence', True),
                     ('cold_start', 0), ('cold_start', True), ('workflow_seconds', 20000),
                     ('workflow_seconds', float('nan')), ('workflow_seconds', float('inf')),
                     ('workflow_seconds', -1), ('workflow_seconds', True), ('status', 'CANCELED'),
                     ('workflow_seconds', 10**400),
                     ('attempt', runs[0]['attempt'])]:
    changed = copy.deepcopy(runs); changed[1][field] = value
    assert not assess(changed, 100)['execution_stable'], field
assert not assess([runs[2], runs[1], runs[0]], 100)['execution_stable']
changed = copy.deepcopy(runs); del changed[1]['runtime_configuration_sha256']
assert not assess(changed, 100)['execution_stable']
changed = copy.deepcopy(runs); changed[1]['validation_passed'] = 'true'
rejects(assess, changed, 100)
rejects(assess, runs, True)
rejects(assess, runs, 100, float('nan'))
rejects(assess, {}, 100)

marker = 'AIDP_TEST::'
events = marker + '{"phase":"write_end"}' + marker + ' {"phase":"metrics_end"}'
notebook = {'cells': [{'source': marker + '{"source_is_not_evidence":true}',
                       'outputs': [{'data': {'text/plain': [events[:20], events[20:]]}}]}]}
payload = {'status': '200 OK', 'data': {'data': [{'type': 'APPLICATION_JSON', 'value': json.dumps(
    {'output': {'data': [{'type': 'NOTEBOOK', 'value': json.dumps(notebook)}]}})}]}}
result = decode(payload, marker)
assert result['events'] == [{'phase': 'write_end'}, {'phase': 'metrics_end'}]
assert not result['command_failure_signature_present']
assert 'source_is_not_evidence' not in json.dumps(result)
kernel = {'status': 'ok', 'outputs': [{'name': 'stderr', 'text': 'Command ID abc failed with RuntimeError'}]}
assert decode(kernel, marker)['command_failure_signature_present']
assert decode({'outputs': [{'output_type': 'error', 'evalue': 'Command ID abc failed with RuntimeError'}]}, marker)['command_failure_signature_present']
assert not decode({'outputs': [{'text': 'Previous task failed but this is a warning'}]}, marker)['command_failure_signature_present']
rejects(decode, {'status': 404, 'data': []}, marker)
rejects(decode, {'data': [{'type': 'UNKNOWN', 'value': events}]}, marker)
rejects(decode, {'data': [{'type': 'TEXT_PLAIN', 'value': marker + '{"truncated":'}]}, marker)
rejects(decode, payload, '')
rejects(decode, {'cells': 'wrong'}, marker)
rejects(decode, {'outputs': [1]}, marker)
rejects(decode, {'outputs': [{'data': 'wrong'}]}, marker)
rejects(decode, {'data': [1]}, marker)
assert task_texts({'data': [{'type': 'TEXT_PLAIN', 'value': r'C:\temp\raw'}]}) == [r'C:\temp\raw']
deep = {'data': []}
for _ in range(10):
    deep = {'output': deep}
rejects(decode, deep, marker)

with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    for script, value, options in [('assess_repeatability.py', runs, ['--files', '100']),
                                    ('decode_task_output.py', payload, ['--marker', marker])]:
        source = root / (script + '.input.json'); output = root / (script + '.output.json')
        source.write_text(json.dumps(value), encoding='utf-8')
        original = source.read_bytes()
        command = [sys.executable, str(Path(__file__).with_name(script)), str(source), *options, '--output']
        process = subprocess.run(command + [str(output)], capture_output=True, text=True)
        assert process.returncode == 0, process.stderr
        saved = output.read_bytes()
        assert subprocess.run(command + [str(output)], capture_output=True).returncode == 2
        assert output.read_bytes() == saved
        assert subprocess.run(command + [str(source)], capture_output=True).returncode == 2
        assert source.read_bytes() == original
        source.write_text('PRIVATE_SENTINEL invalid JSON', encoding='utf-8')
        failure = subprocess.run(command + [str(root / 'invalid.json')], capture_output=True, text=True)
        assert failure.returncode == 2 and not (root / 'invalid.json').exists()
        assert 'PRIVATE_SENTINEL' not in failure.stderr

print('PASS: separate verdicts, same frozen runs, repairs, finite timings, output-only decoding, concatenated events, command failure, CLI and evidence preservation')
