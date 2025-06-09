# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# ChromaDB configuration
CHROMA_HOST = os.getenv("CHROMA_HOST", "172.31.16.55")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
CHROMA_COLLECTION_NAME = "wikipedia_collection"

# LLM configuration
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "https://your-ngrok-url.ngrok-free.app")

# Application configuration
MAX_RESULTS = 5