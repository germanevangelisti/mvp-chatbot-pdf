import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader


def load_documents(directory="data/"):
    """Carga documentos desde una carpeta."""
    docs = []
    for file in os.listdir(directory):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(directory, file))
        elif file.endswith(".txt"):
            loader = TextLoader(os.path.join(directory, file))
        else:
            continue
        docs.extend(loader.load())
    return docs
