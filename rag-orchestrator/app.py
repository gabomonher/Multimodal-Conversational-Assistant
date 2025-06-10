# app.py
import streamlit as st
from PIL import Image
import io

# Importaciones de nuestros módulos locales
from config import CHROMA_HOST, CHROMA_PORT, CHROMA_COLLECTION_NAME, LLM_ENDPOINT, MAX_RESULTS
from utils.chroma_client import ChromaDBClient
from utils.llm_client import LLMClient
from utils.image_handler import ImageHandler

# --- CONFIGURACIÓN DE LA PÁGINA Y ESTILOS ---
st.set_page_config(
    page_title="Asistente Multimodal",
    page_icon="🧠",
    layout="wide"
)

# --- CSS PERSONALIZADO ---
st.markdown("""
<style>
    .stApp { background-color: #f4f6f9; }
    .response-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e1e4e8;
    }
    .stImage > img {
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    h2 {
        color: #1a1a2e;
        border-bottom: 2px solid #e1e4e8;
        padding-bottom: 10px;
    }
    h3 { color: #16213e; }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE CLIENTES ---
@st.cache_resource
def init_clients():
    try:
        chroma = ChromaDBClient(CHROMA_HOST, CHROMA_PORT, CHROMA_COLLECTION_NAME)
        llm = LLMClient(LLM_ENDPOINT)
        image_handler = ImageHandler()
        return chroma, llm, image_handler
    except Exception as e:
        st.error(f"Error fatal al inicializar los servicios: {e}")
        st.stop()

if 'last_query_results' not in st.session_state:
    st.session_state.last_query_results = None

chroma_client, llm_client, image_handler = init_clients()

# --- SIDEBAR (MENÚ LATERAL) ---
with st.sidebar:
    # --- CORRECCIÓN FINAL AQUÍ ---
    # Se reemplaza use_column_width=True por use_container_width=True
    st.image("https://st3.depositphotos.com/8950810/17657/v/450/depositphotos_176577880-stock-illustration-cute-smiling-funny-robot-chat.jpg", use_container_width=True)
    st.header("⚙️ Estado de Servicios")
    
    chroma_status = "🟢 Conectado" if chroma_client and chroma_client.test_connection() else "🔴 Desconectado"
    llm_status = "🟢 Conectado" if llm_client and llm_client.test_connection() else "🔴 Desconectado"
    
    st.success(f"ChromaDB: {chroma_status}")
    st.success(f"Modelo LLM: {llm_status}")
    
    if chroma_status == "🔴 Desconectado" or llm_status == "🔴 Desconectado":
        st.warning("Uno o más servicios no están disponibles.")
    
    st.divider()
    
    with st.expander("🔍 Ver Últimos Resultados de la BBDD"):
        if st.session_state.last_query_results:
            st.json(st.session_state.last_query_results)
        else:
            st.info("Realiza una búsqueda para ver los resultados aquí.")

# --- LAYOUT PRINCIPAL ---
st.title("🧠 Asistente de Conocimiento Multimodal")
st.markdown("### Interactúa con tu base de conocimiento usando texto o imágenes")

tab1, tab2 = st.tabs(["📝 Consulta por Texto", "🖼️ Consulta por Imagen"])

with tab1:
    with st.container():
        text_query = st.text_area("Escribe tu pregunta aquí:", height=100, placeholder="Ej: ¿Qué es la huella de carbono y cómo se puede reducir?")
        
        if st.button("✨ Generar Respuesta", key="text_search", use_container_width=True):
            if chroma_client and llm_client and text_query:
                with st.spinner("Buscando en la base de conocimiento y generando una respuesta..."):
                    try:
                        results_raw = chroma_client.query_multimodal(query_text=text_query, n_results=MAX_RESULTS)
                        st.session_state.last_query_results = results_raw
                        
                        results = image_handler.format_chroma_results(results_raw)
                        response = llm_client.generate_response(prompt=text_query, context=results)
                        
                        st.markdown("<h2>💬 Respuesta del Asistente</h2>", unsafe_allow_html=True)
                        st.markdown(f"<div class='response-card'>{response}</div>", unsafe_allow_html=True)
                        
                        images = [r for r in results if r['has_image']]
                        if images:
                            st.markdown("<h3>🖼️ Imágenes de Contexto</h3>", unsafe_allow_html=True)
                            cols = st.columns(len(images))
                            for idx, res in enumerate(images):
                                with cols[idx]:
                                    st.image(image_handler.decode_image_from_b64(res['image']), 
                                             caption=f"Relevancia: {1-res['distance']:.2%}", 
                                             use_container_width=True)
                    except Exception as e:
                        st.error(f"Ocurrió un error al procesar la consulta: {e}")
            else:
                st.warning("Por favor, escribe una pregunta y asegúrate de que los servicios estén conectados.")

with tab2:
    with st.container():
        uploaded_file = st.file_uploader("Sube una imagen para buscar contenido similar:", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(uploaded_file, caption="Imagen cargada", use_container_width=True)
            
            with col2:
                st.write("Usa la imagen subida para encontrar información y contenido visual similar en la base de conocimiento.")
                if st.button("🔍 Buscar Similares", key="image_search", use_container_width=True):
                    if chroma_client and llm_client:
                        with st.spinner("Analizando imagen y generando análisis..."):
                            try:
                                image_bytes = uploaded_file.getvalue()
                                results_raw = chroma_client.query_multimodal(query_image=image_bytes, n_results=MAX_RESULTS)
                                st.session_state.last_query_results = results_raw
                                
                                results = image_handler.format_chroma_results(results_raw)
                                prompt = "Basado en el contexto recuperado, describe qué información está relacionada con la imagen que he subido."
                                response = llm_client.generate_response(prompt=prompt, context=results)

                                st.markdown("<h2>💬 Análisis del Asistente</h2>", unsafe_allow_html=True)
                                st.markdown(f"<div class='response-card'>{response}</div>", unsafe_allow_html=True)

                                images = [r for r in results if r['has_image']]
                                if images:
                                    st.markdown("<h3>🖼️ Contenido Similar Encontrado</h3>", unsafe_allow_html=True)
                                    cols = st.columns(len(images))
                                    for idx, res in enumerate(images):
                                        with cols[idx]:
                                            st.image(image_handler.decode_image_from_b64(res['image']), 
                                                     caption=f"Similitud: {1-res['distance']:.2%}", 
                                                     use_container_width=True)
                            except Exception as e:
                                st.error(f"Ocurrió un error al procesar la imagen: {e}")
