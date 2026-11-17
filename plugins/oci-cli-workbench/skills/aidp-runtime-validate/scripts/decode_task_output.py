"""Decode an explicitly selected AIDP fetchOutput/kernel export offline.

Reads output channels only, never notebook source. Output may contain private
case data: keep it restricted and sanitize before sharing. No cloud calls.
"""
import argparse
import json
import re
from pathlib import Path


def text_value(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list) and all(isinstance(x, str) for x in value):
        return ''.join(value)
    raise ValueError('Unsupported text representation')


def objects(value):
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError('Expected a list of output objects')
    return value


def notebook_texts(outputs):
    texts = []
    for output in objects(outputs):
        mime = output.get('data') or {}
        if not isinstance(mime, dict):
            raise ValueError('Invalid MIME output data')
        if 'text' in output:
            texts.append(text_value(output['text']))
        elif 'text/plain' in mime:
            texts.append(text_value(mime['text/plain']))
        elif output.get('output_type') == 'error':
            texts.append(text_value(output.get('evalue', '')))
            texts.append(text_value(output.get('traceback', [])))
        else:
            raise ValueError('Unsupported output channel; preserve raw evidence')
    return texts


def aidp_texts(items, depth):
    texts = []
    for item in objects(items):
        kind = item.get('type')
        if kind == 'TEXT_PLAIN':
            texts.append(text_value(item['value']))
        elif kind in ('NOTEBOOK', 'APPLICATION_JSON'):
            texts.extend(task_texts(item['value'], depth + 1))
        else:
            raise ValueError('Unsupported AIDP output type')
    return texts


def task_texts(payload, depth=0):
    if depth > 8:
        raise ValueError('Output nesting exceeds eight layers')
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, dict):
        raise ValueError('Expected an output object')
    status = str(payload.get('status', '')).split(' ', 1)[0]
    if status.isdigit() and status != '200':
        raise ValueError('Unsuccessful API envelope')
    if 'data' in payload and isinstance(payload['data'], dict):
        if status and status != '200':
            raise ValueError('Unsuccessful API envelope')
        return task_texts(payload['data'], depth + 1)
    if 'output' in payload:
        return task_texts(payload['output'], depth + 1)
    if 'cells' in payload:
        return [text for cell in objects(payload['cells']) for text in notebook_texts(cell.get('outputs', []))]
    if 'outputs' in payload:
        return notebook_texts(payload['outputs'])
    return aidp_texts(payload.get('data'), depth)


def marked_events(text, marker):
    if not isinstance(marker, str) or not marker or len(marker) > 128:
        raise ValueError('An explicit marker of 1..128 characters is required')
    events = []; offset = 0; decoder = json.JSONDecoder()
    while (start := text.find(marker, offset)) != -1:
        offset = start + len(marker)
        while offset < len(text) and text[offset].isspace():
            offset += 1
        event, offset = decoder.raw_decode(text, offset)
        if not isinstance(event, dict):
            raise ValueError('Expected a JSON object after the event marker')
        events.append(event)
    return events


def decode(payload, marker):
    text = ''.join(task_texts(payload))
    return {'events': marked_events(text, marker),
            'command_failure_signature_present': bool(re.search(r'\bCommand(?: ID)?\s+\S+\s+failed with\b', text, re.I)),
            'output_characters': len(text),
            'coverage': 'Selected export only; no claim of complete log history or successful execution.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--marker', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        result = decode(json.loads(args.input.read_text(encoding='utf-8-sig')), args.marker)
        encoded = json.dumps(result, indent=2, allow_nan=False)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(encoded)
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as error:
        parser.exit(2, f'Output not decoded ({type(error).__name__}); retain the raw export. Existing files were not overwritten.\n')
    print('Selected output decoded; inspect evidence coverage and command failure signature.')


if __name__ == '__main__':
    main()
