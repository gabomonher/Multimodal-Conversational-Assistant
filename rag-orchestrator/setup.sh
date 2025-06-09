#!/bin/bash
# setup.sh - Script de configuración para EC2

echo "🚀 Configurando RAG Orchestrator..."

# Actualizar sistema
sudo apt update
sudo apt upgrade -y

# Instalar Python y pip
sudo apt install python3-pip python3-venv -y

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Crear archivo .env
cat > .env << EOL
CHROMA_HOST=172.31.16.55
CHROMA_PORT=8000
LLM_ENDPOINT=https://your-ngrok-url.ngrok-free.app
EOL

echo "Configuración completada!"
echo "Para ejecutar la aplicación:"
echo "1. source venv/bin/activate"
echo "2. streamlit run app.py" 