"""
Configuration for AGI Unified Frontend Services
"""
from agi_core.utils.paths import get_workspace_root, add_to_sys_path
import sys

# 워크스페이스 루트 및 경로 설정
WINDOWS_AGI_ROOT = get_workspace_root()
if str(WINDOWS_AGI_ROOT) not in sys.path:
    sys.path.insert(0, str(WINDOWS_AGI_ROOT))
if str(WINDOWS_AGI_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(WINDOWS_AGI_ROOT / "scripts"))

try:
    from credentials_manager import get_linux_vm_credentials
    # Linux VM Credentials
    LINUX_CREDS = get_linux_vm_credentials()
except (ImportError, Exception):
    # Nature-based mode fallbacks
    LINUX_CREDS = {
        'host': '127.0.0.1', 
        'user': 'agi', 
        'password': 'agi'
    }

LINUX_HOST = LINUX_CREDS.get('host', '127.0.0.1')
LINUX_USER = LINUX_CREDS.get('user', 'agi')
LINUX_PASSWORD = LINUX_CREDS.get('password', 'agi')

# API Ports
CONSCIOUSNESS_PORT = 8100
UNCONSCIOUS_PORT = 8101
BACKGROUND_SELF_PORT = 8102
AGGREGATOR_PORT = 8104

# CORS Settings
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Paths
# WINDOWS_AGI_ROOT는 위에서 이미 설정됨 (WINDOWS_AGI_ROOT was already set above)
BODY_PATH = WINDOWS_AGI_ROOT / "body"
MIND_PATH = WINDOWS_AGI_ROOT / "mind"
OUTPUTS_PATH = WINDOWS_AGI_ROOT / "outputs"
INPUTS_PATH = WINDOWS_AGI_ROOT / "inputs"
LOGS_PATH = WINDOWS_AGI_ROOT / "logs"
MEMORY_PATH = WINDOWS_AGI_ROOT / "memory"
CONFIG_PATH = WINDOWS_AGI_ROOT / "config"

# Sub-component Paths
OBS_INTAKE_DIR = INPUTS_PATH / "intake" / "exploration" / "sessions"
RESONANCE_LEDGER = MEMORY_PATH / "resonance_ledger.jsonl"
ARI_BUFFER = MEMORY_PATH / "ari_learning_buffer.json"

# Linux Paths
LINUX_AGI_ROOT = "/home/bino/agi"
LINUX_OUTPUTS = f"{LINUX_AGI_ROOT}/outputs"

# Update Intervals (seconds)
RHYTHM_UPDATE_INTERVAL = 5  # How often to poll Linux for rhythm data
CONSCIOUSNESS_UPDATE_INTERVAL = 10  # How often to check Windows state
