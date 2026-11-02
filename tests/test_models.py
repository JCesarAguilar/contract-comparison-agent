"""Tests del schema de salida. No llaman a la API."""

import pytest
from pydantic import ValidationError

from src.models import ContractChangeOutput

VALID_OUTPUT = {
    "sections_changed": ["2. Plazo"],
    "topics_touched": ["Plazo"],
    "summary_of_the_change": "[MODIFICACIÓN] 2. Plazo: 12 meses → 24 meses",
}


def test_accepts_valid_output():
    result = ContractChangeOutput.model_validate(VALID_OUTPUT)
    assert result.sections_changed == ["2. Plazo"]


def test_strips_summary_spaces():
    data = {**VALID_OUTPUT, "summary_of_the_change": "  Cambio en el plazo.  "}
    result = ContractChangeOutput.model_validate(data)
    assert result.summary_of_the_change == "Cambio en el plazo."


def test_rejects_missing_field():
    data = {
        key: value for key, value in VALID_OUTPUT.items() if key != "topics_touched"
    }
    with pytest.raises(ValidationError):
        ContractChangeOutput.model_validate(data)


def test_rejects_extra_field():
    with pytest.raises(ValidationError):
        ContractChangeOutput.model_validate({**VALID_OUTPUT, "risk_level": "alto"})


def test_rejects_wrong_type():
    with pytest.raises(ValidationError):
        ContractChangeOutput.model_validate(
            {**VALID_OUTPUT, "sections_changed": "2. Plazo"}
        )


def test_rejects_empty_summary():
    with pytest.raises(ValidationError):
        ContractChangeOutput.model_validate(
            {**VALID_OUTPUT, "summary_of_the_change": "   "}
        )
