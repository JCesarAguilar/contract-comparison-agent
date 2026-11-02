"""Agente 2: detecta los cambios entre ambos contratos y devuelve un resultado validado."""

import sys

from langchain_core.exceptions import ModelError
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src import config
from src.models import ContractChangeOutput
from src.prompts.extraction import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_PROMPT


class ExtractionAgent:
    """Auditor Legal: usa el mapa del Agente 1 para encontrar cada cambio de la enmienda."""

    def __init__(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", EXTRACTION_SYSTEM_PROMPT),
                ("human", EXTRACTION_USER_PROMPT),
            ]
        )
        llm = ChatOpenAI(
            model=config.EXTRACTION_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            max_completion_tokens=config.AGENT_MAX_TOKENS,
            timeout=config.API_TIMEOUT_SECONDS,
            max_retries=config.API_MAX_RETRIES,
        )

        # Structured outputs: la API obliga al modelo a responder con el schema de Pydantic.
        # include_raw=True conserva el mensaje original para leer tokens y finish_reason.
        structured_llm = llm.with_structured_output(
            ContractChangeOutput, include_raw=True
        )
        self.chain = prompt | structured_llm

    def run(self, original_text: str, amendment_text: str, context_map: str) -> dict:
        """Devuelve el ContractChangeOutput validado y los tokens usados."""
        try:
            output = self.chain.invoke(
                {
                    "context_map": context_map,
                    "original_text": original_text,
                    "amendment_text": amendment_text,
                }
            )
        except ModelError as error:
            raise RuntimeError(
                f"El Agente de extracción falló ({type(error).__name__}): {error}"
            ) from error

        raw = output["raw"]  # Mensaje original del modelo (AIMessage)
        if raw.response_metadata.get("finish_reason") == "length":
            raise RuntimeError("La respuesta quedó cortada. Aumenta AGENT_MAX_TOKENS.")

        error = output["parsing_error"]  # Error de Pydantic, si la validación falló
        if error or output["parsed"] is None:
            raise RuntimeError(
                f"La salida no cumple el schema ContractChangeOutput: {error}"
            ) from error

        usage = raw.usage_metadata  # Puede venir vacío; en ese caso registramos 0
        return {
            "result": output["parsed"],  # Objeto ContractChangeOutput ya validado
            "input_tokens": usage["input_tokens"] if usage else 0,
            "output_tokens": usage["output_tokens"] if usage else 0,
        }


# Prueba: python -m src.agents.extraction_agent <original.jpg> <enmienda.jpg>
if __name__ == "__main__":
    from src.agents.contextualization_agent import ContextualizationAgent
    from src.image_parser import parse_contract_image

    if len(sys.argv) != 3:
        sys.exit("Uso: python -m src.agents.extraction_agent <original> <enmienda>")

    original = parse_contract_image(sys.argv[1])["text"]
    amendment = parse_contract_image(sys.argv[2])["text"]
    context_map = ContextualizationAgent().run(original, amendment)["context_map"]
    result = ExtractionAgent().run(original, amendment, context_map)

    print(result["result"].model_dump_json(indent=2))
    print(
        f"\nTokens -> entrada: {result['input_tokens']} | salida: {result['output_tokens']}"
    )
