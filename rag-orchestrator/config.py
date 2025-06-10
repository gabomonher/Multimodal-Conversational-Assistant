# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# --- Configuración de ChromaDB (Esta parte está bien) ---
CHROMA_HOST = os.getenv("CHROMA_HOST", "172.31.16.55")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "collection_patron3")

# --- Configuración del Modelo de Lenguaje (LLM) ---
# ¡AQUÍ ESTÁ LA CORRECCIÓN!
# Reemplaza la URL de ejemplo con la que te pasó tu compañero.
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "https://25fe-35-231-144-33.ngrok-free.app")

# --- Configuración de la Aplicación ---
MAX_RESULTS = 11
