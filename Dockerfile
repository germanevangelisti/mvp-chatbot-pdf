# Usa una imagen base oficial de Python
FROM python:3.9-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Instala las dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de requisitos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Crea directorios necesarios para la aplicación
RUN mkdir -p data conversation_histories

# Expone el puerto en el que se ejecuta la aplicación
EXPOSE 8000

# Define la variable de entorno para Python
ENV PYTHONPATH=/app

# Comando para ejecutar la aplicación
CMD ["python", "-m", "uvicorn", "src.web_server:app", "--host", "0.0.0.0", "--port", "8000"] 