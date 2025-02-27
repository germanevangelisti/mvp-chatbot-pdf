from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from .agent import agent
from .file_processing import process_file_and_add_to_chroma, PROCESSED_SOURCES_FILE
from .retrieval import db

import json
import os
import re
import shutil
from pathlib import Path


app = FastAPI()

# Define the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent
# Configure Jinja2Templates to look in the templates folder using an absolute path
templates = Jinja2Templates(directory=str(BASE_DIR / "src/templates"))

# Path to store conversation histories
CONVERSATION_HISTORY_PATH = str(BASE_DIR / "conversation_histories")


class QueryRequest(BaseModel):
    query: str
    source: str  # Add source to the request model


def sanitize_filename(filename):
    """Sanitize the filename to remove or replace invalid characters."""
    return re.sub(r'[<>:"/\\|?*]', "_", filename)


def save_conversation(source, conversation):
    """Save the conversation history for a specific source."""
    if not os.path.exists(CONVERSATION_HISTORY_PATH):
        os.makedirs(CONVERSATION_HISTORY_PATH)
    sanitized_source = sanitize_filename(source)
    with open(f"{CONVERSATION_HISTORY_PATH}/{sanitized_source}.json", "w") as f:
        json.dump(conversation, f)


def load_conversation(source):
    """Load the conversation history for a specific source."""
    sanitized_source = sanitize_filename(source)
    try:
        with open(f"{CONVERSATION_HISTORY_PATH}/{sanitized_source}.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def clean_source(source):
    """Remove extra information from the source string and replace slashes with underscores."""
    # Replace slashes with underscores
    sanitized_source = source.replace("/", "_")
    # Remove extra information in parentheses
    return sanitized_source.split(" (")[0]


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Renderiza la página principal."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat/")
async def chat(request: QueryRequest):
    try:
        clean_source_name = request.source.split(" (")[0]
        response = agent(request.query, clean_source_name)
        conversation = load_conversation(clean_source_name)
        conversation.append({"user": request.query, "agent": response.content})
        save_conversation(clean_source_name, conversation)
        return {"response": response.content, "history": conversation}
    except Exception as e:
        return {"error": str(e)}


@app.get("/documents/sources/")
async def list_unique_sources():
    """Endpoint para listar los diferentes archivos 'source' almacenados en ChromaDB con la cantidad de documentos por cada uno."""
    documents = db.get()

    # Verificar si hay documentos en la base de datos
    if "metadatas" not in documents or not documents["metadatas"]:
        return {"message": "No hay documentos almacenados."}

    # Contar cuántos documentos hay por cada archivo 'source'
    source_count = {}
    for metadata in documents["metadatas"]:
        if "source" in metadata:
            source = metadata["source"]
            source_count[source] = source_count.get(source, 0) + 1

    # Convertir el diccionario en una lista estructurada
    sources_list = [
        {"source": src, "document_count": count} for src, count in source_count.items()
    ]

    return {"total_sources": len(sources_list), "sources": sources_list}


@app.get("/documents/")
async def list_documents():
    """Endpoint para listar todos los documentos en ChromaDB con todos sus atributos."""
    documents = db.get()

    # Obtener la cantidad total de documentos
    total_docs = len(documents.get("ids", []))

    # Construir la lista de documentos con todos los atributos
    document_list = []
    for idx in range(total_docs):
        document_list.append(
            {
                "id": documents["ids"][idx],
                "content": (
                    documents["documents"][idx]
                    if "documents" in documents
                    else "No Content"
                ),
                "metadata": {
                    "author": documents["metadatas"][idx].get("author", "Unknown"),
                    "creationdate": documents["metadatas"][idx].get(
                        "creationdate", "Unknown"
                    ),
                    "creator": documents["metadatas"][idx].get("creator", "Unknown"),
                    "moddate": documents["metadatas"][idx].get("moddate", "Unknown"),
                    "page": documents["metadatas"][idx].get("page", "Unknown"),
                    "page_label": documents["metadatas"][idx].get(
                        "page_label", "Unknown"
                    ),
                    "producer": documents["metadatas"][idx].get("producer", "Unknown"),
                    "source": documents["metadatas"][idx].get("source", "Unknown"),
                    "title": documents["metadatas"][idx].get("title", "Unknown"),
                    "total_pages": documents["metadatas"][idx].get("total_pages", 0),
                },
            }
        )

    return {"total_documents": total_docs, "documents": document_list}


@app.get("/chat/history/{source}", response_model=list)
async def get_conversation_history(source: str):
    """Retrieve the conversation history for a specific source."""
    try:
        clean_source_name = clean_source(source)
        conversation = load_conversation(clean_source_name)
        return conversation if conversation else []
    except Exception as e:
        return {"error": str(e)}


@app.delete("/chat/history/{source}")
async def clear_conversation_history(source: str):
    """Clear the conversation history for a specific source."""
    try:
        clean_source_name = clean_source(source)
        sanitized_source = sanitize_filename(clean_source_name)
        file_path = f"{CONVERSATION_HISTORY_PATH}/{sanitized_source}.json"

        # Check if the file exists and clear its contents
        if os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("[]")  # Write an empty JSON array to clear the file
        return {"message": "Conversation history cleared."}
    except Exception as e:
        return {"error": str(e)}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Endpoint to upload a new file."""
    try:
        file_location = f"data/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Call the processing function to add the file to Chroma
        process_file_and_add_to_chroma(file_location)

        return {"message": "File uploaded and processed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/delete/{source:path}")
async def delete_document(source: str):
    """Endpoint to delete a document from ChromaDB by source."""
    try:
        # Get all documents
        all_docs = db.get()
        ids_to_delete = []

        # Find the document IDs to delete
        for i, metadata in enumerate(all_docs.get("metadatas", [])):
            if metadata.get("source") == source:
                ids_to_delete.append(all_docs.get("ids", [])[i])

        # Delete the documents
        if ids_to_delete:
            db.delete(ids=ids_to_delete)

            # Also delete conversation history for this source
            sanitized_source = sanitize_filename(source)
            history_file = f"{CONVERSATION_HISTORY_PATH}/{sanitized_source}.json"
            if os.path.exists(history_file):
                os.remove(history_file)

            # Delete the local file in the data directory
            local_file_path = f"{source}"
            if os.path.exists(local_file_path):
                os.remove(local_file_path)

            # Remove references from processed_sources.json
            json_path = PROCESSED_SOURCES_FILE
            if os.path.exists(json_path):
                try:
                    # Leer el archivo JSON
                    with open(json_path, "r") as file:
                        data = json.load(file)
                    
                    # Filtrar las entradas para eliminar las que coinciden con el source
                    filtered_documents = [
                        doc for doc in data.get("documents", [])
                        if doc.get("source") != source
                    ]
                    
                    # Actualizar el archivo JSON
                    data["documents"] = filtered_documents
                    
                    # Escribir de vuelta al archivo
                    with open(json_path, "w") as file:
                        json.dump(data, file, indent=2)
                        
                    print(f"Referencias a {source} eliminadas de {json_path}")
                except Exception as e:
                    print(f"Error al actualizar {json_path}: {str(e)}")

            # Para compatibilidad, también actualizar el archivo de texto antiguo si existe
            processed_sources_path = "processed_sources.txt"
            if os.path.exists(processed_sources_path):
                with open(processed_sources_path, "r") as file:
                    lines = file.readlines()
                with open(processed_sources_path, "w") as file:
                    for line in lines:
                        if line.strip() != f"{source}":
                            file.write(line)

            return {
                "message": f"Successfully deleted {len(ids_to_delete)} documents from {source}"
            }
        else:
            return {"message": f"No documents found for source: {source}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
