#!/usr/bin/env python3
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("StoryValidator")

class StoryValidator:
    """
    Story Validator — 가설 검증 및 학습기
    ====================================
    생성된 가설(Story Candidates)이 실제 상황과 일치했는지 사후 검증하고,
    학습 결과를 기록하여 시스템의 메타인지를 강화합니다.
    """
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.candidates_file = root_dir / "outputs" / "story_candidates.jsonl"
        self.metrics_file = root_dir / "outputs" / "action_metrics.jsonl"
        self.orbit_file = root_dir / "outputs" / "context_orbit.json"
        self.validation_file = root_dir / "outputs" / "story_validations.jsonl"
        self.ledger_file = Path(r"C:\workspace\agi\memory\resonance_ledger.jsonl")
        
    def validate_pending_candidates(self):
        """아직 결과가 확인되지 않은 가설들을 검증합니다."""
        if not self.candidates_file.exists():
            return
            
        updated_lines = []
        validated_count = 0
        
        try:
            with open(self.candidates_file, "r", encoding="utf-8") as f:
                for line in f:
                    analysis = json.loads(line)
                    has_update = False
                    
                    for candidate in analysis.get("story_candidates", []):
                        # 피드백 필드가 없거나 unknown인 경우 검증 시도
                        current_feedback = candidate.get("feedback", "unknown")
                        if current_feedback == "unknown":
                            result = self._check_hypothesis(candidate, analysis["timestamp"])
                            if result:
                                candidate["feedback"] = result["feedback"]
                                candidate["status"] = result["status"]
                                candidate["validated_at"] = datetime.now().isoformat()
                                candidate["validation_evidence"] = result["evidence"]
                                candidate["validation_confidence"] = result["confidence"]
                                self._append_validation_record(analysis, candidate, result)
                                if result["feedback"] == "confirmed":
                                    logger.info(f"✨ [LEARNING_SIGNAL] 가설 지지됨: {candidate['id']} -> confirmed")
                                else:
                                    logger.info(f"🧭 [LEARNING_SIGNAL] 가설 정정됨: {candidate['id']} -> {result['feedback']}")
                                has_update = True
                                validated_count += 1
                                
                    updated_lines.append(json.dumps(analysis, ensure_ascii=False))
            
            if validated_count > 0:
                with open(self.candidates_file, "w", encoding="utf-8") as f:
                    for line in updated_lines:
                        f.write(line + "\n")
            
            self._log_learning_metrics()
                        
        except Exception as e:
            logger.error(f"Failed to validate candidates: {e}")

    def _check_hypothesis(self, candidate: Dict[str, Any], created_at: str) -> Optional[Dict[str, Any]]:
        """개별 가설의 타당성을 데이터로 확인합니다."""
        cid = candidate["id"]
        created_dt = datetime.fromisoformat(created_at)
        
        # 1. 자가 교정 검증 (Self-Correction Validation)
        if cid == "STUCK_IN_LOOP":
            subsequent_actions = self._get_actions_after(created_dt)
            trigger_action = self._extract_trigger_action(candidate)
            if not trigger_action or not subsequent_actions:
                return None
            if not self._is_stutter_watched_now(trigger_action):
                return {
                    "feedback": "rejected",
                    "status": "invalidated",
                    "confidence": 0.9,
                    "evidence": [
                        f"{trigger_action} is allowed as unconscious auto-action in the current orbit",
                        "Repeated auto-action alone is not a boundary contact",
                    ],
                }
            
            evidence = self._evaluate_stutter_resolution(trigger_action, subsequent_actions)
            if evidence["feedback"]:
                return {
                    "feedback": evidence["feedback"],
                    "status": "validated",
                    "confidence": evidence["confidence"],
                    "evidence": evidence["evidence"],
                }
            return None

        if cid == "GOAL_DEVIATION":
            trigger_action = self._extract_trigger_action(candidate)
            if trigger_action and self._is_action_allowed_now(trigger_action):
                return {
                    "feedback": "rejected",
                    "status": "invalidated",
                    "confidence": 0.9,
                    "evidence": [
                        f"{trigger_action} is allowed by the current context_orbit policy",
                        "Older candidate likely came from an outdated allowed-action check",
                    ],
                }

        # 2. 사용자 피드백 검증 (User Feedback Validation)
        user_feedback = self._scan_ledger_for_confirmation(created_dt, candidate)
        if user_feedback:
            return user_feedback

        return None

    def _extract_trigger_action(self, candidate: Dict[str, Any]) -> Optional[str]:
        text = " ".join([
            str(candidate.get("story", "")),
            " ".join(str(item) for item in candidate.get("evidence", [])),
        ])
        match = re.search(r"ACTION_[A-Z_]+", text)
        if match:
            return match.group(0)
        return None

    def _evaluate_stutter_resolution(self, trigger_action: str, actions: List[str]) -> Dict[str, Any]:
        """반복이 실제로 완화됐는지 작은 관측 창으로 판정합니다."""
        observation_window = actions[:6]
        non_recovery = [a for a in observation_window if a != "ACTION_CONTEXT_UNPACK"]
        if len(non_recovery) < 2:
            return {
                "feedback": None,
                "confidence": 0.0,
                "evidence": ["Not enough post-hypothesis actions to validate loop resolution"],
            }

        trigger_count = sum(1 for a in non_recovery if a == trigger_action)
        longest_trigger_run = self._longest_run(non_recovery, trigger_action)

        if longest_trigger_run >= 3:
            return {
                "feedback": "rejected",
                "confidence": 0.85,
                "evidence": [
                    f"{trigger_action} repeated {longest_trigger_run} times again after context unpacking",
                    f"Observed actions: {observation_window}",
                ],
            }

        if trigger_count / len(non_recovery) <= 0.5:
            return {
                "feedback": "confirmed",
                "confidence": 0.7,
                "evidence": [
                    f"{trigger_action} no longer dominates the post-unpack action window",
                    f"Observed actions: {observation_window}",
                ],
            }

        return {
            "feedback": None,
            "confidence": 0.0,
            "evidence": [
                f"{trigger_action} still appears frequently; leaving hypothesis pending",
                f"Observed actions: {observation_window}",
            ],
        }

    def _longest_run(self, actions: List[str], target: str) -> int:
        longest = 0
        current = 0
        for action in actions:
            if action == target:
                current += 1
                longest = max(longest, current)
            else:
                current = 0
        return longest

    def _is_action_allowed_now(self, action: str) -> bool:
        if not self.orbit_file.exists():
            return False
        try:
            orbit = json.loads(self.orbit_file.read_text(encoding="utf-8"))
            allowed = []
            for key in ("allowed_auto_actions", "allowed_reflex_actions", "recovery_actions"):
                allowed.extend(orbit.get(key, []))
            return action in allowed
        except Exception:
            return False

    def _is_stutter_watched_now(self, action: str) -> bool:
        if not self.orbit_file.exists():
            return False
        try:
            orbit = json.loads(self.orbit_file.read_text(encoding="utf-8"))
            watched = orbit.get("stutter_watch_actions")
            if watched is None:
                watched = orbit.get("allowed_reflex_actions", []) + orbit.get("recovery_actions", [])
            return action in watched
        except Exception:
            return False

    def _get_actions_after(self, dt: datetime) -> List[str]:
        """특정 시점 이후의 액션 리스트를 가져옵니다."""
        if not self.metrics_file.exists(): return []
        actions = []
        try:
            with open(self.metrics_file, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    ts = datetime.fromisoformat(data["timestamp"])
                    if ts > dt:
                        actions.append(data["action"])
            return actions
        except: return []

    def _scan_ledger_for_confirmation(self, dt: datetime, candidate: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """공명 레저에서 지휘자님의 긍정/부정 피드백을 스캔합니다."""
        if not self.ledger_file.exists(): return None
        
        confirm_keywords = ["맞아", "응", "그렇네", "정답", "빙고", "yes", "correct"]
        reject_keywords = ["아니야", "틀렸어", "글쎄", "no", "wrong"]
        
        try:
            with open(self.ledger_file, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    ts = self._parse_timestamp(data.get("timestamp"))
                    if ts and ts <= dt:
                        continue
                    content = self._extract_ledger_content(data)
                    if not content or not self._feedback_mentions_candidate(content, candidate):
                        continue
                    if any(kw in content for kw in confirm_keywords):
                        return {
                            "feedback": "confirmed",
                            "status": "validated",
                            "confidence": 0.75,
                            "evidence": [f"User feedback after hypothesis: {content[:160]}"],
                        }
                    if any(kw in content for kw in reject_keywords):
                        return {
                            "feedback": "rejected",
                            "status": "validated",
                            "confidence": 0.75,
                            "evidence": [f"User feedback after hypothesis: {content[:160]}"],
                        }
            return None
        except: return None

    def _log_learning_metrics(self):
        """누적된 학습 지표를 계산하고 출력합니다."""
        if not self.candidates_file.exists(): return
        
        stats = {"confirmed": 0, "rejected": 0, "unknown": 0}
        status_counts = {"hypothesis": 0, "validated": 0, "invalidated": 0}
        total = 0
        
        try:
            with open(self.candidates_file, "r", encoding="utf-8") as f:
                for line in f:
                    analysis = json.loads(line)
                    for c in analysis.get("story_candidates", []):
                        fb = c.get("feedback", "unknown")
                        stats[fb] = stats.get(fb, 0) + 1
                        status = c.get("status", "hypothesis")
                        status_counts[status] = status_counts.get(status, 0) + 1
                        total += 1
            
            if total > 0:
                confirmed = stats.get("confirmed", 0)
                rejected = stats.get("rejected", 0)
                decided = confirmed + rejected
                support_rate_all = (confirmed / total) * 100
                support_rate_decided = (confirmed / decided) * 100 if decided else 0.0
                
                # 재발률 계산 (Recurrence Rate after Unpack)
                recurrence_data = self._calculate_recurrence_rate()
                
                logger.info(f"📊 [LEARNING_METRICS] 가설 지지 신호: 총 {total}건")
                logger.info(f"   ㄴ 지지(Confirmed): {confirmed} | 기각(Rejected): {rejected} | 대기(Unknown): {stats.get('unknown', 0)}")
                logger.info(f"   ㄴ 무효화(Invalidated): {status_counts.get('invalidated', 0)} | 지지율(전체 기준): {support_rate_all:.1f}%")
                
                if recurrence_data:
                    logger.info(f"   📈 재발 지표: {recurrence_data['avg_recurrence_time']:.1f}분 (평균 재발 간격)")
                    logger.info(f"      ㄴ 재발 감소율: {recurrence_data['reduction_rate']:.1%}")

                logger.info(f"   ㄴ 주의: 이 값은 학습 증명이 아니라 가설 품질의 관측 신호입니다.")
                
                # 별도 지표 파일 업데이트
                metrics_path = self.root_dir / "outputs" / "learning_state.json"
                with open(metrics_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "timestamp": datetime.now().isoformat(),
                        "total_hypotheses": total,
                        "stats": stats,
                        "status_counts": status_counts,
                        "support_rate_all": round(support_rate_all, 2),
                        "support_rate_decided": round(support_rate_decided, 2),
                        "recurrence_metrics": recurrence_data,
                        "interpretation": "Observation signal only; do not treat as proof of generalized learning."
                    }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to log metrics: {e}")

    def _calculate_recurrence_rate(self) -> Optional[Dict[str, Any]]:
        """성찰 이후 동일한 경계 접촉이 재발하기까지의 시간을 분석합니다."""
        if not self.candidates_file.exists(): return None
        
        intervals = []
        try:
            with open(self.candidates_file, "r", encoding="utf-8") as f:
                last_ts = None
                for line in f:
                    data = json.loads(line)
                    ts = datetime.fromisoformat(data["timestamp"])
                    if last_ts:
                        intervals.append((ts - last_ts).total_seconds() / 60.0)
                    last_ts = ts
            
            if not intervals: return None
            avg_interval = sum(intervals) / len(intervals)
            # 재발 간격이 길어질수록(시간이 흐를수록) 학습이 일어나고 있다고 가정
            reduction = 0.0
            if len(intervals) > 1:
                reduction = (intervals[-1] - intervals[0]) / max(1, intervals[0])
            
            return {
                "avg_recurrence_time": avg_interval,
                "reduction_rate": reduction,
                "interval_history": intervals[-5:]
            }
        except: return None

    def _parse_timestamp(self, value: Any) -> Optional[datetime]:
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            if parsed.tzinfo is not None:
                return parsed.replace(tzinfo=None)
            return parsed
        except Exception:
            return None

    def _extract_ledger_content(self, data: Dict[str, Any]) -> str:
        for key in ("content", "message", "text", "body"):
            value = data.get(key)
            if isinstance(value, str):
                return value
        payload = data.get("payload")
        if isinstance(payload, dict):
            for key in ("content", "message", "text", "body"):
                value = payload.get(key)
                if isinstance(value, str):
                    return value
        return ""

    def _feedback_mentions_candidate(self, content: str, candidate: Dict[str, Any]) -> bool:
        trigger_action = self._extract_trigger_action(candidate)
        anchors = [candidate.get("id", ""), trigger_action or ""]
        story = candidate.get("story", "")
        if "루프" in story:
            anchors.append("루프")
        if "궤도" in story:
            anchors.append("궤도")
        if "공백" in story or "시간" in story:
            anchors.extend(["공백", "시간"])
        return any(anchor and anchor in content for anchor in anchors)

    def _append_validation_record(
        self,
        analysis: Dict[str, Any],
        candidate: Dict[str, Any],
        result: Dict[str, Any],
    ):
        record = {
            "timestamp": datetime.now().isoformat(),
            "candidate_created_at": analysis.get("timestamp"),
            "candidate_id": candidate.get("id"),
            "feedback": result.get("feedback"),
            "status": result.get("status"),
            "confidence": result.get("confidence"),
            "evidence": result.get("evidence", []),
        }
        try:
            with open(self.validation_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.warning(f"Failed to append validation record: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    validator = StoryValidator(Path(r"c:\workspace2\shion"))
    validator.validate_pending_candidates()
