from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_direct_youtube_upload_is_not_public_by_default() -> None:
    source = (ROOT / "actions" / "upload_to_youtube.py").read_text(encoding="utf-8")

    assert 'DEFAULT_PRIVACY_STATUS = "private"' in source
    assert "dry_run=True" in source
    assert "confirm_upload=True" in source
    assert "--confirm-upload" in source
    assert '"privacyStatus": privacy_status' in source
    assert "--confirm-public-upload" in source
    assert '"privacyStatus": "public"' not in source


def test_default_requirements_stay_minimal() -> None:
    source = (ROOT / "requirements.txt").read_text(encoding="utf-8")

    assert "-r requirements-minimal.txt" in source
    assert "torch" not in source
    assert "transformers" not in source


def test_context_recovery_demo_runs_without_external_dependencies() -> None:
    demo_path = ROOT / "examples" / "context_recovery_demo.py"
    spec = importlib.util.spec_from_file_location("context_recovery_demo", demo_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    note = module.build_context_recovery_note("Settled decision: keep it small.\nUnresolved question: what next?\n")

    assert "Context Recovery Note" in note
    assert "Current Goal" in note
    assert "Settled Decisions" in note
    assert "Files Or Context To Inspect First" in note
    assert "Unresolved Questions" in note
    assert "What Not To Reopen Unless Evidence Changes" in note
    assert "Next Smallest Action" in note
