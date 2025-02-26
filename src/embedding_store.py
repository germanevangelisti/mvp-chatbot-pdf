from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from .config import OPENAI_API_KEY, CHROMA_DB_PATH

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small", openai_api_key=OPENAI_API_KEY
)


def store_embeddings(docs):
    """Crea y almacena embeddings en ChromaDB."""
    db = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embedding_model)
    db.add_documents(docs)

    return db
