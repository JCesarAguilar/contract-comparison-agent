"""Tests de validación y codificación de imágenes. No llaman a la API."""

from pathlib import Path

import pytest

from src.image_parser import encode_image, validate_image

SAMPLE_IMAGE = (
    Path(__file__).parent.parent / "data/test_contracts/documento_1__original.jpg"
)


def test_accepts_valid_image():
    path = validate_image(SAMPLE_IMAGE)
    assert path.name == "documento_1__original.jpg"


def test_rejects_missing_file():
    with pytest.raises(FileNotFoundError):
        validate_image("data/test_contracts/no_existe.jpg")


def test_rejects_unsupported_extension(tmp_path):
    pdf_file = tmp_path / "contrato.pdf"
    pdf_file.write_bytes(b"contenido")
    with pytest.raises(ValueError):
        validate_image(pdf_file)


def test_rejects_empty_file(tmp_path):
    empty_file = tmp_path / "vacio.jpg"
    empty_file.touch()
    with pytest.raises(ValueError):
        validate_image(empty_file)


def test_encode_image_returns_data_url():
    data_url = encode_image(validate_image(SAMPLE_IMAGE))
    assert data_url.startswith("data:image/jpeg;base64,")
