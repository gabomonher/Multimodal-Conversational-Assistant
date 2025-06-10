# utils/image_handler.py
import base64
from PIL import Image
import io
from typing import List, Dict

class ImageHandler:
    def format_chroma_results(self, chroma_results: Dict) -> List[Dict]:
        if not chroma_results or not chroma_results.get('ids') or not chroma_results['ids'][0]: return []
        processed_list = []
        ids, docs, metas, dists = (chroma_results['ids'][0], chroma_results.get('documents', [[]])[0], chroma_results.get('metadatas', [[]])[0], chroma_results.get('distances', [[]])[0])
        
        for i in range(len(ids)):
            meta = metas[i] if i < len(metas) else {}
            image_b64 = meta.get('image_base64')
            item = {"id": ids[i], "document": docs[i] if i < len(docs) else "", "distance": dists[i] if i < len(dists) else 0.0, "metadata": meta, "image": image_b64, "has_image": image_b64 is not None}
            processed_list.append(item)
        return processed_list

    def decode_image_from_b64(self, base64_string: str) -> Image.Image:
        try:
            if base64_string.startswith('data:image'): base64_string = base64_string.split(',')[1]
            image_data = base64.b64decode(base64_string)
            return Image.open(io.BytesIO(image_data))
        except Exception as e:
            raise Exception(f"Error decodificando la imagen base64: {e}")
