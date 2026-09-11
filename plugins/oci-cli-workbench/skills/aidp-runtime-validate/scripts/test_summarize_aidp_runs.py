"""Run directly with Python; no cloud calls or additional dependencies."""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

source = Path(__file__).with_name("summarize_aidp_runs.py")
spec = importlib.util.spec_from_file_location("run_summary", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

payload = {
    "key": "private-run-id", "state": {"status": "SUCCESS"},
    "startTime": 5000, "endTime": 9000,
    "parameters": [{"name": "token", "value": "PRIVATE_SENTINEL"}],
    "repairHistory": [{"startTime": 1000, "endTime": 3000}],
    "taskToTaskRunMap": {"Ingest": "new"},
    "taskRunSummaryMap": {
        "old": {"taskKey": "Ingest", "startTime": None, "endTime": None,
                "state": {"status": "FAILED", "stateMessage": "PRIVATE_SENTINEL Transport endpoint is not connected"}},
        "new": {"taskKey": "Ingest", "startTime": 5000, "endTime": 9000,
                "state": {"status": "SUCCESS"}},
    },
}
result = module.summarize({"status": "200 OK", "data": payload})
assert result["repair_count"] == 1 and not result["unrepaired_success"]
assert result["reported_wall_seconds"] == 4
assert result["tasks"][0]["scope"] == "historical"
assert result["tasks"][0]["wall_seconds"] is None
assert result["tasks"][0]["signatures"] == ["volume_transport_disconnected"]
assert result["tasks"][1]["scope"] == "current"
assert "PRIVATE_SENTINEL" not in json.dumps(result)
assert "private-run-id" not in json.dumps(result)
assert module.elapsed_seconds(True, 9000) is None
assert module.elapsed_seconds(9000, 5000) is None
assert module.elapsed_seconds(float("nan"), 9000) is None
assert module.epoch_ms("PRIVATE_SENTINEL") is None
assert module.epoch_ms(float("inf")) is None
payload["taskToTaskRunMap"] = {"Ingest": "missing"}
assert "CURRENT_ATTEMPT_MAP_INCONSISTENT" in module.summarize(payload)["warnings"]
assert all(t["scope"] == "unknown" for t in module.summarize(payload)["tasks"])
payload["taskToTaskRunMap"] = {"DifferentTask": "new"}
assert all(t["scope"] == "unknown" for t in module.summarize(payload)["tasks"])
payload["taskRunSummaryMap"]["new"]["state"]["stateMessage"] = "PRIVATE_SENTINEL Wrong basePath"
assert module.summarize(payload)["tasks"][1]["signatures"] == ["spark_wrong_base_path"]
payload.pop("taskToTaskRunMap")
assert all(t["scope"] == "unknown" for t in module.summarize(payload)["tasks"])
try:
    module.summarize({"status": "404 Not Found", "data": payload})
except ValueError:
    pass
else:
    raise AssertionError("An HTTP error must not become an empty healthy run")
with tempfile.TemporaryDirectory() as directory:
    input_file = Path(directory) / "run-detail.json"
    output_file = Path(directory) / "summary.json"
    original = json.dumps(payload).encode("utf-8")
    input_file.write_bytes(original)
    command = [sys.executable, str(source), str(input_file), "--output"]
    success = subprocess.run(command + [str(output_file)], capture_output=True, text=True)
    assert success.returncode == 0, success.stderr
    assert "PRIVATE_SENTINEL" not in output_file.read_text(encoding="utf-8")
    saved_summary = output_file.read_bytes()
    repeat = subprocess.run(command + [str(output_file)], capture_output=True, text=True)
    assert repeat.returncode == 2 and output_file.read_bytes() == saved_summary
    overwrite = subprocess.run(command + [str(input_file)], capture_output=True, text=True)
    assert overwrite.returncode == 2 and input_file.read_bytes() == original
    input_file.write_text("PRIVATE_SENTINEL invalid JSON", encoding="utf-8")
    invalid_output = Path(directory) / "invalid-summary.json"
    invalid = subprocess.run(command + [str(invalid_output)], capture_output=True, text=True)
    assert invalid.returncode == 2 and not invalid_output.exists()
    assert "PRIVATE_SENTINEL" not in invalid.stderr
print("PASS: repair scopes, durations, redaction, path signature, CLI round trip, invalid input, overwrite protection")
