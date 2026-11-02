"""Interfaz web de prueba: sube un contrato y su enmienda y compara los cambios.

Ejecutar: streamlit run app.py
"""

import tempfile
from pathlib import Path

import streamlit as st

from src.image_parser import ContractParsingError
from src.main import langfuse, run_pipeline
from src.models import ContractChangeOutput

IMAGE_TYPES = ["jpg", "jpeg", "png"]


def compare(original_file, amendment_file) -> ContractChangeOutput:
    """Guarda las imágenes subidas en archivos temporales y ejecuta el pipeline."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_path = Path(tmp_dir) / f"original{Path(original_file.name).suffix}"
        amendment_path = Path(tmp_dir) / f"enmienda{Path(amendment_file.name).suffix}"
        original_path.write_bytes(original_file.getvalue())
        amendment_path.write_bytes(amendment_file.getvalue())

        result = run_pipeline(str(original_path), str(amendment_path))

    langfuse.flush()  # Envía la traza a Langfuse de inmediato
    return result


def show_result(result: ContractChangeOutput) -> None:
    """Muestra el resultado de forma legible."""
    st.success(f"Análisis completo: {len(result.sections_changed)} secciones con cambios.")

    col_sections, col_topics = st.columns(2)
    with col_sections:
        st.subheader("Secciones modificadas")
        for section in result.sections_changed:
            st.markdown(f"- {section}")
    with col_topics:
        st.subheader("Temas afectados")
        for topic in result.topics_touched:
            st.markdown(f"- {topic}")

    st.subheader("Detalle de cambios")
    for line in result.summary_of_the_change.splitlines():
        if line.strip():
            st.markdown(f"- {line}")

    with st.expander("Ver JSON"):
        st.json(result.model_dump())
    st.download_button(
        "Descargar JSON",
        data=result.model_dump_json(indent=2),
        file_name="cambios_contrato.json",
        mime="application/json",
    )


st.set_page_config(page_title="Comparador de Contratos", page_icon="📄", layout="wide")
st.title("📄 Comparador de Contratos")
st.caption("Sube el contrato original y su enmienda. El sistema detecta qué cambió.")

col_original, col_amendment = st.columns(2)
with col_original:
    original_file = st.file_uploader("Contrato original", type=IMAGE_TYPES)
    if original_file:
        st.image(original_file)
with col_amendment:
    amendment_file = st.file_uploader("Enmienda", type=IMAGE_TYPES)
    if amendment_file:
        st.image(amendment_file)

both_uploaded = original_file is not None and amendment_file is not None
if st.button("Comparar contratos", type="primary", disabled=not both_uploaded):
    with st.spinner("Analizando los contratos... (unos 10 segundos)"):
        try:
            st.session_state["result"] = compare(original_file, amendment_file)
        except (FileNotFoundError, ValueError, ContractParsingError, RuntimeError) as error:
            st.error(f"No se pudo completar el análisis: {error}")

if "result" in st.session_state:
    show_result(st.session_state["result"])