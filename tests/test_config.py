"""tests nothing, makes pytest happy"""

import pytest
from qbtapi import QBTAPIConfig


def test_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QB_USERNAME", "testuser")
    monkeypatch.setenv("QB_PASSWORD", "hunter2")
    monkeypatch.setenv("HECHOST", "localhost")
    monkeypatch.setenv("HECTOKEN", "hunter2")
    monkeypatch.setenv("QB_PORT", "12345")
    foo = QBTAPIConfig.model_validate({})
    assert foo.qb_port == 12345
