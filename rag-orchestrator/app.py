# app.py
import streamlit as st
import requests
from PIL import Image
import io
import base64
import time
from typing import Optional

from config import *
from utils.chroma_client import ChromaDBClient
from utils.llm_client import LLMClient
from utils.image_handler import ImageHandler

# Configuración de la página
st.set_page_config(
    page_title="RAG Multimodal - Vida Artificial",
    page_icon="🤖",
    layout="wide"
)

# Inicializar clientes en session state
@st.cache_resource
def init_clients():
    try:
        chroma = ChromaDBClient(CHROMA_HOST, CHROMA_PORT, CHROMA_COLLECTION_NAME)
        llm = LLMClient(LLM_ENDPOINT)
        return chroma, llm, True
    except Exception as e:
        st.error(f"Error inicializando clientes: {e}")
        return None, None, False

# CSS personalizado
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stImage {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .result-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .status-connected {
        background-color: #00cc00;
    }
    .status-disconnected {
        background-color: #cc0000;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🤖 Sistema RAG Multimodal")
st.markdown("### Proyecto Final - Vida Artificial")

# Inicializar clientes
chroma_client, llm_client, services_ok = init_clients()
image_handler = ImageHandler()

# Mostrar estado de conexión
col1, col2 = st.columns(2)
with col1:
    chroma_status = "🟢 Conectado" if chroma_client and chroma_client.test_connection() else "🔴 Desconectado"
    st.markdown(f"**ChromaDB:** {chroma_status}")
with col2:
    llm_status = "🟢 Conectado" if llm_client and llm_client.test_connection() else "🔴 Desconectado"
    st.markdown(f"**LLM:** {llm_status}")

st.divider()

# Tabs para diferentes tipos de consulta
tab1, tab2 = st.tabs(["📝 Consulta por Texto", "🖼️ Consulta por Imagen"])

with tab1:
    st.markdown("### Realizar consulta por texto")
    text_query = st.text_area(
        "Escribe tu pregunta:",
        placeholder="Por ejemplo: ¿Qué es la inteligencia artificial?",
        height=100
    )
    
    if st.button("🔍 Buscar", key="text_search"):
        if text_query and services_ok:
            with st.spinner("Procesando consulta..."):
                try:
                    # Recuperar contexto de ChromaDB
                    search_results = chroma_client.query_multimodal(
                        query_text=text_query,
                        n_results=MAX_RESULTS
                    )
                    
                    # Procesar resultados con imágenes
                    processed_results = image_handler.process_results_with_images(
                        search_results.get('results', [])
                    )
                    
                    # Generar respuesta con LLM
                    llm_response = llm_client.generate_response(
                        prompt=text_query,
                        context=processed_results
                    )
                    
                    # Mostrar resultados
                    st.success("✅ Consulta procesada exitosamente")
                    
                    # Respuesta del LLM
                    st.markdown("### 💬 Respuesta:")
                    st.write(llm_response)
                    
                    # Mostrar imágenes relacionadas
                    images_with_content = [r for r in processed_results if r.get('has_image')]
                    if images_with_content:
                        st.markdown("### 🖼️ Imágenes relacionadas:")
                        
                        # Crear columnas para las imágenes
                        cols = st.columns(min(3, len(images_with_content)))
                        for idx, result in enumerate(images_with_content[:3]):
                            with cols[idx]:
                                if result.get('image'):
                                    # Decodificar imagen base64
                                    if result['image'].startswith('data:image'):
                                        image_data = result['image'].split(',')[1]
                                    else:
                                        image_data = result['image']
                                    
                                    image_bytes = base64.b64decode(image_data)
                                    image = Image.open(io.BytesIO(image_bytes))
                                    
                                    st.image(image, use_column_width=True)
                                    
                                    # Mostrar caption si existe
                                    caption = result.get('metadata', {}).get('title', 'Imagen relacionada')
                                    st.caption(caption)
                    
                    # Detalles adicionales (expandible)
                    with st.expander("📊 Ver detalles de la búsqueda"):
                        st.json({
                            "query": text_query,
                            "num_results": len(processed_results),
                            "results_with_images": len(images_with_content)
                        })
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            if not text_query:
                st.warning("Por favor, ingresa una consulta")
            else:
                st.error("Los servicios no están disponibles")

with tab2:
    st.markdown("### Realizar consulta por imagen")
    uploaded_file = st.file_uploader(
        "Selecciona una imagen:",
        type=['png', 'jpg', 'jpeg'],
        help="Formatos soportados: PNG, JPG, JPEG"
    )
    
    if uploaded_file is not None:
        # Mostrar preview de la imagen
        col1, col2 = st.columns([1, 2])
        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption="Imagen cargada", use_column_width=True)
        
        with col2:
            if st.button("🔍 Buscar similares", key="image_search"):
                if services_ok:
                    with st.spinner("Analizando imagen..."):
                        try:
                            # Leer imagen
                            uploaded_file.seek(0)
                            image_data = uploaded_file.read()
                            
                            # Buscar en ChromaDB
                            st.info("⚠️ Nota: La búsqueda por imagen requiere embeddings OpenCLIP")
                            search_results = chroma_client.query_multimodal(
                                query_image=image_data,
                                n_results=MAX_RESULTS
                            )
                            
                            # Procesar resultados
                            processed_results = image_handler.process_results_with_images(
                                search_results.get('results', [])
                            )
                            
                            # Generar descripción con LLM
                            context_prompt = "Basándote en los resultados encontrados, describe qué información está relacionada con la imagen proporcionada."
                            llm_response = llm_client.generate_response(
                                prompt=context_prompt,
                                context=processed_results
                            )
                            
                            # Mostrar resultados
                            st.success("✅ Análisis completado")
                            
                            st.markdown("### 💬 Análisis:")
                            st.write(llm_response)
                            
                            # Mostrar imágenes similares encontradas
                            images_found = [r for r in processed_results if r.get('has_image')]
                            if images_found:
                                st.markdown("### 🖼️ Imágenes similares encontradas:")
                                cols = st.columns(min(3, len(images_found)))
                                for idx, result in enumerate(images_found[:3]):
                                    with cols[idx]:
                                        if result.get('image'):
                                            # Procesar y mostrar imagen
                                            if result['image'].startswith('data:image'):
                                                image_data = result['image'].split(',')[1]
                                            else:
                                                image_data = result['image']
                                            
                                            image_bytes = base64.b64decode(image_data)
                                            similar_image = Image.open(io.BytesIO(image_bytes))
                                            
                                            st.image(similar_image, use_column_width=True)
                                            
                                            # Caption
                                            caption = result.get('metadata', {}).get('title', f'Similitud: {1 - result.get("distance", 1):.2%}')
                                            st.caption(caption)
                            
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                else:
                    st.error("Los servicios no están disponibles")

# Sidebar con configuración
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    
    with st.form("config_form"):
        st.markdown("### Conexión ChromaDB")
        new_chroma_host = st.text_input(
            "Host:", 
            value=CHROMA_HOST,
            help="IP o hostname del servidor ChromaDB"
        )
        new_chroma_port = st.text_input(
            "Puerto:", 
            value=CHROMA_PORT,
            help="Puerto del servidor ChromaDB"
        )
        
        st.markdown("### Endpoint LLM")
        new_llm_endpoint = st.text_input(
            "URL Ngrok:", 
            value=LLM_ENDPOINT,
            help="URL del endpoint Ngrok desde Colab"
        )
        
        if st.form_submit_button("Actualizar Configuración"):
            # Actualizar variables globales
            CHROMA_HOST = new_chroma_host
            CHROMA_PORT = new_chroma_port
            LLM_ENDPOINT = new_llm_endpoint
            
            # Reinicializar clientes
            st.cache_resource.clear()
            st.rerun()
    
    st.divider()
    
    # Información del sistema
    st.markdown("### 📊 Información del Sistema")
    st.info("""
    **Componentes:**
    - Base de Datos: ChromaDB
    - Embeddings: OpenCLIP
    - LLM: Via Ngrok (Colab)
    - Patrón: Multimodal RAG (Patrón 2)
    """)
    
    # Instrucciones
    with st.expander("📖 Instrucciones de Uso"):
        st.markdown("""
        1. **Consulta por Texto**: Escribe tu pregunta y el sistema buscará información relevante
        2. **Consulta por Imagen**: Sube una imagen para encontrar contenido similar
        3. **Configuración**: Actualiza los endpoints si es necesario
        
        **Nota**: Asegúrate de que tanto ChromaDB como el endpoint de Ngrok estén activos.
        """)

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Proyecto Final - Vida Artificial | Sistema RAG Multimodal</p>
    </div>
    """,
    unsafe_allow_html=True
) 