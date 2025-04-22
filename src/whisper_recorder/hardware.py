"""
Detect and represent hardware capabilities.
"""
import platform
import hashlib
import json
import os
from typing import Dict, Any

# Optional import for system metrics
try:
    import psutil
except ImportError:
    psutil = None

# Optional import for GPU detection
try:
    import torch
except ImportError:
    torch = None

def detect_hardware() -> Dict[str, Any]:
    """
    Detect basic hardware information.
    Returns a dict with OS, CPU cores, RAM, CUDA availability, GPU name, VRAM, and compute capability.
    """
    os_name = platform.system()
    # CPU cores
    if psutil is not None:
        cpu_cores = psutil.cpu_count(logical=True) or 0
    else:
        cpu_cores = os.cpu_count() or 0
    # Total RAM in GB
    if psutil is not None:
        ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
    else:
        ram_gb = 0.0
    # Detect CUDA/GPU if torch is available
    cuda_available = False
    gpu_name = None
    vram_gb = 0.0
    compute_capability = None
    if torch is not None and torch.cuda.is_available():
        cuda_available = True
        props = torch.cuda.get_device_properties(0)
        gpu_name = props.name
        vram_gb = round(props.total_memory / (1024 ** 3), 2)
        compute_capability = (props.major, props.minor)
    return {
        "os": os_name,
        "cpu_cores": cpu_cores,
        "ram_gb": ram_gb,
        "cuda_available": cuda_available,
        "gpu_name": gpu_name,
        "vram_gb": vram_gb,
        "compute_capability": compute_capability,
    }

def compute_hardware_hash(detected: Dict[str, Any]) -> str:
    """
    Compute a SHA-256 hash of the detected hardware dict for change detection.
    """
    serial = json.dumps(detected, sort_keys=True).encode("utf-8")
    return hashlib.sha256(serial).hexdigest()