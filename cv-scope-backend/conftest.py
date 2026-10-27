# conftest.py  — top-level pytest configuration for cv-scope-backend
#
# Adds the backend directory to sys.path so that all test files can
# import project modules without needing per-file sys.path hacks.

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
