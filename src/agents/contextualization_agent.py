"""Agente 1: construye el mapa estructural de ambos contratos. No extrae cambios."""

import sys

from langchain_core.exceptions import ModelError
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src import config
from src.prompts.contextualization import (
    CONTEXTUALIZATION_SYSTEM_PROMPT,
    CONTEXTUALIZATION_USER_PROMPT,
)


class ContextualizationAgent:
    """Analista Legal Senior: mapea qué sección del original corresponde a cuál de la enmienda."""

    def __init__(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", CONTEXTUALIZATION_SYSTEM_PROMPT),
                ("human", CONTEXTUALIZATION_USER_PROMPT),
            ]
        )
        llm = ChatOpenAI(
            model=config.AGENT_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            max_completion_tokens=config.AGENT_MAX_TOKENS,
            timeout=config.API_TIMEOUT_SECONDS,
            max_retries=config.API_MAX_RETRIES,
        )
        self.chain = prompt | llm  # LCEL: el prompt se completa y pasa al modelo

    def run(self, original_text: str, amendment_text: str) -> dict:
        """Devuelve el mapa contextual y los tokens usados."""
        try:
            response = self.chain.invoke(
                {"original_text": original_text, "amendment_text": amendment_text}
            )
        except ModelError as error:
            # Cubre API key inválida, límites de uso, timeouts y caídas de conexión
            raise RuntimeError(
                f"El Agente de contextualización falló ({type(error).__name__}): {error}"
            ) from error

        if response.response_metadata.get("finish_reason") == "length":
            raise RuntimeError(
                "El mapa contextual quedó cortado. Aumenta AGENT_MAX_TOKENS."
            )
        if not response.content:
            raise RuntimeError(
                "El Agente de contextualización devolvió una respuesta vacía."
            )

        usage = response.usage_metadata  # Puede venir vacío; en ese caso registramos 0
        return {
            "context_map": response.content,
            "input_tokens": usage["input_tokens"] if usage else 0,
            "output_tokens": usage["output_tokens"] if usage else 0,
        }


# Prueba: python -m src.agents.contextualization_agent <original.jpg> <enmienda.jpg>
if __name__ == "__main__":
    from src.image_parser import parse_contract_image

    if len(sys.argv) != 3:
        sys.exit(
            "Uso: python -m src.agents.contextualization_agent <original> <enmienda>"
        )

    original = parse_contract_image(sys.argv[1])["text"]
    amendment = parse_contract_image(sys.argv[2])["text"]
    result = ContextualizationAgent().run(original, amendment)

    print(result["context_map"])
    print(
        f"\nTokens -> entrada: {result['input_tokens']} | salida: {result['output_tokens']}"
    )
