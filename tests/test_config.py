"""tests nothing, makes pytest happy"""

import pytest
from qbtapi import QBTAPIConfig


def test_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """test config parsing"""
    monkeypatch.setenv("QB_USERNAME", "testuser")
    monkeypatch.setenv("QB_PASSWORD", "hunter2")
    monkeypatch.setenv("HECHOST", "localhost")
    monkeypatch.setenv("HECTOKEN", "hunter2")
    monkeypatch.setenv("QB_PORT", "12345")
    test_parsed_config = QBTAPIConfig.model_validate({})
    assert test_parsed_config.qb_port == 12345
