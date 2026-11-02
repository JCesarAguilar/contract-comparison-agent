"""Lee contratos escaneados con GPT-4o (visión) y devuelve su texto."""

import base64
import sys
from pathlib import Path

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from src import config
from src.prompts.vision import VISION_SYSTEM_PROMPT, VISION_USER_PROMPT

client = OpenAI(timeout=config.API_TIMEOUT_SECONDS, max_retries=config.API_MAX_RETRIES)


class ContractParsingError(Exception):
    """No se pudo obtener una transcripción válida del contrato."""


def validate_image(image_path: str) -> Path:
    """Revisa que la imagen exista, sea JPG o PNG, no esté vacía y no sea demasiado grande."""
    path = Path(image_path)

    if not path.is_file():
        raise FileNotFoundError(f"No existe la imagen: {image_path}")
    if path.suffix.lower() not in config.ALLOWED_EXTENSIONS:
        raise ValueError(f"Formato no permitido: {path.suffix}. Usa JPG o PNG.")

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb == 0:
        raise ValueError(f"La imagen está vacía: {image_path}")
    if size_mb > config.MAX_IMAGE_MB:
        raise ValueError(
            f"La imagen pesa {size_mb:.1f} MB. Máximo: {config.MAX_IMAGE_MB} MB."
        )

    return path


def encode_image(path: Path) -> str:
    """Convierte la imagen a texto base64 para poder enviarla a la API."""
    image_base64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    image_type = "png" if path.suffix.lower() == ".png" else "jpeg"
    return f"data:image/{image_type};base64,{image_base64}"


def parse_contract_image(image_path: str) -> dict:
    """Envía la imagen a GPT-4o y devuelve el texto del contrato y los tokens usados."""
    path = validate_image(image_path)
    image_url = encode_image(path)

    # Si llegamos a un except, el SDK ya agotó sus reintentos automáticos
    try:
        response = client.chat.completions.create(
            model=config.VISION_MODEL,
            temperature=0,  # Queremos copiar, no crear: respuestas estables
            max_completion_tokens=config.MAX_TOKENS,
            messages=[
                {"role": "system", "content": VISION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": VISION_USER_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                                "detail": config.IMAGE_DETAIL,
                            },
                        },
                    ],
                },
            ],
        )
    except AuthenticationError as error:
        raise ContractParsingError(
            "La API key de OpenAI no es válida. Revisa tu archivo .env."
        ) from error
    except (RateLimitError, APITimeoutError, APIConnectionError) as error:
        # Fallas temporales: el SDK ya reintentó 3 veces antes de llegar aquí
        raise ContractParsingError(
            f"OpenAI no respondió para '{path.name}' tras varios intentos. Intenta más tarde."
        ) from error
    except APIStatusError as error:
        raise ContractParsingError(
            f"OpenAI respondió con error {error.status_code}: {error.message}"
        ) from error

    choice = response.choices[0]
    text = choice.message.content

    if choice.finish_reason == "length":
        raise ContractParsingError(
            f"La transcripción de '{path.name}' quedó cortada. Aumenta MAX_TOKENS."
        )
    if not text:
        raise ContractParsingError(
            f"El modelo devolvió una respuesta vacía para '{path.name}'."
        )

    usage = response.usage  # Puede venir vacío; en ese caso registramos 0
    return {
        "text": text.strip(),
        "model": response.model,
        "input_tokens": usage.prompt_tokens if usage else 0,
        "output_tokens": usage.completion_tokens if usage else 0,
    }


# Prueba: python -m src.image_parser data/test_contracts/documento_1__original.jpg
if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: python -m src.image_parser <ruta_de_la_imagen>")

    result = parse_contract_image(sys.argv[1])
    print(result["text"])
    print(
        f"\nModelo: {result['model']} | Tokens -> entrada: {result['input_tokens']} | salida: {result['output_tokens']}"
    )
