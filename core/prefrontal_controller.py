#!/usr/bin/env python3
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from phase_governor import PhaseGovernor

logger = logging.getLogger("PrefrontalController")

class PrefrontalController:
    """
    Prefrontal Controller (Legacy Adapter)
    ======================================
    기존의 PrefrontalController 인터페이스를 유지하면서,
    내부적으로는 PhaseGovernor의 파동 조율 로직을 사용하도록 연결하는 어댑터입니다.
    """
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.governor = PhaseGovernor(root_dir)
        
    def deliberate(self, 
                   sensing: Dict[str, Any], 
                   memory: Optional[Dict[str, Any]], 
                   hypothesis: Optional[Dict[str, Any]], 
                   metrics: Dict[str, Any]) -> Dict[str, Any]:
        """기존 deliberate 호출을 PhaseGovernor의 modulate로 변환합니다."""
        
        # PhaseGovernor 호출
        candidate_action = "ACTION_CONTEXT_UNPACK" if sensing.get("is_boundary") else "ACTION_CONTINUOUS_SCAN"
        modulation = self.governor.modulate(sensing, memory, hypothesis, metrics, candidate_action)
        
        # 기존 인터페이스 형식에 맞춰 반환값 변환
        return {
            "timestamp": modulation["timestamp"],
            "chosen_action": modulation["final_action"],
            "vetoed": [modulation["interference"]] if modulation["interference"] == "destructive" else [],
            "reason": modulation["phase_decision"],
            "phase_trace": modulation # 상세 파동 데이터 포함
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    controller = PrefrontalController(Path(r"c:\workspace2\shion"))
    res = controller.deliberate({"is_boundary": True}, None, None, {})
    print(res)
