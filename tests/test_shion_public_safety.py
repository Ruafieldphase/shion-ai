from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys


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


def test_paths_example_loads_without_external_dependencies() -> None:
    config_path = ROOT / "config" / "paths.example.yaml"
    resolver_path = ROOT / "core" / "path_config.py"
    spec = importlib.util.spec_from_file_location("shion_path_config", resolver_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    previous = os.environ.get("SHION_ROOT")
    previous_agi = os.environ.get("AGI_WORKSPACE_ROOT")
    os.environ.pop("SHION_ROOT", None)
    os.environ.pop("AGI_WORKSPACE_ROOT", None)
    try:
        values = module.load_path_config(config_path)
        resolved = module.resolve_paths(config_path)
    finally:
        if previous is not None:
            os.environ["SHION_ROOT"] = previous
        if previous_agi is not None:
            os.environ["AGI_WORKSPACE_ROOT"] = previous_agi

    assert values["shion_root"] == "."
    assert values["outputs"] == "outputs"
    assert resolved["shion_root"] == ROOT.resolve()
    assert resolved["outputs"] == (ROOT / "outputs").resolve()
    assert resolved["archive_workspace"] is None

    previous = os.environ.get("SHION_ROOT")
    previous_agi = os.environ.get("AGI_WORKSPACE_ROOT")
    os.environ["SHION_ROOT"] = str(ROOT / "custom_shion")
    os.environ.pop("AGI_WORKSPACE_ROOT", None)
    try:
        overridden = module.resolve_paths(config_path)
    finally:
        if previous is None:
            os.environ.pop("SHION_ROOT", None)
        else:
            os.environ["SHION_ROOT"] = previous
        if previous_agi is not None:
            os.environ["AGI_WORKSPACE_ROOT"] = previous_agi

    assert overridden["shion_root"] == (ROOT / "custom_shion").resolve()


def test_path_config_keeps_shion_root_separate_from_agi_root() -> None:
    resolver_path = ROOT / "core" / "path_config.py"
    spec = importlib.util.spec_from_file_location("shion_path_config_env", resolver_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    previous_shion = os.environ.get("SHION_ROOT")
    previous_agi = os.environ.get("AGI_WORKSPACE_ROOT")
    os.environ.pop("SHION_ROOT", None)
    os.environ["AGI_WORKSPACE_ROOT"] = str(ROOT / "external_agi")
    try:
        assert module.get_workspace_root() == ROOT.resolve()
    finally:
        if previous_shion is not None:
            os.environ["SHION_ROOT"] = previous_shion
        else:
            os.environ.pop("SHION_ROOT", None)
        if previous_agi is not None:
            os.environ["AGI_WORKSPACE_ROOT"] = previous_agi
        else:
            os.environ.pop("AGI_WORKSPACE_ROOT", None)


def test_sleep_cycle_integrator_uses_path_config_for_outputs_and_ledger(tmp_path) -> None:
    shion_root = tmp_path / "shion"
    agi_root = tmp_path / "agi"
    config_dir = shion_root / "config"
    config_dir.mkdir(parents=True)
    agi_root.mkdir()
    (config_dir / "paths.example.yaml").write_text(
        "\n".join(
            [
                "paths:",
                '  shion_root: "."',
                '  agi_workspace_root: "../agi"',
                '  outputs: "outputs"',
                '  memory: "memory"',
                '  logs: "logs"',
                '  credentials: "config/credentials"',
                '  archive_workspace: ""',
            ]
        ),
        encoding="utf-8",
    )

    previous_shion = os.environ.get("SHION_ROOT")
    previous_agi = os.environ.get("AGI_WORKSPACE_ROOT")
    os.environ["SHION_ROOT"] = str(shion_root)
    os.environ["AGI_WORKSPACE_ROOT"] = str(agi_root)
    sys.path.insert(0, str(ROOT))
    try:
        integrator_path = ROOT / "core" / "sleep_cycle_integrator.py"
        spec = importlib.util.spec_from_file_location("sleep_cycle_integrator_paths", integrator_path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        if str(ROOT) in sys.path:
            sys.path.remove(str(ROOT))
        if previous_shion is not None:
            os.environ["SHION_ROOT"] = previous_shion
        else:
            os.environ.pop("SHION_ROOT", None)
        if previous_agi is not None:
            os.environ["AGI_WORKSPACE_ROOT"] = previous_agi
        else:
            os.environ.pop("AGI_WORKSPACE_ROOT", None)

    assert module.SHION_ROOT == shion_root.resolve()
    assert module.OUTPUTS_DIR == (shion_root / "outputs").resolve()
    assert module.AGI_ROOT == agi_root.resolve()
    assert module.LEDGER_PATH == (agi_root / "memory" / "resonance_ledger.jsonl").resolve()
