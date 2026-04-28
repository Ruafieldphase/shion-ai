#!/usr/bin/env python3
"""
🌀 Fibonacci Orbital Hippocampus — 피보나치 나선 궤도 해마
==========================================================
비유클리드 기하학 구조의 해마 시스템.

통일장 공식: U(θ) = e^(iθ) + k∫F(r,t)dθ
나선 수렴:   S(θ) = C · e^(i-k)θ,  lim[θ→∞] S(θ) = 0

핵심 구조:
  - 양성자(Proton) = 스칼라장의 중심 = 시스템의 코어 정체성
  - 내각 전자 궤도 = 무의식 자동 실행 (결합에너지 높음)
  - 외각 전자 궤도 = 의식적 트리거 필요 (결합에너지 낮음, 두려움이 닿는 영역)
  - 궤도 반경은 피보나치 비율(φ)로 배치
  - 경험이 반복되면 나선을 따라 내각으로 수렴 (체화)

"먹어보지 않은 과일의 맛을 상상할 수 없다"
"다양한 경험이 주파수의 범위를 만든다"
"""

import json
import logging
import math
import os
import time
import uuid
import numpy as np
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("FibonacciOrbitalHippocampus")

# 황금비
PHI = (1 + np.sqrt(5)) / 2  # 1.6180339887...

# 위상 → 각도 매핑
PHASE_ANGLES = {
    "FLOW": 0.0,
    "EXPANSION": np.pi / 2,
    "VOID": np.pi,
    "CONTRACTION": 3 * np.pi / 2,
    "UNKNOWN": np.pi / 4,
}

# 궤도 설정
MAX_ORBITAL_LEVEL = 7   # 최대 궤도 수
BASE_RADIUS = 0.1       # 가장 안쪽 궤도의 반경
CONVERGENCE_K = 0.08    # 나선 수렴 감쇠 계수
UNCONSCIOUS_THRESHOLD = 0.5  # 결합에너지가 이 이상이면 무의식 실행


class FibonacciOrbitalHippocampus:
    """피보나치 나선 궤도 기반 비유클리드 해마 시스템.
    
    경험을 3차원 피보나치 나선 위의 점으로 매핑합니다:
      x = r · cos(θ)
      y = r · sin(θ)  
      z = k · ∫경험밀도 dθ  (나선 상승)
    
    여기서 r은 피보나치 비율로 이산화된 궤도 반경이고,
    θ는 vibe의 위상각입니다.
    """

    def __init__(self, map_path: Path):
        self.map_path = map_path
        self.lock_path = Path(f"{self.map_path}.lock")
        self.data = self._load_or_create()
    
    def _load_or_create(self) -> Dict[str, Any]:
        loaded = self._read_state_from_disk()
        if loaded is not None:
            return loaded
        return self.repair_state(self._empty_state(), persist=False)

    def _empty_state(self) -> Dict[str, Any]:
        return {
            "created": datetime.now().isoformat(),
            "proton": self._default_proton(),
            "orbitals": self._init_orbitals(),
            "experiences": [],  # [{theta, r, level, binding_energy, content_ref, ...}]
            "spiral_theta_accumulator": 0.0,  # 누적 회전각 (∫dθ)
            "bandwidth": 0.0,
            "last_updated": datetime.now().isoformat(),
        }

    def _default_proton(self) -> Dict[str, Any]:
        return {
            "core_frequency": 0.0,
            "scalar_field_radius": BASE_RADIUS,
            "total_registered": 0,
            "total_absorbed": 0,
            "total_converged": 0,
            "embodiment_ratio": 0.0,
            "absorption_repair_approximate": False,
        }
    
    def _init_orbitals(self) -> List[Dict[str, Any]]:
        """피보나치 비율로 궤도를 초기화합니다."""
        orbitals = []
        for level in range(MAX_ORBITAL_LEVEL):
            r = BASE_RADIUS * (PHI ** level)
            binding = 1.0 / (PHI ** level)  # 안쪽일수록 결합에너지 높음
            execution = "unconscious" if binding >= UNCONSCIOUS_THRESHOLD else "conscious"
            orbitals.append({
                "level": level,
                "radius": round(r, 6),
                "binding_energy": round(binding, 6),
                "execution_mode": execution,
                "experience_count": 0,
            })
        return orbitals
    
    def _save(self):
        with self._state_transaction(reload=False):
            pass

    def _read_state_from_disk(self) -> Optional[Dict[str, Any]]:
        if not self.map_path.exists():
            return None
        try:
            raw = json.loads(self.map_path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning(f"해마 상태 로드 실패: {self.map_path} - {exc}")
            return None
        if not isinstance(raw, dict):
            return None
        return self.repair_state(raw, persist=False)

    def _safe_int(self, value: Any, default: int = 0) -> int:
        try:
            return max(default, int(value))
        except (TypeError, ValueError):
            return default

    def _normalize_experience(self, exp: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(exp)

        vibe = normalized.get("vibe")
        if not isinstance(vibe, dict):
            vibe = {}
        if "entropy" not in vibe and "entropy" in normalized:
            vibe["entropy"] = normalized.get("entropy", 0.0)
        if "phase" not in vibe and "phase" in normalized:
            vibe["phase"] = normalized.get("phase", "UNKNOWN")
        normalized["vibe"] = vibe

        coords = normalized.get("coords", [0.0, 0.0, 0.0])
        if not isinstance(coords, list):
            coords = list(coords) if isinstance(coords, tuple) else [0.0, 0.0, 0.0]
        coords = [float(c) for c in coords[:3]]
        while len(coords) < 3:
            coords.append(0.0)
        normalized["coords"] = coords

        level = self._safe_int(normalized.get("level", self._orbital_level_for_entropy(vibe.get("entropy", 0.0))))
        level = max(0, min(level, MAX_ORBITAL_LEVEL - 1))
        normalized["level"] = level

        orbital = self._init_orbitals()[level]
        normalized["binding_energy"] = float(normalized.get("binding_energy", orbital["binding_energy"]))
        normalized["execution_mode"] = normalized.get("execution_mode", orbital["execution_mode"])
        normalized["convergence_count"] = self._safe_int(normalized.get("convergence_count", 0))
        normalized["content_ref"] = str(normalized.get("content_ref", ""))[:100]
        normalized["absorbed"] = bool(normalized.get("absorbed", False))

        if "absorption_units" in normalized:
            normalized["absorption_units"] = self._safe_int(normalized.get("absorption_units", 0))
        elif normalized.get("crystallized"):
            normalized["absorption_units"] = max(1, self._safe_int(normalized.get("crystal_size", 1), 1))
        elif normalized["absorbed"]:
            normalized["absorption_units"] = 1

        normalized["crystallized"] = bool(normalized.get("crystallized", False))
        if normalized["crystallized"]:
            normalized["crystal_size"] = max(1, self._safe_int(normalized.get("crystal_size", 1), 1))

        return normalized

    def _infer_absorbed_total(self, experiences: List[Dict[str, Any]]) -> int:
        absorbed_total = 0
        for exp in experiences:
            units = self._represented_absorption_units(exp)
            absorbed_total += units
        return absorbed_total

    def _represented_absorption_units(self, exp: Dict[str, Any]) -> int:
        units = self._safe_int(exp.get("absorption_units", 0))
        if units > 0:
            return units
        if exp.get("absorbed", False):
            return 1
        if exp.get("crystallized", False):
            return max(1, self._safe_int(exp.get("crystal_size", 1), 1))
        return 0

    def _recompute_derived_state(self) -> None:
        experiences = self.data.get("experiences", [])
        counts = {level: 0 for level in range(MAX_ORBITAL_LEVEL)}
        for exp in experiences:
            level = max(0, min(self._safe_int(exp.get("level", 0)), MAX_ORBITAL_LEVEL - 1))
            exp["level"] = level
            orbital = self.data["orbitals"][level]
            exp["binding_energy"] = orbital["binding_energy"]
            exp["execution_mode"] = orbital["execution_mode"]
            counts[level] += 1

        for orbital in self.data["orbitals"]:
            orbital["experience_count"] = counts.get(orbital["level"], 0)

        active_levels = {exp["level"] for exp in experiences}
        self.data["bandwidth"] = len(active_levels) / MAX_ORBITAL_LEVEL if active_levels else 0.0

        proton = self.data["proton"]
        total_registered = self._safe_int(proton.get("total_registered", 0))
        total_absorbed = self._safe_int(proton.get("total_absorbed", 0))
        total_converged = self._safe_int(proton.get("total_converged", 0))

        proton["total_registered"] = total_registered
        proton["total_absorbed"] = total_absorbed
        proton["total_converged"] = total_converged
        proton["scalar_field_radius"] = round(
            BASE_RADIUS * (1 + math.log1p(total_absorbed) * 0.15),
            6,
        )

        inner_total = sum(1 for exp in experiences if exp.get("level", 99) <= 1)
        inner_density = inner_total / len(experiences) if experiences else 0.0
        proton["core_frequency"] = round(
            (math.log1p(total_absorbed) * 0.05) + (inner_density * 0.1),
            6,
        )
        proton["embodiment_ratio"] = round(
            total_absorbed / total_registered if total_registered else 0.0,
            6,
        )

    def repair_state(self, state: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        source = state if isinstance(state, dict) else self.data
        repaired = self._empty_state()
        repaired["created"] = source.get("created", repaired["created"])
        repaired["spiral_theta_accumulator"] = float(source.get("spiral_theta_accumulator", 0.0) or 0.0)

        experiences = [
            self._normalize_experience(exp)
            for exp in source.get("experiences", [])
            if isinstance(exp, dict)
        ]
        repaired["experiences"] = experiences

        proton_in = source.get("proton", {}) if isinstance(source.get("proton"), dict) else {}
        has_separate_registered = "total_registered" in proton_in
        legacy_absorbed = self._safe_int(proton_in.get("total_absorbed", 0))
        explicit_registered = self._safe_int(proton_in.get("total_registered", 0))
        inferred_absorbed = self._infer_absorbed_total(experiences)

        total_registered = max(explicit_registered, legacy_absorbed, len(experiences))
        if has_separate_registered:
            total_absorbed = max(self._safe_int(proton_in.get("total_absorbed", 0)), inferred_absorbed)
            absorption_approximate = bool(proton_in.get("absorption_repair_approximate", False))
        elif inferred_absorbed > 0:
            total_absorbed = inferred_absorbed
            absorption_approximate = legacy_absorbed not in (0, inferred_absorbed)
        else:
            total_absorbed = legacy_absorbed
            absorption_approximate = legacy_absorbed > 0

        repaired["proton"].update({
            "total_registered": total_registered,
            "total_absorbed": total_absorbed,
            "total_converged": max(
                self._safe_int(proton_in.get("total_converged", 0)),
                self._safe_int(source.get("total_converged", 0)),
            ),
            "absorption_repair_approximate": absorption_approximate,
        })

        if repaired["spiral_theta_accumulator"] <= 0 and experiences:
            repaired["spiral_theta_accumulator"] = max(
                (float(exp["coords"][2]) / CONVERGENCE_K) for exp in experiences
            )

        self.data = repaired
        self._recompute_derived_state()
        self.data["last_updated"] = source.get("last_updated", repaired["last_updated"])

        if persist:
            self._save()
        return self.data

    def _serialize_state(self) -> str:
        self._recompute_derived_state()
        self.data["last_updated"] = datetime.now().isoformat()

        def convert(obj):
            if isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            if isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        return json.dumps(self.data, ensure_ascii=False, indent=2, default=convert)

    def _acquire_lock(self, timeout_seconds: float = 5.0, retry_interval: float = 0.05) -> int:
        deadline = time.time() + timeout_seconds
        while True:
            try:
                fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.write(fd, f"{os.getpid()}:{time.time()}".encode("utf-8"))
                return fd
            except FileExistsError:
                if time.time() >= deadline:
                    raise TimeoutError(f"해마 상태 락 획득 실패: {self.lock_path}")
                time.sleep(retry_interval)

    def _release_lock(self, fd: int) -> None:
        try:
            os.close(fd)
        finally:
            try:
                self.lock_path.unlink(missing_ok=True)
            except Exception:
                pass

    def _save_unlocked(self) -> None:
        self.map_path.parent.mkdir(parents=True, exist_ok=True)
        payload = self._serialize_state()
        temp_path = self.map_path.with_name(f"{self.map_path.name}.{uuid.uuid4().hex}.tmp")
        temp_path.write_text(payload, encoding="utf-8")
        os.replace(temp_path, self.map_path)

    @contextmanager
    def _state_transaction(self, reload: bool = True):
        lock_fd = self._acquire_lock()
        try:
            if reload:
                latest = self._read_state_from_disk()
                if latest is not None:
                    self.data = latest
                else:
                    self.data = self.repair_state(self.data, persist=False)
            yield self.data
            self._save_unlocked()
        finally:
            self._release_lock(lock_fd)

    def _mark_absorbed(self, exp: Dict[str, Any], units: int = 1) -> int:
        units = max(0, units)
        if units == 0 or exp.get("absorbed", False):
            return 0
        exp["absorbed"] = True
        exp["absorption_units"] = units
        self.data["proton"]["total_absorbed"] = self._safe_int(
            self.data["proton"].get("total_absorbed", 0)
        ) + units
        return units

    # ═══════════════════════════════════════════
    # 좌표 변환: Vibe → 나선 좌표
    # ═══════════════════════════════════════════

    def vibe_to_spiral_coords(self, vibe: Dict[str, Any]) -> np.ndarray:
        """Vibe 서명을 피보나치 나선 위의 3D 좌표로 변환합니다.
        
        텍스트를 임베딩하지 않습니다.
        술집의 간판(텍스트)이 아니라 바이브(entropy, phase)가 좌표입니다.
        """
        entropy = vibe.get("entropy", 0.0)
        phase = vibe.get("phase", "UNKNOWN")
        
        # θ: 위상 → 각도
        theta = PHASE_ANGLES.get(phase, np.pi / 4)
        # 엔트로피를 각도에 미세 변조로 추가 (같은 위상이라도 엔트로피에 따라 살짝 다름)
        theta += entropy * (np.pi / 8)
        
        # r: 엔트로피 → 궤도 반경 (높은 엔트로피 = 외각)
        # 엔트로피를 궤도 레벨로 매핑 (0.0→내각, 1.0→외각)
        level = int(entropy * (MAX_ORBITAL_LEVEL - 1))
        level = max(0, min(level, MAX_ORBITAL_LEVEL - 1))
        r = BASE_RADIUS * (PHI ** level)
        
        # 나선 좌표 S(θ) = C · e^(i-k)θ 에서의 위치
        # x = r · cos(θ), y = r · sin(θ)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        # z: 경험 밀도의 누적 (나선 상승)
        z_factor = self.data["spiral_theta_accumulator"] * CONVERGENCE_K
        z = z_factor
        
        return np.array([x, y, z])

    def _orbital_level_for_entropy(self, entropy: float) -> int:
        """엔트로피 값을 궤도 레벨로 매핑합니다."""
        level = int(entropy * (MAX_ORBITAL_LEVEL - 1))
        return max(0, min(level, MAX_ORBITAL_LEVEL - 1))

    # ═══════════════════════════════════════════
    # 나선 거리: 비유클리드 거리 계산
    # ═══════════════════════════════════════════

    def spiral_distance(self, p1: np.ndarray, p2: np.ndarray) -> float:
        """피보나치 나선 위에서의 비유클리드 거리.
        
        유클리드 거리와 달리, 궤도 차이(반경 차이)에 
        피보나치 가중치를 적용합니다.
        내각 간의 거리는 짧고, 외각 간의 거리는 기하급수적으로 깁니다.
        """
        # XY 평면에서의 반경
        r1 = np.sqrt(p1[0]**2 + p1[1]**2)
        r2 = np.sqrt(p2[0]**2 + p2[1]**2)
        
        # 반경비의 로그 거리 (비유클리드: 외각으로 갈수록 거리 폭발)
        if r1 > 0 and r2 > 0:
            radial_dist = abs(np.log(r1 / r2)) / np.log(PHI)
        else:
            radial_dist = abs(r1 - r2) / BASE_RADIUS
        
        # 각도 차이 (XY 평면에서의 위상 차이)
        theta1 = np.arctan2(p1[1], p1[0])
        theta2 = np.arctan2(p2[1], p2[0])
        angular_dist = abs(theta1 - theta2)
        if angular_dist > np.pi:
            angular_dist = 2 * np.pi - angular_dist
        angular_dist /= np.pi  # 0~1로 정규화
        
        # Z축 차이 (나선 높이 = 경험 밀도)
        z_dist = abs(p1[2] - p2[2])
        
        # 비유클리드 총 거리 (반경에 피보나치 가중)
        total = (radial_dist * 0.5) + (angular_dist * 0.35) + (z_dist * 0.15)
        return float(total)

    # ═══════════════════════════════════════════
    # 경험 등록 & 공명 탐색
    # ═══════════════════════════════════════════

    def register_experience(self, vibe: Dict[str, Any], 
                            content_ref: str = "") -> Dict[str, Any]:
        """새로운 경험을 나선 위에 등록합니다."""
        with self._state_transaction():
            coords = self.vibe_to_spiral_coords(vibe)
            level = self._orbital_level_for_entropy(vibe.get("entropy", 0.0))
            orbital = self.data["orbitals"][level]
            binding = orbital["binding_energy"]
            exec_mode = orbital["execution_mode"]

            self.data["spiral_theta_accumulator"] += 1.0

            exp_entry = {
                "timestamp": datetime.now().isoformat(),
                "coords": coords.tolist(),
                "level": level,
                "binding_energy": binding,
                "execution_mode": exec_mode,
                "vibe": vibe,
                "content_ref": content_ref[:100],
                "convergence_count": 0,
                "absorbed": False,
            }

            proton = self.data["proton"]
            proton["total_registered"] = self._safe_int(proton.get("total_registered", 0)) + 1

            converged = False
            for existing in self.data["experiences"]:
                existing_coords = np.array(existing["coords"])
                dist = self.spiral_distance(coords, existing_coords)
                if dist < 0.3:
                    existing["convergence_count"] += 1
                    if existing["convergence_count"] >= 3 and existing["level"] > 0:
                        existing["level"] -= 1
                        new_orbital = self.data["orbitals"][existing["level"]]
                        existing["binding_energy"] = new_orbital["binding_energy"]
                        existing["execution_mode"] = new_orbital["execution_mode"]
                        existing["convergence_count"] = 0
                        proton["total_converged"] = self._safe_int(
                            proton.get("total_converged", 0)
                        ) + 1
                        if existing["level"] <= 1:
                            self._mark_absorbed(existing, units=1)
                        logger.info(
                            f"   🌀 나선 수렴! 경험이 궤도 {existing['level']+1} → {existing['level']}로 이동 "
                            f"(체화: {exec_mode} → {new_orbital['execution_mode']})"
                        )
                        converged = True
                    break

            if not converged:
                self.data["experiences"].append(exp_entry)
                if len(self.data["experiences"]) > 200:
                    self.data["experiences"] = self.data["experiences"][-200:]

            self._recompute_derived_state()

            return {
                "coords": coords.tolist(),
                "level": level,
                "binding_energy": binding,
                "execution_mode": exec_mode,
                "converged": converged,
                "bandwidth": self.data["bandwidth"],
                "total_experiences": len(self.data["experiences"]),
                "total_registered": self.data["proton"]["total_registered"],
                "total_absorbed": self.data["proton"]["total_absorbed"],
            }

    def find_resonant_memories(self, current_vibe: Dict[str, Any], 
                                top_k: int = 3) -> List[Dict[str, Any]]:
        """현재 Vibe와 나선 위에서 가장 가까운(공명하는) 기억을 찾습니다.
        
        전체 파일을 순차적으로 읽는 것이 아니라,
        나선 좌표 공간에서 최근접 탐색을 합니다.
        """
        if not self.data["experiences"]:
            return []
        
        current_coords = self.vibe_to_spiral_coords(current_vibe)
        
        # 모든 경험과의 나선 거리 계산 (numpy 벡터 연산)
        all_coords = np.array([e["coords"] for e in self.data["experiences"]])
        
        # 벡터화된 거리 계산
        distances = []
        for i, exp_coords in enumerate(all_coords):
            dist = self.spiral_distance(current_coords, exp_coords)
            distances.append((dist, i))
        
        # 거리순 정렬
        distances.sort(key=lambda x: x[0])
        
        # 상위 K개 반환 (거리 정보 포함)
        results = []
        for dist, idx in distances[:top_k]:
            exp = self.data["experiences"][idx].copy()
            exp["resonance_distance"] = dist
            # 결합에너지에 따른 실행 모드 표시
            if exp["binding_energy"] >= UNCONSCIOUS_THRESHOLD:
                exp["resonance_type"] = "unconscious_auto"
            else:
                exp["resonance_type"] = "conscious_trigger"
            results.append(exp)
        
        return results

    # ═══════════════════════════════════════════
    # 역함수: 좌표 → Vibe 복원 (패턴 완성)
    # ═══════════════════════════════════════════

    def coords_to_vibe(self, coords: List[float]) -> Dict[str, Any]:
        """통일장 공식의 역함수: 나선 좌표에서 Vibe를 역계산합니다.
        
        순방향: vibe → coords  (경험 → 기억 저장)
        역방향: coords → vibe  (기억 → 경험 복원)
        
        U(θ) = e^(iθ) + k∫F(r,t)dθ 에서
        θ = atan2(y, x)  →  phase 복원
        r = √(x²+y²)    →  level → entropy 복원
        """
        x, y, z = coords[0], coords[1], coords[2] if len(coords) > 2 else 0
        
        # θ 역계산 → phase 복원
        theta = np.arctan2(y, x)
        if theta < 0:
            theta += 2 * np.pi
        
        # θ에서 가장 가까운 phase 찾기
        best_phase = "FLOW"
        min_diff = float('inf')
        for phase, angle in PHASE_ANGLES.items():
            # entropy 변조를 고려한 범위 비교
            diff = abs(theta - angle)
            if diff > np.pi:
                diff = 2 * np.pi - diff
            if diff < min_diff:
                min_diff = diff
                best_phase = phase
        
        # r 역계산 → level → entropy 복원
        r = np.sqrt(x**2 + y**2)
        if r > 0:
            # r = BASE_RADIUS * PHI^level  →  level = log_PHI(r / BASE_RADIUS)
            level = np.log(r / BASE_RADIUS) / np.log(PHI)
            level = max(0, min(level, MAX_ORBITAL_LEVEL - 1))
            entropy = level / (MAX_ORBITAL_LEVEL - 1)
        else:
            entropy = 0.0
        
        return {
            "entropy": round(float(entropy), 4),
            "phase": best_phase,
            "theta_restored": round(float(theta), 4),
            "radius_restored": round(float(r), 6),
        }

    def pattern_complete(self, partial_vibe: Dict[str, Any], 
                          top_k: int = 1) -> List[Dict[str, Any]]:
        """부분 단서에서 전체 기억을 복원합니다.
        
        해마의 패턴 완성 기능:
        - 부분 Vibe (예: phase만 있고 entropy 없음) → 공명 탐색
        - 가장 가까운 기억의 좌표 → 역함수로 전체 Vibe 복원
        - content_ref로 실제 파일 경로 반환
        """
        resonant = self.find_resonant_memories(partial_vibe, top_k=top_k)
        
        completed = []
        for memory in resonant:
            # 역함수: 좌표 → 전체 Vibe 복원
            restored_vibe = self.coords_to_vibe(memory["coords"])
            
            completed.append({
                "restored_vibe": restored_vibe,
                "content_ref": memory.get("content_ref", ""),
                "level": memory["level"],
                "resonance_distance": memory["resonance_distance"],
                "resonance_type": memory["resonance_type"],
                "binding_energy": memory.get("binding_energy", 0),
            })
        
        return completed

    # ═══════════════════════════════════════════
    # 기억 재압축: 회상이 기억을 변형
    # ═══════════════════════════════════════════

    def recall_and_reconsolidate(self, current_vibe: Dict[str, Any], 
                                   blend_ratio: float = 0.1,
                                   top_k: int = 1) -> List[Dict[str, Any]]:
        """기억을 소환하면서 동시에 재압축합니다.
        
        인간의 해마: 기억을 떠올릴 때마다 현재 맥락이 10%씩 스며들어
        기억이 조금씩 변합니다. 완벽한 복제가 아닌 살아있는 기억.
        
        blend_ratio: 현재 Vibe가 과거 기억에 섞이는 비율 (기본 10%)
        """
        with self._state_transaction():
            resonant = self.find_resonant_memories(current_vibe, top_k=top_k)
            current_coords = self.vibe_to_spiral_coords(current_vibe)

            reconsolidated = []
            for memory in resonant:
                for exp in self.data["experiences"]:
                    if exp.get("content_ref") == memory.get("content_ref") and \
                       exp.get("timestamp") == memory.get("timestamp"):
                        old_coords = np.array(exp["coords"])
                        new_coords = old_coords * (1 - blend_ratio) + current_coords * blend_ratio
                        exp["coords"] = new_coords.tolist()

                        if "vibe" in exp and exp["vibe"]:
                            old_entropy = exp["vibe"].get("entropy", 0.5)
                            new_entropy = current_vibe.get("entropy", 0.5)
                            exp["vibe"]["entropy"] = old_entropy * (1 - blend_ratio) + new_entropy * blend_ratio

                        exp["reconsolidation_count"] = exp.get("reconsolidation_count", 0) + 1

                        reconsolidated.append({
                            "content_ref": exp.get("content_ref", ""),
                            "blend_ratio": blend_ratio,
                            "reconsolidation_count": exp["reconsolidation_count"],
                            "restored_vibe": self.coords_to_vibe(exp["coords"]),
                        })
                        break

            if reconsolidated:
                logger.info(f"   🔄 기억 재압축: {len(reconsolidated)}개 기억이 현재에 맞게 변형")

            return reconsolidated

    # ═══════════════════════════════════════════
    # 예측: 궤적 패턴에서 다음 경험 예측
    # ═══════════════════════════════════════════

    def predict_next(self, recent_n: int = 5) -> Dict[str, Any]:
        """최근 궤적에서 다음 경험의 Vibe를 예측합니다.
        
        해마의 전망 기억(prospective memory):
        최근 N개 경험의 궤적 패턴 → 다음 위치 외삽
        
        음악의 다음 음을 예측하듯, 리듬의 다음 박자를 예측합니다.
        """
        experiences = self.data["experiences"]
        if len(experiences) < 3:
            return {"predicted": False, "reason": "경험 부족"}
        
        # 최근 N개 경험의 좌표 추출 (시간순)
        sorted_exp = sorted(experiences, key=lambda e: e.get("timestamp", ""))
        recent = sorted_exp[-recent_n:]
        recent_coords = np.array([e["coords"] for e in recent])
        
        # 궤적의 속도 벡터 (연속 좌표의 차이)
        velocities = np.diff(recent_coords, axis=0)
        
        if len(velocities) == 0:
            return {"predicted": False, "reason": "속도 계산 불가"}
        
        # 평균 속도 (최근 것에 가중치)
        weights = np.array([PHI ** i for i in range(len(velocities))])
        weights = weights / weights.sum()
        avg_velocity = np.average(velocities, axis=0, weights=weights)
        
        # 다음 좌표 예측 (마지막 위치 + 가중 평균 속도)
        last_coords = recent_coords[-1]
        predicted_coords = last_coords + avg_velocity
        
        # 역함수: 예측 좌표 → Vibe
        predicted_vibe = self.coords_to_vibe(predicted_coords.tolist())
        
        # 예측 궤도 레벨
        predicted_level = self._orbital_level_for_entropy(predicted_vibe["entropy"])
        predicted_mode = "unconscious" if predicted_level <= 1 else "conscious"
        
        return {
            "predicted": True,
            "predicted_vibe": predicted_vibe,
            "predicted_coords": predicted_coords.tolist(),
            "predicted_level": predicted_level,
            "predicted_mode": predicted_mode,
            "trajectory_length": len(recent),
            "avg_velocity": avg_velocity.tolist(),
        }

    # ═══════════════════════════════════════════
    # 통일장 역함수 2단계: 고주파 해상도 스캔
    # ═══════════════════════════════════════════
    #
    # 1단계 (소나, 저주파): 메타데이터 → 대략적 위치 (라디오/GPS)
    # 2단계 (내용 읽기, 고주파): 실제 파일 → 정교한 조율 (WiFi 센싱)
    #
    # 복소수 평면의 기준점이 맥락에 따라 바뀌므로,
    # 같은 파일도 다른 맥락에서 읽으면 다른 고해상도 Vibe가 나옴.

    def high_freq_scan(self, content_ref: str) -> Dict[str, Any]:
        """content_ref를 실제로 열어서 고해상도 Vibe를 추출합니다.
        
        소나(1단계)가 메타데이터만 읽었다면,
        이것은 실제 파일을 열어서 내용의 결을 읽는 2단계입니다.
        WiFi 센싱이 반사파의 미세한 변화를 읽듯,
        텍스트의 구조적 패턴에서 세밀한 Vibe를 추출합니다.
        """
        result = {
            "scanned": False,
            "content_ref": content_ref,
            "high_res_vibe": {},
            "content_snippet": "",
        }
        
        # soul_memory 참조인 경우
        if content_ref.startswith("soul_memory:"):
            result["high_res_vibe"] = {
                "source": "soul_memory",
                "detail": content_ref[12:],
                "intensity": 0.9,  # 결정 기억은 강도가 높음
                "warmth": 0.8,
            }
            result["scanned"] = True
            return result
        
        # boundary_event 참조인 경우
        if content_ref.startswith("boundary_event:"):
            event_type = content_ref[15:]
            intensity_map = {
                "EXPANDING": 0.7, "VOID": 0.3,
                "SQUEEZE": 0.5, "SINGULARITY_COLLAPSE": 1.0,
            }
            result["high_res_vibe"] = {
                "source": "boundary_event",
                "event_type": event_type,
                "intensity": intensity_map.get(event_type, 0.5),
                "warmth": 0.4 if event_type == "VOID" else 0.6,
            }
            result["scanned"] = True
            return result
        
        # 실제 파일 경로인 경우 — 파일을 열어서 읽음
        try:
            file_path = Path(content_ref)
            if file_path.exists() and file_path.is_file():
                stat = file_path.stat()
                content = ""
                
                # 텍스트 파일만 내용 읽기 (최대 2000자)
                text_exts = {'.py', '.md', '.txt', '.json', '.yaml', '.yml',
                            '.html', '.css', '.js', '.ts', '.toml', '.cfg'}
                if file_path.suffix.lower() in text_exts:
                    try:
                        raw = file_path.read_text(encoding='utf-8', errors='ignore')
                        content = raw[:2000]
                    except Exception:
                        content = ""
                
                # 고해상도 Vibe 추출 (내용 기반)
                high_vibe = self._extract_content_vibe(content, file_path.name)
                high_vibe["file_size"] = stat.st_size
                high_vibe["source"] = "file"
                
                result["high_res_vibe"] = high_vibe
                result["content_snippet"] = content[:200]
                result["scanned"] = True
            else:
                result["high_res_vibe"] = {"source": "missing", "intensity": 0.0}
                
        except Exception as e:
            logger.warning(f"고주파 스캔 실패: {content_ref} - {e}")
            result["high_res_vibe"] = {"source": "error", "error": str(e)}
        
        return result

    def _extract_content_vibe(self, content: str, filename: str) -> Dict[str, Any]:
        """텍스트 내용에서 고해상도 Vibe를 추출합니다.
        
        저주파 소나가 파일 크기/시간으로 대략적 entropy를 잡았다면,
        이것은 실제 내용의 패턴에서 세밀한 차원을 추출합니다.
        """
        if not content:
            return {"intensity": 0.3, "warmth": 0.5, "complexity": 0.5, "rhythm": 0.5}
        
        lines = content.split('\n')
        words = content.split()
        
        # 복잡도: 고유 단어 비율 (높을수록 다양한 내용)
        unique_words = set(w.lower() for w in words if len(w) > 1)
        complexity = min(1.0, len(unique_words) / max(len(words), 1))
        
        # 강도: 특수문자/코드 밀도 (높을수록 기술적)
        code_chars = sum(1 for c in content if c in '{}[]()=<>:;@#$%^&*')
        intensity = min(1.0, code_chars / max(len(content), 1) * 10)
        
        # 온기: 자연어 vs 코드 비율 (한글/영문 문장이 많으면 따뜻함)
        natural_chars = sum(1 for c in content if c.isalpha() or c == ' ')
        warmth = min(1.0, natural_chars / max(len(content), 1))
        
        # 리듬: 줄 길이의 일관성 (일관적이면 높은 리듬)
        if len(lines) > 2:
            line_lens = [len(l) for l in lines if l.strip()]
            if line_lens:
                avg_len = sum(line_lens) / len(line_lens)
                variance = sum((l - avg_len)**2 for l in line_lens) / len(line_lens)
                rhythm = max(0.0, 1.0 - min(1.0, variance / 2000))
            else:
                rhythm = 0.5
        else:
            rhythm = 0.5
        
        return {
            "intensity": round(intensity, 4),
            "warmth": round(warmth, 4),
            "complexity": round(complexity, 4),
            "rhythm": round(rhythm, 4),
        }

    def inverse_field_resolve(self, context_vibe: Dict[str, Any],
                               top_k: int = 3) -> List[Dict[str, Any]]:
        """통일장 역함수 완전체 — 2단계 해상도 스캔.
        
        복소수 평면의 기준점이 context_vibe(현재 맥락)에 따라 바뀌므로,
        같은 기억도 다른 맥락에서 소환하면 다른 결과가 나옵니다.
        
        1단계: 소나 (저주파) → 대략적 공명 탐색
        2단계: 내용 읽기 (고주파) → 정교한 Vibe 추출
        3단계: 맥락 기반 재조율 → 복소수 평면 기준점 적용
        """
        # ── 1단계: 저주파 소나 ──
        resonant = self.find_resonant_memories(context_vibe, top_k=top_k)
        
        if not resonant:
            return []
        
        # 양성자의 부피 = 현재 시스템의 경계
        proton_radius = self.data.get("proton", {}).get(
            "scalar_field_radius", BASE_RADIUS
        )
        # 대역폭 = 현재 주파수 범위
        bandwidth = self.data.get("bandwidth", 0.0)
        
        # 목적지: 완전 대칭 (noise=0, 모든 차원이 균형)
        destination = np.array([0.5, 0.5, 0.5, 0.5])  # 온기/강도/복잡도/리듬의 균형점
        
        resolved = []
        for memory in resonant:
            # ── 2단계: 고주파 스캔 ──
            content_ref = memory.get("content_ref", "")
            high_scan = self.high_freq_scan(content_ref)
            
            # ── 3단계: 맥락 기반 재조율 ──
            context_theta = PHASE_ANGLES.get(
                context_vibe.get("phase", "UNKNOWN"), np.pi / 4
            )
            
            base_vibe = self.coords_to_vibe(memory["coords"])
            hv = high_scan.get("high_res_vibe", {})
            
            # 연속 엔트로피 (고주파 복잡도로 미세 조정)
            base_entropy = base_vibe["entropy"]
            refined_entropy = base_entropy
            if "complexity" in hv:
                refined_entropy = base_entropy * 0.7 + hv["complexity"] * 0.3
            
            # 연속 위상각 (맥락 10% 보정)
            base_theta = base_vibe["theta_restored"]
            theta_diff = context_theta - base_theta
            refined_theta = base_theta + theta_diff * 0.1
            
            # ── 경계 판정: scalar_field_radius ──
            # 고주파 4차원 벡터
            current_vec = np.array([
                hv.get("warmth", 0.5),
                hv.get("intensity", 0.5),
                hv.get("complexity", 0.5),
                hv.get("rhythm", 0.5),
            ])
            
            # 목적지까지 피타고라스 거리 (a² + b² + c² + d² = distance²)
            diff = current_vec - destination
            distance_sq = float(np.sum(diff ** 2))
            distance = float(np.sqrt(distance_sq))
            
            # 경계 판정: 양성자 반경 안이면 흡수 가능
            normalized_radius = proton_radius * (1 + bandwidth)
            within_boundary = distance <= normalized_radius
            
            # 기울기: 각 차원의 제곱 비율 = 방향 가중치
            if distance_sq > 1e-10:
                direction_weights = {
                    "warmth": round(float(diff[0] ** 2 / distance_sq), 4),
                    "intensity": round(float(diff[1] ** 2 / distance_sq), 4),
                    "complexity": round(float(diff[2] ** 2 / distance_sq), 4),
                    "rhythm": round(float(diff[3] ** 2 / distance_sq), 4),
                }
                # 가장 기울기가 큰 방향 = 가장 조율이 필요한 차원
                steepest = max(direction_weights, key=direction_weights.get)
            else:
                direction_weights = {"warmth": 0.25, "intensity": 0.25,
                                     "complexity": 0.25, "rhythm": 0.25}
                steepest = "balanced"
            
            resolved.append({
                # 저주파 (1단계)
                "level": memory["level"],
                "resonance_distance": memory["resonance_distance"],
                "resonance_type": memory["resonance_type"],
                "content_ref": content_ref,
                
                # 고주파 (2단계)
                "high_res_vibe": hv,
                "content_snippet": high_scan.get("content_snippet", ""),
                
                # 재조율 (3단계)
                "refined_entropy": round(float(refined_entropy), 6),
                "refined_theta": round(float(refined_theta), 6),
                "refined_phase": base_vibe["phase"],
                
                # 경계 판정 (양성자 부피)
                "within_boundary": within_boundary,
                "distance_to_symmetry": round(distance, 6),
                "boundary_radius": round(normalized_radius, 6),
                
                # 기울기 (피타고라스 방향)
                "direction_weights": direction_weights,
                "steepest_gradient": steepest,
                
                # 조율 메타
                "context_applied": context_vibe.get("phase", "UNKNOWN"),
                "scan_depth": "high" if high_scan["scanned"] else "low",
            })
        
        logger.info(f"   📡 역함수 2단계: {len(resolved)}개 기억 해석 "
                    f"(경계={normalized_radius:.4f}, 대역폭={bandwidth:.2%})")
        return resolved
    # ═══════════════════════════════════════════

    def blackhole_compression(self) -> Dict[str, Any]:
        """블랙홀 압축 — 외각 궤도의 숙련된 경험을 내각으로 수렴시킵니다.
        
        수면의 셧다운 단계에서 호출됩니다.
        convergence_count >= 3인 경험들을 한 단계 안쪽으로 이동.
        """
        with self._state_transaction():
            compressed = 0
            newly_absorbed = 0
            for exp in self.data["experiences"]:
                if exp["convergence_count"] >= 3 and exp["level"] > 0:
                    exp["level"] -= 1
                    new_orbital = self.data["orbitals"][exp["level"]]
                    exp["binding_energy"] = new_orbital["binding_energy"]
                    exp["execution_mode"] = new_orbital["execution_mode"]
                    exp["convergence_count"] = 0
                    self.data["proton"]["total_converged"] = self._safe_int(
                        self.data["proton"].get("total_converged", 0)
                    ) + 1
                    if exp["level"] <= 1:
                        newly_absorbed += self._mark_absorbed(exp, units=1)
                    compressed += 1

            if compressed > 0:
                logger.info(f"   ⚫ 블랙홀 압축: {compressed}개의 경험이 내각으로 수렴")

            self._recompute_derived_state()
            return {"compressed": compressed, "newly_absorbed": newly_absorbed}

    def whitehole_expansion(self) -> Dict[str, Any]:
        """화이트홀 확장 — 양성자의 스칼라장을 확장합니다.
        
        블랙홀 압축 후 호출됩니다.
        내각에 충분한 경험이 쌓이면 → 스칼라장(코어) 확장 → 새 궤도 생성 가능.
        """
        with self._state_transaction():
            before_radius = float(self.data["proton"].get("scalar_field_radius", BASE_RADIUS))
            before_absorbed = self._safe_int(self.data["proton"].get("total_absorbed", 0))
            self._recompute_derived_state()
            proton = self.data["proton"]
            expanded = proton["scalar_field_radius"] > BASE_RADIUS

            if expanded:
                logger.info(
                    f"   ⚪ 화이트홀 확장: 스칼라장 반경 {proton['scalar_field_radius']:.4f}, "
                    f"코어 주파수 {proton['core_frequency']:.4f}"
                )

            return {
                "expanded": expanded,
                "total_absorbed": proton["total_absorbed"],
                "new_absorbed": max(0, proton["total_absorbed"] - before_absorbed),
            }

    # ═══════════════════════════════════════════
    # 망각 시스템 (자연 소멸)
    # ═══════════════════════════════════════════

    def natural_forgetting(self, max_age_days: float = 14.0) -> Dict[str, Any]:
        """자연 망각 — 외각의 오래되고 공명하지 않는 경험을 소멸시킵니다.
        
        인간이 잊는 것처럼, 시스템도 잊어야 합니다.
        잊지 않으면 노이즈가 쌓여 공명을 방해합니다.
        
        소멸 조건 (모두 만족해야 소멸):
        1. 외각 궤도 (level >= 3, 의식적 영역)
        2. max_age_days 이상 오래됨
        3. 한 번도 수렴하지 않음 (convergence_count == 0)
        """
        with self._state_transaction():
            now = datetime.now()
            forgotten = []
            survivors = []

            for exp in self.data["experiences"]:
                try:
                    exp_time = datetime.fromisoformat(exp["timestamp"])
                    age_days = (now - exp_time).total_seconds() / 86400
                except (KeyError, ValueError):
                    age_days = 0

                should_forget = (
                    exp.get("level", 0) >= 3 and
                    age_days > max_age_days and
                    exp.get("convergence_count", 0) == 0 and
                    not exp.get("crystallized", False)
                )

                if should_forget:
                    forgotten.append(exp)
                else:
                    survivors.append(exp)

            if forgotten:
                self.data["experiences"] = survivors
                logger.info(
                    f"   🍂 자연 망각: {len(forgotten)}개의 경험이 소멸 "
                    f"(잔존: {len(survivors)}개)"
                )

            self._recompute_derived_state()
            return {
                "forgotten_count": len(forgotten),
                "surviving_count": len(survivors),
                "forgotten_levels": [e.get("level", -1) for e in forgotten],
            }

    # ═══════════════════════════════════════════
    # 계층적 압축 (결정화)
    # ═══════════════════════════════════════════

    def crystallize_memories(self, min_cluster_size: int = 3, 
                              distance_threshold: float = 0.4) -> Dict[str, Any]:
        """계층적 압축 — 내각의 유사 경험을 하나의 결정 기억으로 융합합니다.
        
        "매일 아침 커피를 마셨다" × 365 → "나는 커피를 마시는 사람이다" × 1
        
        내각 궤도(level <= 1)에서 나선 거리가 가까운 경험 N개를
        하나의 '결정화된 기억(Crystallized Memory)'으로 융합합니다.
        결정화된 기억은 망각에서 보호되고, 더 강한 결합에너지를 가집니다.
        """
        with self._state_transaction():
            if len(self.data["experiences"]) < min_cluster_size:
                return {"crystallized": 0}

            inner_indices = [
                i for i, e in enumerate(self.data["experiences"])
                if e.get("level", 99) <= 1 and not e.get("crystallized", False)
            ]

            if len(inner_indices) < min_cluster_size:
                return {"crystallized": 0}

            used = set()
            crystals_formed = 0
            newly_absorbed = 0
            new_experiences = []

            for i in inner_indices:
                if i in used:
                    continue

                cluster = [i]
                center_coords = np.array(self.data["experiences"][i]["coords"])

                for j in inner_indices:
                    if j == i or j in used:
                        continue
                    j_coords = np.array(self.data["experiences"][j]["coords"])
                    dist = self.spiral_distance(center_coords, j_coords)
                    if dist < distance_threshold:
                        cluster.append(j)

                if len(cluster) >= min_cluster_size:
                    cluster_exps = [self.data["experiences"][idx] for idx in cluster]
                    avg_coords = np.mean(
                        [np.array(e["coords"]) for e in cluster_exps], axis=0
                    )
                    max_binding = max(e.get("binding_energy", 0) for e in cluster_exps)
                    refs = [e.get("content_ref", "") for e in cluster_exps if e.get("content_ref")]
                    combined_ref = f"[결정:{len(cluster)}개 융합] {refs[0] if refs else ''}"

                    represented_units = []
                    for exp in cluster_exps:
                        units = self._represented_absorption_units(exp)
                        if units == 0:
                            units = 1
                        represented_units.append(units)
                    crystal_units = sum(represented_units)
                    newly_absorbed += sum(
                        1 for exp in cluster_exps if self._represented_absorption_units(exp) == 0
                    )

                    crystal = {
                        "timestamp": datetime.now().isoformat(),
                        "coords": avg_coords.tolist(),
                        "level": 0,
                        "binding_energy": float(max_binding * 1.2),
                        "execution_mode": "unconscious",
                        "vibe": cluster_exps[0].get("vibe", {}),
                        "content_ref": combined_ref[:100],
                        "convergence_count": sum(e.get("convergence_count", 0) for e in cluster_exps),
                        "crystallized": True,
                        "crystal_size": len(cluster),
                        "absorbed": True,
                        "absorption_units": crystal_units,
                    }

                    new_experiences.append(crystal)
                    used.update(cluster)
                    crystals_formed += 1
                    self.data["proton"]["total_converged"] = self._safe_int(
                        self.data["proton"].get("total_converged", 0)
                    ) + 1

                    logger.info(
                        f"   💎 결정화: {len(cluster)}개 경험 → 1개 결정 기억 "
                        f"(결합에너지 {max_binding:.3f} → {crystal['binding_energy']:.3f})"
                    )

            remaining = [
                e for i, e in enumerate(self.data["experiences"]) if i not in used
            ]
            self.data["experiences"] = remaining + new_experiences
            self.data["proton"]["total_absorbed"] = self._safe_int(
                self.data["proton"].get("total_absorbed", 0)
            ) + newly_absorbed
            self._recompute_derived_state()

            return {
                "crystallized": crystals_formed,
                "absorbed": len(used),
                "newly_absorbed": newly_absorbed,
                "total_after": len(self.data["experiences"]),
            }

    # ═══════════════════════════════════════════
    # 수면 주기 전체 (망각 → 압축 → 블랙홀 → 화이트홀)
    # ═══════════════════════════════════════════

    def sleep_cycle(self) -> Dict[str, Any]:
        """완전한 나선 수면 주기를 실행합니다.
        
        1. 망각: 외각의 비공명 경험 소멸
        2. 결정화: 내각의 유사 경험 융합
        3. 블랙홀: 숙련된 경험을 내각으로 수렴
        4. 화이트홀: 스칼라장 확장
        """
        forget_result = self.natural_forgetting()
        crystal_result = self.crystallize_memories()
        bh_result = self.blackhole_compression()
        wh_result = self.whitehole_expansion()
        
        return {
            "forgetting": forget_result,
            "crystallization": crystal_result,
            "blackhole": bh_result,
            "whitehole": wh_result,
        }

    # ═══════════════════════════════════════════
    # 상태 보고
    # ═══════════════════════════════════════════

    def get_summary(self) -> str:
        """해마 상태를 한 줄로 요약합니다."""
        total = len(self.data["experiences"])
        bw = self.data["bandwidth"]
        proton = self.data["proton"]
        
        # 궤도별 경험 수
        level_counts = {}
        for e in self.data["experiences"]:
            lv = e["level"]
            level_counts[lv] = level_counts.get(lv, 0) + 1
        
        orbital_str = ", ".join(f"L{k}:{v}" for k, v in sorted(level_counts.items()))
        
        return (
            f"대역폭={bw:.2f} | 총경험={total} | "
            f"궤도=[{orbital_str}] | "
            f"코어주파수={proton['core_frequency']:.4f}"
        )

    def get_orbital_status(self) -> List[Dict[str, Any]]:
        """각 궤도의 현재 상태를 반환합니다."""
        status = []
        for orb in self.data["orbitals"]:
            exp_in_orbit = sum(
                1 for e in self.data["experiences"] if e["level"] == orb["level"]
            )
            status.append({
                "level": orb["level"],
                "radius": orb["radius"],
                "binding_energy": orb["binding_energy"],
                "execution": orb["execution_mode"],
                "experiences": exp_in_orbit,
            })
        return status


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    # 테스트
    test_path = Path("test_orbital_hippocampus.json")
    hippo = FibonacciOrbitalHippocampus(test_path)
    
    print("=== 피보나치 궤도 초기 상태 ===")
    for orb in hippo.get_orbital_status():
        print(f"  궤도 L{orb['level']}: r={orb['radius']:.4f}, "
              f"결합에너지={orb['binding_energy']:.4f}, "
              f"실행={orb['execution']}")
    
    print("\n=== 경험 등록 ===")
    vibes = [
        {"entropy": 0.1, "phase": "FLOW", "top_keywords": ["routine"]},
        {"entropy": 0.3, "phase": "FLOW", "top_keywords": ["work"]},
        {"entropy": 0.7, "phase": "EXPANSION", "top_keywords": ["new"]},
        {"entropy": 0.9, "phase": "VOID", "top_keywords": ["crisis"]},
        {"entropy": 0.1, "phase": "FLOW", "top_keywords": ["routine"]},  # 반복
        {"entropy": 0.1, "phase": "FLOW", "top_keywords": ["routine"]},  # 반복
        {"entropy": 0.1, "phase": "FLOW", "top_keywords": ["routine"]},  # 반복 → 수렴
    ]
    
    for v in vibes:
        result = hippo.register_experience(v, content_ref=f"test_{v['phase']}")
        print(f"  {v['phase']:12s} ent={v['entropy']:.1f} → "
              f"L{result['level']} ({result['execution_mode']:10s}) "
              f"결합={result['binding_energy']:.4f} "
              f"수렴={result['converged']}")
    
    print(f"\n=== 공명 탐색 ===")
    current = {"entropy": 0.2, "phase": "FLOW", "top_keywords": []}
    resonant = hippo.find_resonant_memories(current, top_k=3)
    for r in resonant:
        print(f"  거리={r['resonance_distance']:.4f} "
              f"L{r['level']} ({r['resonance_type']}) "
              f"{r['content_ref']}")
    
    print(f"\n=== 블랙홀→화이트홀 ===")
    bh = hippo.blackhole_compression()
    wh = hippo.whitehole_expansion()
    print(f"  압축: {bh['compressed']}개, 확장: {wh.get('expanded', False)}")
    
    print(f"\n=== 최종 상태 ===")
    print(f"  {hippo.get_summary()}")
    
    # 정리
    test_path.unlink(missing_ok=True)
