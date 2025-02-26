from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from config import OPENAI_API_KEY, CHROMA_DB_PATH

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small", openai_api_key=OPENAI_API_KEY
)
db = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embedding_model)

retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 5})

def retrieve_relevant_docs(query, source=None):
    """Recupera documentos relevantes usando LangChain Retriever."""
    return retriever.invoke(query, filter={"source": source})

# def retrieve_relevant_docs(query, source=None):
#     """Retrieve relevant documents from the database, filtered by source if provided."""
#     print(f"Retrieving documents for source: {source}")
    
#     # Retrieve all documents
#     documents = db.get()
#     all_docs = documents.get("documents", [])
#     metadatas = documents.get("metadatas", [])
    
#     if source:
#         # Filter documents that match the specified source
#         filtered_docs = [
#             {"content": doc, "metadata": meta}
#             for doc, meta in zip(all_docs, metadatas)
#             if meta.get("source") == source
#         ]
#         print(f"Found {len(filtered_docs)} documents for source: {source}")
#     else:
#         filtered_docs = [{"content": doc, "metadata": meta} for doc, meta in zip(all_docs, metadatas)]
#         print(f"Retrieving all documents, total: {len(filtered_docs)}")

#     # Perform similarity search on the filtered documents
#     return db.similarity_search(query, k=3, filter={"source": source})
