"""
runs unit tests

this is meant to be executed with blender headless, meaning: blender --background --python unit_test_utility.py
this gives the possibility to execute unit tests inside blender

for the unit tests, the sources of the package, and the venv are appended to sys.path
if some of the packages used aren't available in blender vanilla interpreter, the .venv is the fallback
"""

import sys, os
from pathlib import Path

working_dir = Path(os.getcwd())

if not (working_dir / '.venv').is_dir():
    raise Exception('.venv does not exist, cannot proceed')  # TODO set up .venv automatically

sys.path.append(str(working_dir / '.venv' / 'Lib'))
sys.path.append(str(working_dir / '.venv' / 'Lib' / 'site-packages'))

try:
    import pytest
except ImportError:
    raise RuntimeError(f'no "pytest" found in the virtual environment, cannot run unit tests')


class TestResultSummaryService:

    def pytest_terminal_summary(self, terminalreporter, exitstatus, config):
        print(terminalreporter.stats)


def run_unit_tests():
    # we append project's .venv to sys.path to locate libs not installed in vanilla blender
    # if there's no .venv, need to set up one, because, among others, it must contain pytest

    exit_code = pytest.main(['--verbose', 'tests/'], plugins=[TestResultSummaryService()])

    raise SystemExit(exit_code)


run_unit_tests()
