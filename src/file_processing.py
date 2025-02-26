from .data_ingestion import load_documents
from .embedding_store import store_embeddings
from .retrieval import db  # Importa db directamente desde retrieval
import os
import json
import datetime

# Nombre del archivo JSON para tracking
PROCESSED_SOURCES_FILE = "processed_sources.json"


def get_processed_sources_from_chromadb():
    """Obtiene directamente de ChromaDB las fuentes existentes."""
    try:
        documents = db.get()
        sources = set()
        for metadata in documents.get("metadatas", []):
            if "source" in metadata:
                sources.add(metadata["source"])
        return sources
    except Exception as e:
        print(f"Error al consultar ChromaDB directamente: {str(e)}")
        return set()


def get_processed_sources_from_json():
    """Obtiene un conjunto de fuentes ya procesadas desde el archivo JSON."""
    if os.path.exists(PROCESSED_SOURCES_FILE):
        try:
            with open(PROCESSED_SOURCES_FILE, "r") as f:
                data = json.load(f)
                # Extraer solo los nombres de las fuentes
                return set(item["source"] for item in data.get("documents", []))
        except json.JSONDecodeError:
            print(
                f"Error decodificando {PROCESSED_SOURCES_FILE}. Creando nuevo archivo."
            )
            create_json_file()
            return set()
    else:
        # Crear el archivo si no existe
        create_json_file()
        return set()


def create_json_file():
    """Crea un nuevo archivo JSON con estructura básica."""
    with open(PROCESSED_SOURCES_FILE, "w") as f:
        json.dump({"documents": []}, f, indent=2)


def get_processed_sources():
    """Obtiene un conjunto de fuentes procesadas, priorizando ChromaDB."""
    # Primero intentar obtener de ChromaDB
    chromadb_sources = get_processed_sources_from_chromadb()

    # Luego obtener del archivo JSON
    json_sources = get_processed_sources_from_json()

    # Combinar ambos conjuntos
    combined_sources = chromadb_sources.union(json_sources)

    # Actualizar el archivo JSON si hay diferencias
    if chromadb_sources.difference(json_sources):
        update_json_with_new_sources(chromadb_sources.difference(json_sources))

    return combined_sources


def update_json_with_new_sources(new_sources):
    """Actualiza el archivo JSON con nuevas fuentes encontradas en ChromaDB."""
    try:
        # Cargar el archivo existente
        if os.path.exists(PROCESSED_SOURCES_FILE):
            with open(PROCESSED_SOURCES_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {"documents": []}

        # Añadir las nuevas fuentes con marca de tiempo
        timestamp = datetime.datetime.now().isoformat()
        for source in new_sources:
            data["documents"].append(
                {"source": source, "processed_at": timestamp, "method": "chromadb_sync"}
            )

        # Guardar el archivo actualizado
        with open(PROCESSED_SOURCES_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error actualizando {PROCESSED_SOURCES_FILE}: {str(e)}")


def mark_source_as_processed(source):
    """Marca una fuente como procesada en el archivo JSON."""
    try:
        # Cargar el archivo existente
        if os.path.exists(PROCESSED_SOURCES_FILE):
            with open(PROCESSED_SOURCES_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {"documents": []}

        # Añadir la nueva fuente con marca de tiempo
        timestamp = datetime.datetime.now().isoformat()
        data["documents"].append(
            {"source": source, "processed_at": timestamp, "method": "direct_upload"}
        )

        # Guardar el archivo actualizado
        with open(PROCESSED_SOURCES_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error al marcar la fuente como procesada: {str(e)}")
        # Como respaldo, intentar con el antiguo método
        with open("processed_sources.txt", "a") as f:
            f.write(source + "\n")


def process_file_and_add_to_chroma(file_path):
    """Procesa un archivo y lo añade a ChromaDB si no existe."""
    processed_sources = get_processed_sources()
    docs = load_documents()
    new_docs = [doc for doc in docs if doc.metadata["source"] not in processed_sources]

    if new_docs:
        store_embeddings(new_docs)
        for doc in new_docs:
            mark_source_as_processed(doc.metadata["source"])
        print(
            f"Procesados {len(new_docs)} documentos nuevos. Base de datos lista para consultas."
        )
    else:
        print("No hay nuevos documentos para procesar.")
