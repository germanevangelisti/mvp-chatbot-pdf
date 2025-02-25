from data_ingestion import load_documents
from embedding_store import store_embeddings
import os

def get_processed_sources(directory="data/"):
    """Obtiene un conjunto de fuentes ya procesadas."""
    if os.path.exists("processed_sources.txt"):
        with open("processed_sources.txt", "r") as f:
            return set(line.strip() for line in f)
    return set()

def mark_source_as_processed(source):
    """Marca una fuente como procesada."""
    with open("processed_sources.txt", "a") as f:
        f.write(source + "\n")

def process_file_and_add_to_chroma(file_path):
    processed_sources = get_processed_sources()
    docs = load_documents()
    new_docs = [doc for doc in docs if doc.metadata["source"] not in processed_sources]

    if new_docs:
        store_embeddings(new_docs)
        for doc in new_docs:
            mark_source_as_processed(doc.metadata["source"])
        print("Base de datos vectorial creada y lista para consultas.")
    else:
        print("No hay nuevos documentos para procesar.")
        
# if __name__ == "__main__":
#     processed_sources = get_processed_sources()
#     docs = load_documents()
#     new_docs = [doc for doc in docs if doc.metadata["source"] not in processed_sources]

#     if new_docs:
#         store_embeddings(new_docs)
#         for doc in new_docs:
#             mark_source_as_processed(doc.metadata["source"])
#         print("Base de datos vectorial creada y lista para consultas.")
#     else:
#         print("No hay nuevos documentos para procesar.")