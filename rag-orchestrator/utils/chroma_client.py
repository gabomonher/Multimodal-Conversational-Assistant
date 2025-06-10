# utils/chroma_client.py
import chromadb
import torch
from PIL import Image
import io
import logging
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from transformers import BlipProcessor, BlipForConditionalGeneration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaDBClient:
    def __init__(self, host: str, port: str, collection_name: str):
        logger.info("Inicializando ChromaDBClient para PATRÓN 3...")
        try:
            self.client = chromadb.HttpClient(host=host, port=int(port))
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Usando dispositivo: {device}")

            logger.info("Cargando modelo de embeddings de texto (all-MiniLM-L6-v2)...")
            self.text_embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
            
            logger.info("Cargando modelo de descripción de imágenes (BLIP)...")
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to(device)
            
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Conectado a la colección: '{self.collection.name}'.")

        except Exception as e:
            logger.error(f"Error fatal durante la inicialización: {e}")
            raise

    def _embed_text(self, text: str) -> List[List[float]]:
        embedding = self.text_embedding_model.encode([text], convert_to_tensor=True)
        return embedding.cpu().tolist()

    def _get_image_caption(self, image_data: bytes) -> str:
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        inputs = self.blip_processor(image, return_tensors="pt").to(self.blip_model.device)
        out = self.blip_model.generate(**inputs, max_new_tokens=50)
        return self.blip_processor.decode(out[0], skip_special_tokens=True)

    def query_multimodal(self, query_text: Optional[str] = None, query_image: Optional[bytes] = None, n_results: int = 5) -> Dict[str, Any]:
        if query_text:
            query_vector = self._embed_text(query_text)
        elif query_image:
            caption = self._get_image_caption(query_image)
            logger.info(f"Descripción generada para la imagen: '{caption}'")
            query_vector = self._embed_text(caption)
        else:
            raise ValueError("Se debe proporcionar un texto o una imagen.")

        return self.collection.query(query_embeddings=query_vector, n_results=n_results, include=["metadatas", "documents", "distances"])

    def test_connection(self) -> bool:
        try:
            self.client.heartbeat()
            return True
        except Exception:
            return False
