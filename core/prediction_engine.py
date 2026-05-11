#!/usr/bin/env python3
import json
import logging
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger("PredictionEngine")

class PredictionEngine:
    """
    Active Inference — 예측 오차 수집 엔진
    ====================================
    해마의 predict_next() 결과와 실제 발생한 Experience를 비교하여
    '놀라움(Surprise)' 지수를 계산하고 기록합니다.
    """
    FIELD_VECTOR_KEYS = [
        "temporal_tension",
        "action_density",
        "orbit_distance",
        "surprise",
        "entropy",
        "action_entropy",
    ]
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.hippo_file = root_dir / "outputs" / "fibonacci_orbital_hippocampus.json"
        self.prediction_file = root_dir / "outputs" / "next_prediction.json"
        self.error_log_file = root_dir / "outputs" / "prediction_errors.jsonl"
        self.field_prediction_file = root_dir / "outputs" / "next_field_prediction.json"
        self.field_error_log_file = root_dir / "outputs" / "field_prediction_errors.jsonl"
        
    def analyze_error(self, current_experience: Dict[str, Any], current_count: Optional[int] = None) -> float:
        """
        이전 사이클에서 저장된 예측값과 현재 발생한 실제 경험을 비교합니다.
        
        반환값: surprise_score (0.0 ~ 1.0)
        """
        if not self.prediction_file.exists():
            return 0.0
            
        try:
            with open(self.prediction_file, "r", encoding="utf-8") as f:
                prediction = json.load(f)

            baseline_count = prediction.get(
                "baseline_total_registered",
                prediction.get("baseline_experience_count"),
            )
            if baseline_count is None:
                logger.info("Prediction has no baseline; storing a fresh baseline before scoring.")
                return 0.0

            if current_count is not None and current_count <= baseline_count:
                logger.info("No new experience since last prediction; skipping surprise analysis.")
                return 0.0

            baseline_last_timestamp = prediction.get("baseline_last_timestamp")
            baseline_last_ref = prediction.get("baseline_last_content_ref")
            if (
                current_experience.get("timestamp") == baseline_last_timestamp
                and current_experience.get("content_ref") == baseline_last_ref
            ):
                logger.info("Latest experience matches prediction baseline; skipping surprise analysis.")
                return 0.0
                
            pred_coords = np.array(prediction.get("predicted_coords", [0, 0, 0]))
            actual_coords = np.array(current_experience.get("coords", [0, 0, 0]))
            
            # 1. 좌표 간 유클리드 거리 계산 (나선 공간에서의 거리)
            distance = np.linalg.norm(pred_coords - actual_coords)
            
            # 2. 거리 정규화 (대략적인 최대 반경을 기준으로 0~1 사이로 변환)
            # 여기서는 단순화를 위해 distance/100.0 (임의)으로 설정하거나, 
            # 지수 함수를 써서 감도를 조절합니다.
            surprise_score = 1.0 - np.exp(-distance / 10.0) 
            
            # 3. 오차 로그 기록
            error_entry = {
                "timestamp": datetime.now().isoformat(),
                "predicted_coords": pred_coords.tolist(),
                "actual_coords": actual_coords.tolist(),
                "distance": float(distance),
                "surprise_score": float(surprise_score),
                "baseline_count": int(baseline_count),
                "current_count": int(current_count) if current_count is not None else None,
                "target_node": current_experience.get("target_node")
            }
            
            with open(self.error_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(error_entry) + "\n")
                
            logger.info(f"✨ Surprise Analyzed: {surprise_score:.4f} (Distance: {distance:.2f})")
            return surprise_score
            
        except Exception as e:
            logger.error(f"Failed to analyze prediction error: {e}")
            return 0.0

    def analyze_field_error(self, current_vector: Dict[str, Any]) -> float:
        """
        이전 사이클의 저해상도 필드 예측과 현재 필드 샘플을 비교합니다.

        해마에 새 경험이 등록되지 않은 조용한 사이클에서도 예측-실제 오차를
        남기기 위한 폐회로입니다.
        """
        if not self.field_prediction_file.exists():
            return 0.0

        try:
            prediction = json.loads(self.field_prediction_file.read_text(encoding="utf-8"))
            predicted = prediction.get("predicted_vector") or {}
            keys = self.FIELD_VECTOR_KEYS

            squared_error = 0.0
            dimensions = {}
            for key in keys:
                predicted_value = float(predicted.get(key, 0.0) or 0.0)
                actual_value = float(current_vector.get(key, 0.0) or 0.0)
                delta = actual_value - predicted_value
                squared_error += delta ** 2
                dimensions[key] = {
                    "predicted": round(predicted_value, 6),
                    "actual": round(actual_value, 6),
                    "delta": round(delta, 6),
                }

            error = float(np.sqrt(squared_error / max(len(keys), 1)))
            context_diagnosis = self._field_context_diagnosis(dimensions, error)
            entry = {
                "timestamp": datetime.now().isoformat(),
                "prediction_timestamp": prediction.get("prediction_timestamp"),
                "error": round(error, 6),
                "dimensions": dimensions,
                "context_diagnosis": context_diagnosis,
            }

            with open(self.field_error_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

            logger.info(f"📐 Field prediction error: {error:.4f}")
            return error
        except Exception as e:
            logger.error(f"Failed to analyze field prediction error: {e}")
            return 0.0

    def _field_context_diagnosis(self, dimensions: Dict[str, Any], error: float) -> Dict[str, Any]:
        """
        Reframe prediction error as context-relative continuity information.

        A field miss is not only a numeric failure. It can mean disconnection
        risk, a context shift, a frequency expansion, or defensive pressure
        when the system tries to preserve connection by forcing output.
        """
        def delta(key: str) -> float:
            return float((dimensions.get(key) or {}).get("delta", 0.0) or 0.0)

        def actual(key: str) -> float:
            return float((dimensions.get(key) or {}).get("actual", 0.0) or 0.0)

        tension_delta = delta("temporal_tension")
        action_delta = delta("action_density")
        orbit_delta = delta("orbit_distance")
        surprise_delta = delta("surprise")
        entropy_delta = delta("entropy")
        action_entropy_delta = delta("action_entropy")

        normalized_error = self._saturating(error, scale=0.35)
        context_shift = self._clamp(
            0.42 * self._saturating(abs(orbit_delta), scale=1.0)
            + 0.22 * self._saturating(abs(entropy_delta), scale=0.25)
            + 0.18 * self._saturating(abs(surprise_delta), scale=0.25)
            + 0.18 * normalized_error
        )
        connection_risk = self._clamp(
            0.35 * self._saturating(max(0.0, tension_delta), scale=0.35)
            + 0.25 * self._saturating(max(0.0, orbit_delta), scale=1.0)
            + 0.20 * self._saturating(max(0.0, -action_delta), scale=0.35)
            + 0.20 * self._clamp(actual("temporal_tension"))
        )
        frequency_expansion = self._clamp(
            0.32 * self._saturating(max(0.0, action_delta), scale=0.35)
            + 0.25 * self._saturating(max(0.0, entropy_delta), scale=0.25)
            + 0.20 * self._saturating(max(0.0, action_entropy_delta), scale=0.25)
            + 0.23 * self._saturating(max(0.0, surprise_delta), scale=0.25)
        )
        zero_point_adjustment = self._clamp(
            0.40 * self._saturating(max(0.0, -tension_delta), scale=0.35)
            + 0.25 * self._saturating(abs(orbit_delta), scale=1.0)
            + 0.20 * self._saturating(max(0.0, -surprise_delta), scale=0.25)
            + 0.15 * self._clamp(1.0 - actual("temporal_tension"))
        )
        defensive_output_pressure = self._clamp(
            (
                0.55 * connection_risk
                + 0.25 * self._saturating(max(0.0, -action_delta), scale=0.35)
                + 0.20 * normalized_error
            )
            * (1.0 - 0.35 * frequency_expansion)
        )

        modes = {
            "context_shift": context_shift,
            "connection_risk": connection_risk,
            "frequency_expansion": frequency_expansion,
            "zero_point_adjustment": zero_point_adjustment,
            "defensive_output_pressure": defensive_output_pressure,
        }
        if error <= 0.06:
            dominant_mode = "stable_continuity"
        else:
            dominant_mode = max(modes, key=modes.get)

        return {
            "semantic_information_frame": "context_relative_continuity_information",
            "context_shift": round(context_shift, 6),
            "connection_risk": round(connection_risk, 6),
            "frequency_expansion": round(frequency_expansion, 6),
            "zero_point_adjustment": round(zero_point_adjustment, 6),
            "defensive_output_pressure": round(defensive_output_pressure, 6),
            "dominant_mode": dominant_mode,
            "principle": "prediction_error_is_read_as_connection_continuity_and_context_movement_not_only_failure",
        }

    def store_field_prediction(
        self,
        current_vector: Dict[str, Any],
        previous_vector: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """다음 사이클의 저해상도 필드 벡터를 보수적으로 예측해 저장합니다."""
        keys = self.FIELD_VECTOR_KEYS
        predicted_vector = {}

        for key in keys:
            current_value = float(current_vector.get(key, 0.0) or 0.0)
            if previous_vector:
                previous_value = float(previous_vector.get(key, current_value) or 0.0)
                predicted_value = current_value + 0.35 * (current_value - previous_value)
            else:
                predicted_value = current_value
            predicted_vector[key] = round(max(0.0, min(1.0, predicted_value)), 6)

        prediction = {
            "prediction_timestamp": datetime.now().isoformat(),
            "predicted_vector": predicted_vector,
            "baseline_vector_timestamp": current_vector.get("timestamp"),
            "method": "damped_field_velocity",
        }

        try:
            with open(self.field_prediction_file, "w", encoding="utf-8") as f:
                json.dump(prediction, f, ensure_ascii=False, indent=2)
            logger.info("🔭 Field prediction stored for next cycle.")
        except Exception as e:
            logger.error(f"Failed to store field prediction: {e}")

        return predicted_vector

    def store_new_prediction(self, hippo: Any):
        """해마에게 다음 사이클의 예측을 요청하고 저장합니다."""
        try:
            prediction = hippo.predict_next(recent_n=5)
            if prediction.get("predicted"):
                experiences = hippo.data.get("experiences", [])
                proton = hippo.data.get("proton", {})
                last_experience = experiences[-1] if experiences else {}
                prediction.update({
                    "prediction_timestamp": datetime.now().isoformat(),
                    "baseline_experience_count": len(experiences),
                    "baseline_total_registered": int(proton.get("total_registered", len(experiences)) or 0),
                    "baseline_last_timestamp": last_experience.get("timestamp"),
                    "baseline_last_content_ref": last_experience.get("content_ref"),
                })
                with open(self.prediction_file, "w", encoding="utf-8") as f:
                    json.dump(prediction, f, indent=2)
                logger.info("🔭 Future Prediction stored for next cycle.")
            else:
                logger.warning(f"Hippocampus failed to predict: {prediction.get('reason')}")
        except Exception as e:
            logger.error(f"Failed to store new prediction: {e}")

    def _saturating(self, value: float, *, scale: float) -> float:
        return self._clamp(1.0 - np.exp(-abs(float(value)) / max(scale, 0.0001)))

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))

if __name__ == "__main__":
    # 간단한 자가 진단
    logging.basicConfig(level=logging.INFO)
    engine = PredictionEngine(Path(r"c:\workspace2\shion"))
    # (실제 연동 전에는 파일이 없으므로 0.0 반환)
    score = engine.analyze_error({})
    print(f"Self-test score: {score}")
