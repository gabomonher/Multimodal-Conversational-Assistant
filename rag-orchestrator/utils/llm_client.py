# utils/llm_client.py
import requests
from typing import Dict, List
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        logger.info(f"Cliente LLM inicializado para el endpoint: {self.endpoint}")

    def test_connection(self) -> bool:
        """
        Verifica si el endpoint del LLM está activo y es una API de FastAPI funcional.
        """
        try:
            docs_url = urljoin(self.endpoint, "docs")
            response = requests.get(docs_url, timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def generate_response(self, prompt: str, context: List[Dict], max_tokens: int = 300) -> str:
        """
        Genera una respuesta utilizando el conocimiento interno del modelo,
        complementado y verificado por el contexto proporcionado.
        """
        context_text = "\n\n".join([doc.get('document', '') for doc in context if doc.get('document')])
        
        # --- PROMPT AVANZADO: Sinergia entre Conocimiento y Contexto ---
        # Le damos al modelo un rol y un proceso de pensamiento claro.
        full_prompt = (
            "You are an expert research assistant. Your goal is to provide a comprehensive and accurate answer to the user's question. Follow these steps:\n"
            "1. First, formulate a concise answer based on your general knowledge.\n"
            "2. Second, carefully review the provided context to verify, correct, and enrich your initial answer.\n"
            "\n\n"
            f"--- Context from Knowledge Base ---\n{context_text}\n\n"
            f"--- User's Question ---\n{prompt}\n\n"
            "Assistant's Final Answer:"
        )
        
        payload = {
            "prompt": full_prompt,
            "max_tokens": max_tokens
        }
        
        generate_url = urljoin(self.endpoint, "generate")
        logger.info(f"Enviando petición de generación a: {generate_url}")
        
        try:
            response = requests.post(generate_url, json=payload, timeout=120)
            response.raise_for_status()
            
            return response.json().get("response", "The model did not return a valid response.")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Communication error with the language model: {e}")
