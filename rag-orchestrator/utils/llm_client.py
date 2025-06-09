import requests
from typing import Dict, List, Optional

class LLMClient:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
    
    def test_connection(self) -> bool:
        try:
            response = requests.get(self.endpoint + "/health")
            return response.status_code == 200
        except Exception:
            return False
    
    def generate_response(
        self,
        prompt: str,
        context: List[Dict],
        max_tokens: int = 500
    ) -> str:
        """
        Genera una respuesta usando el modelo de lenguaje.
        
        Args:
            prompt: La consulta del usuario
            context: Lista de documentos de contexto
            max_tokens: Número máximo de tokens en la respuesta
            
        Returns:
            str: La respuesta generada
        """
        try:
            # Preparar el prompt con el contexto
            context_text = "\n\n".join([
                f"Documento {i+1}:\n{doc['text']}"
                for i, doc in enumerate(context)
            ])
            
            full_prompt = f"""Contexto:
{context_text}

Consulta: {prompt}

Por favor, genera una respuesta basada en el contexto proporcionado:"""
            
            # Realizar la petición al endpoint
            response = requests.post(
                self.endpoint + "/generate",
                json={
                    "prompt": full_prompt,
                    "max_tokens": max_tokens
                }
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                raise Exception(f"Error en la generación: {response.text}")
                
        except Exception as e:
            raise Exception(f"Error al generar respuesta: {str(e)}") 