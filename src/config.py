import os

from dotenv import load_dotenv

load_dotenv()

# Fallar al inicio si falta la clave, en vez de fallar a mitad del proceso
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("Falta OPENAI_API_KEY en el archivo .env")

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
AGENT_MODEL = "gpt-4o"
AGENT_TEMPERATURE = 0
AGENT_MAX_TOKENS = 4096
