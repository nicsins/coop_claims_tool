import json
import os
from pathlib import Path

import pytest


@pytest.fixture
def dataset_path(tmp_path: Path) -> Path:
    source = Path(__file__).resolve().parent.parent / "claims_dataset.json"
    target = tmp_path / "claims_dataset.json"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return target


@pytest.fixture
def dataset_env(dataset_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CLAIMS_DATASET_FILE", str(dataset_path))
    monkeypatch.delenv("CLAIMS_API_KEY", raising=False)
    monkeypatch.setenv("STRIPE_MOCK_MODE", "true")
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
