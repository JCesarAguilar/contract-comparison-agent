"""Punto de entrada: compara un contrato original con su enmienda.

Uso: python -m src.main <imagen_contrato_original> <imagen_enmienda>
"""

import sys

from langfuse import get_client

from src import config
from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent
from src.image_parser import ContractParsingError, parse_contract_image
from src.models import ContractChangeOutput

langfuse = get_client()  # Lee las claves de Langfuse desde el .env


def parse_step(span_name: str, image_path: str) -> str:
    """Transcribe una imagen y lo registra como un paso de la traza."""
    with langfuse.start_as_current_observation(
        as_type="generation",
        name=span_name,
        model=config.VISION_MODEL,
        input={"image_path": image_path},  # La ruta, no la imagen: evita registrar datos pesados
    ) as generation:
        parsed = parse_contract_image(image_path)
        generation.update(
            output=parsed["text"],
            model=parsed["model"],
            usage_details={"input": parsed["input_tokens"], "output": parsed["output_tokens"]},
        )
    return parsed["text"]


def run_pipeline(original_path: str, amendment_path: str) -> ContractChangeOutput:
    """Ejecuta el flujo completo dentro de una traza de Langfuse."""
    with langfuse.start_as_current_observation(
        as_type="span",
        name="contract-analysis",
        input={"original": original_path, "amendment": amendment_path},
        metadata={"vision_model": config.VISION_MODEL, "agent_model": config.AGENT_MODEL},
    ) as root:
        # Pasos 1 y 2: imágenes → texto
        original_text = parse_step("parse_original_contract", original_path)
        amendment_text = parse_step("parse_amendment_contract", amendment_path)

        # Paso 3: Agente 1 construye el mapa de secciones
        with langfuse.start_as_current_observation(
            as_type="generation",
            name="contextualization_agent",
            model=config.AGENT_MODEL,
            input={"original_text": original_text, "amendment_text": amendment_text},
        ) as generation:
            context = ContextualizationAgent().run(original_text, amendment_text)
            generation.update(
                output=context["context_map"],
                usage_details={"input": context["input_tokens"], "output": context["output_tokens"]},
            )

        # Paso 4: Agente 2 usa el mapa para extraer los cambios (handoff)
        with langfuse.start_as_current_observation(
            as_type="generation",
            name="extraction_agent",
            model=config.AGENT_MODEL,
            input={
                "context_map": context["context_map"],
                "original_text": original_text,
                "amendment_text": amendment_text,
            },
        ) as generation:
            extraction = ExtractionAgent().run(
                original_text, amendment_text, context["context_map"]
            )
            result: ContractChangeOutput = extraction["result"]
            generation.update(
                output=result.model_dump(),
                usage_details={"input": extraction["input_tokens"], "output": extraction["output_tokens"]},
            )

        root.update(output=result.model_dump())
        return result


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("Uso: python -m src.main <imagen_contrato_original> <imagen_enmienda>")

    try:
        result = run_pipeline(sys.argv[1], sys.argv[2])
    except (FileNotFoundError, ValueError, ContractParsingError, RuntimeError) as error:
        sys.exit(f"Error: {error}")
    finally:
        langfuse.flush()  # Envía las trazas pendientes a Langfuse antes de terminar

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()