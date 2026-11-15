import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shopkart import payments  # noqa: E402


class FakeContext:
    """Stands in for ADK's ToolContext in offline tests: just a state dict."""

    def __init__(self):
        self.state = {}


class FakeTool:
    def __init__(self, name):
        self.name = name


@pytest.fixture
def ctx():
    return FakeContext()


@pytest.fixture
def payments_down(monkeypatch, tmp_path):
    flag = tmp_path / "payments_down.flag"
    flag.write_text("down")
    monkeypatch.setattr(payments, "DOWN_FLAG", flag)
    monkeypatch.setattr(payments, "HANG_SECONDS", 0)
    return flag


@pytest.fixture(autouse=True)
def payments_up_by_default(monkeypatch, tmp_path, request):
    if "payments_down" not in request.fixturenames:
        monkeypatch.setattr(payments, "DOWN_FLAG", tmp_path / "not_down.flag")
