#!/usr/bin/env python
"""Quick wrapper to run test_quick.py without stdin issues"""
import subprocess
import sys

result = subprocess.run([sys.executable, "test_quick.py"], capture_output=False)
sys.exit(result.returncode)
