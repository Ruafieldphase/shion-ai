import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import scripts.participant_frequency_field as frequency
import shader_feedback_server as server


def patch_paths(monkeypatch, tmp_path):
    out_path = tmp_path / "outputs" / "participant_frequency_field_latest.json"
    log_path = tmp_path / "outputs" / "participant_frequency_field.jsonl"
    lock_path = tmp_path / "outputs" / ".participant_frequency_field.lock"
    monkeypatch.setattr(frequency, "ROOT", tmp_path)
    monkeypatch.setattr(frequency, "OUT_PATH", out_path)
    monkeypatch.setattr(frequency, "LOG_PATH", log_path)
    monkeypatch.setattr(frequency, "LOCK_PATH", lock_path)
    monkeypatch.setattr(server, "PARTICIPANT_FREQUENCY_FIELD_PATH", out_path)


def test_server_records_participant_frequency_upload(monkeypatch, tmp_path):
    patch_paths(monkeypatch, tmp_path)

    result = server.record_participant_frequency_payload(
        {
            "participant_id": "luvit",
            "phase": 0.18,
            "amplitude": 0.88,
            "current_pressure": 0.66,
            "field_confidence": 0.91,
        }
    )

    assert result["ok"] is True
    assert result["field"]["uploaded_count"] == 1
    assert server.synthesize_participant_frequency_field()["uploaded_count"] == 1
