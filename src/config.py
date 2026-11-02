import os

from dotenv import load_dotenv

load_dotenv()

# Fallar al inicio si falta la clave, en vez de fallar a mitad del proceso
for key in ("OPENAI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"):
    if not os.getenv(key):
        raise RuntimeError(f"Falta {key} en el archivo .env")

# --- Cliente OpenAI ---
API_TIMEOUT_SECONDS = 60

# El SDK reintenta solo timeouts, límites de uso (429) y errores del servidor
API_MAX_RETRIES = 3

# --- Parsing de imágenes ---
VISION_MODEL = "gpt-4o"
IMAGE_DETAIL = "high"  # Alta resolución para leer letra chica
MAX_TOKENS = 4096  # Máximo de tokens en la respuesta
MAX_IMAGE_MB = 20
ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png"]

# --- Agentes ---
CONTEXTUALIZATION_MODEL = "gpt-4o-mini"  # Tarea simple: emparejar secciones
EXTRACTION_MODEL = "gpt-4o"  # Tarea crítica: detectar cambios sutiles
AGENT_TEMPERATURE = 0
AGENT_MAX_TOKENS = 4096
