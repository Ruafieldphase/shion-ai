#!/usr/bin/env python3
"""
🚪 Quality Gate — 결과물의 '감각적 검증'
==========================================
에이전트가 "성공했다"고 선언하기 전에, 출력물의 물리적 속성을
검사하여 거짓 성공을 구조적으로 차단합니다.

사용법:
    from quality_gate import QualityGate
    gate = QualityGate()
    result = gate.verify_file(path, {"min_size_bytes": 1024})
    if not result["passed"]:
        # 실패 사실을 사용자에게 보고
"""

import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger("QualityGate")


class QualityGate:
    """결과물의 물리적/논리적 품질을 검증하는 관문."""

    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or (Path(__file__).resolve().parents[1] / "outputs" / "quality_gate_logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def verify_file(self, path: Path, rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        파일의 물리적 속성을 검증합니다.

        rules 키:
            min_size_bytes (int): 최소 파일 크기
            max_size_bytes (int): 최대 파일 크기
            expected_extension (str): 기대하는 확장자 (예: ".mp4")
            expected_keys (list): JSON 파일의 필수 키 목록
            must_contain (list[str]): 텍스트 파일에 반드시 포함되어야 할 문자열
            must_not_contain (list[str]): 포함되면 안 되는 문자열 (에러 마커 등)
        """
        result = {
            "passed": True,
            "failures": [],
            "path": str(path),
            "timestamp": datetime.now().isoformat(),
        }

        # 1. 존재 여부
        if not path.exists():
            result["passed"] = False
            result["failures"].append("FILE_NOT_FOUND")
            self._log_result(result)
            return result

        # 2. 파일 크기
        size = path.stat().st_size
        result["size_bytes"] = size

        min_size = rules.get("min_size_bytes", 1)
        if size < min_size:
            result["passed"] = False
            result["failures"].append(f"TOO_SMALL: {size}B < {min_size}B")

        max_size = rules.get("max_size_bytes")
        if max_size and size > max_size:
            result["passed"] = False
            result["failures"].append(f"TOO_LARGE: {size}B > {max_size}B")

        # 3. 확장자
        expected_ext = rules.get("expected_extension")
        if expected_ext and path.suffix.lower() != expected_ext.lower():
            result["passed"] = False
            result["failures"].append(f"WRONG_EXTENSION: got '{path.suffix}', expected '{expected_ext}'")

        # 4. JSON 구조 검증
        expected_keys = rules.get("expected_keys")
        if expected_keys and path.suffix.lower() == ".json":
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                missing = [k for k in expected_keys if k not in data]
                if missing:
                    result["passed"] = False
                    result["failures"].append(f"MISSING_KEYS: {missing}")
            except json.JSONDecodeError as e:
                result["passed"] = False
                result["failures"].append(f"INVALID_JSON: {e}")

        # 5. 텍스트 내용 검증
        if rules.get("must_contain") or rules.get("must_not_contain"):
            try:
                content = path.read_text(encoding="utf-8", errors="replace")

                for phrase in rules.get("must_contain", []):
                    if phrase not in content:
                        result["passed"] = False
                        result["failures"].append(f"MISSING_CONTENT: '{phrase}'")

                for phrase in rules.get("must_not_contain", []):
                    if phrase in content:
                        result["passed"] = False
                        result["failures"].append(f"FORBIDDEN_CONTENT: '{phrase}'")
            except Exception as e:
                result["passed"] = False
                result["failures"].append(f"READ_ERROR: {e}")

        self._log_result(result)
        return result

    def verify_video(self, path: Path) -> Dict[str, Any]:
        """FFprobe로 영상의 실제 길이/스트림을 검증합니다."""
        result = {
            "passed": False,
            "failures": [],
            "path": str(path),
            "timestamp": datetime.now().isoformat(),
        }

        if not path.exists():
            result["failures"].append("FILE_NOT_FOUND")
            self._log_result(result)
            return result

        try:
            cmd = [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                str(path),
            ]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if r.returncode != 0:
                result["failures"].append(f"FFPROBE_FAILED: {r.stderr[:200]}")
                self._log_result(result)
                return result

            info = json.loads(r.stdout)
            duration = float(info.get("format", {}).get("duration", 0))
            streams = info.get("streams", [])
            has_video = any(s.get("codec_type") == "video" for s in streams)
            has_audio = any(s.get("codec_type") == "audio" for s in streams)

            result["duration_sec"] = round(duration, 2)
            result["has_video"] = has_video
            result["has_audio"] = has_audio
            result["stream_count"] = len(streams)

            if duration < 1.0:
                result["failures"].append(f"TOO_SHORT: {duration:.1f}s")
            if not has_video:
                result["failures"].append("NO_VIDEO_STREAM")

            result["passed"] = len(result["failures"]) == 0

        except FileNotFoundError:
            result["failures"].append("FFPROBE_NOT_INSTALLED")
        except subprocess.TimeoutExpired:
            result["failures"].append("FFPROBE_TIMEOUT")
        except Exception as e:
            result["failures"].append(f"UNEXPECTED: {e}")

        self._log_result(result)
        return result

    def verify_subprocess(
        self,
        cmd: List[str],
        expected_output: Optional[Path] = None,
        output_rules: Optional[Dict] = None,
        timeout: int = 120,
    ) -> Dict[str, Any]:
        """
        subprocess를 실행하고, 종료 코드 + 출력물을 함께 검증합니다.
        기존의 subprocess.run(check=True) 를 대체합니다.
        """
        result = {
            "cmd": " ".join(cmd),
            "timestamp": datetime.now().isoformat(),
            "passed": False,
            "failures": [],
        }

        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=timeout, encoding="utf-8", errors="replace",
            )
            result["returncode"] = proc.returncode
            result["stderr_preview"] = proc.stderr[:500] if proc.stderr else ""
            result["stdout_preview"] = proc.stdout[:500] if proc.stdout else ""

            if proc.returncode != 0:
                result["failures"].append(f"EXIT_CODE_{proc.returncode}: {proc.stderr[:200]}")
            elif expected_output and output_rules:
                file_check = self.verify_file(expected_output, output_rules)
                if not file_check["passed"]:
                    result["failures"].extend(file_check["failures"])
                result["output_check"] = file_check
            else:
                # 종료 코드 0이고, 출력 검증 규칙 없으면 통과
                pass

            result["passed"] = len(result["failures"]) == 0

        except subprocess.TimeoutExpired:
            result["failures"].append(f"TIMEOUT: {timeout}s")
        except Exception as e:
            result["failures"].append(f"EXECUTION_ERROR: {e}")

        self._log_result(result)
        return result

    def _log_result(self, result: Dict[str, Any]):
        """검증 결과를 로그 파일에 기록합니다."""
        status = "PASS" if result.get("passed") else "FAIL"
        target = result.get("path") or result.get("cmd", "unknown")
        logger.info(f"🚪 [{status}] {target}")
        if not result.get("passed"):
            logger.warning(f"   Failures: {result.get('failures')}")

        # 실패 시 파일로도 기록
        if not result.get("passed"):
            log_file = self.log_dir / f"fail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                log_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass


if __name__ == "__main__":
    # 셀프 테스트
    gate = QualityGate()
    root = Path(__file__).resolve().parents[1]

    # 1. mitochondria_state.json 검증
    mito_path = root / "outputs" / "mitochondria_state.json"
    r = gate.verify_file(mito_path, {
        "min_size_bytes": 10,
        "expected_extension": ".json",
    })
    print(f"Mito check: {'✅ PASS' if r['passed'] else '❌ FAIL'} — {r.get('failures', [])}")

    # 2. entropy 검증
    entropy_path = root / "outputs" / "body_entropy_latest.json"
    r = gate.verify_file(entropy_path, {
        "min_size_bytes": 10,
        "expected_keys": ["entropy", "state"],
    })
    print(f"Entropy check: {'✅ PASS' if r['passed'] else '❌ FAIL'} — {r.get('failures', [])}")

