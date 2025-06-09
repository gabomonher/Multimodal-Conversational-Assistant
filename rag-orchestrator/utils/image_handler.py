from typing import Dict, List
import base64
from PIL import Image
import io

class ImageHandler:
    def process_results_with_images(self, results: List[Dict]) -> List[Dict]:
        """
        Procesa los resultados de la búsqueda y extrae las imágenes.
        
        Args:
            results: Lista de resultados de la búsqueda
            
        Returns:
            Lista de resultados procesados con imágenes
        """
        processed_results = []
        
        for result in results:
            processed_result = result.copy()
            
            # Verificar si hay imagen en los metadatos
            if result.get('metadata', {}).get('image'):
                try:
                    # La imagen ya está en base64, solo la copiamos
                    processed_result['image'] = result['metadata']['image']
                    processed_result['has_image'] = True
                except Exception as e:
                    print(f"Error procesando imagen: {str(e)}")
                    processed_result['has_image'] = False
            else:
                processed_result['has_image'] = False
            
            processed_results.append(processed_result)
        
        return processed_results
    
    def encode_image(self, image_path: str) -> str:
        """
        Codifica una imagen a base64.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            str: Imagen codificada en base64
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Error codificando imagen: {str(e)}")
    
    def decode_image(self, base64_string: str) -> Image.Image:
        """
        Decodifica una imagen desde base64.
        
        Args:
            base64_string: String base64 de la imagen
            
        Returns:
            Image.Image: Objeto imagen de PIL
        """
        try:
            # Remover el prefijo data:image si existe
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            
            image_data = base64.b64decode(base64_string)
            return Image.open(io.BytesIO(image_data))
        except Exception as e:
            raise Exception(f"Error decodificando imagen: {str(e)}") 