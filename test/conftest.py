# test/conftest.py
import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "target_machine: mark test to run on the target machine"
    )
