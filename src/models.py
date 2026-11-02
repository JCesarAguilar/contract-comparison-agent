"""Modelo de salida del sistema: el resultado validado que devuelve el Agente 2."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ContractChangeOutput(BaseModel):
    """Cambios detectados entre un contrato original y su enmienda."""

    # Rechaza cualquier campo que no esté definido aquí (ej. si el modelo inventa uno)
    model_config = ConfigDict(extra="forbid")

    sections_changed: list[str] = Field(
        description=(
            "Secciones del contrato que fueron modificadas, agregadas o eliminadas, "
            "tal como aparecen en el documento (ej. '3. Pago')."
        )
    )
    topics_touched: list[str] = Field(
        description=(
            "Categorías legales o comerciales afectadas por los cambios "
            "(ej. 'Precio', 'Plazo', 'Confidencialidad')."
        )
    )
    summary_of_the_change: str = Field(
        description=(
            "Descripción detallada de cada cambio: indica si es una adición, "
            "eliminación o modificación, y el valor anterior y el nuevo."
        )
    )

    @field_validator("summary_of_the_change")
    @classmethod
    def summary_not_empty(cls, value: str) -> str:
        """El resumen es el corazón del resultado: no puede venir vacío."""
        if not value.strip():
            raise ValueError("El resumen de cambios no puede estar vacío.")
        return value.strip()
