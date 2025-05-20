"""tests nothing, makes pytest happy"""

import pytest
from qbtapi import QBTAPIConfig


def test_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QB_PORT", "12345")
    monkeypatch.setenv("HEC_HOST", "localhost")
    foo = QBTAPIConfig.model_validate({})
    assert foo.qb_port == 12345
