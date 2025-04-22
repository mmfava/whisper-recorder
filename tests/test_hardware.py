import pytest

from whisper_recorder.hardware import detect_hardware, compute_hardware_hash

def test_compute_hardware_hash_deterministic():
    data1 = {"b": 2, "a": 1}
    data2 = {"a": 1, "b": 2}
    hash1 = compute_hardware_hash(data1)
    hash2 = compute_hardware_hash(data2)
    assert isinstance(hash1, str)
    assert hash1 == hash2

def test_detect_hardware_keys_and_types():
    detected = detect_hardware()
    expected_keys = {"os", "cpu_cores", "ram_gb", "cuda_available", "gpu_name", "vram_gb", "compute_capability"}
    assert expected_keys.issubset(detected.keys())
    assert isinstance(detected["os"], str)
    assert isinstance(detected["cpu_cores"], int)
    assert isinstance(detected["ram_gb"], (float, int))
    assert isinstance(detected["cuda_available"], bool)
    assert detected["gpu_name"] is None or isinstance(detected["gpu_name"], str)
    assert isinstance(detected["vram_gb"], (float, int))
    cc = detected["compute_capability"]
    assert cc is None or (isinstance(cc, tuple) and len(cc) == 2)