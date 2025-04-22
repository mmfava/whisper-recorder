"""
Pytest configuration: ensure src directory is on sys.path for imports.
"""
import sys
import os

# Add project src/ directory to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)