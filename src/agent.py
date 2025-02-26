from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage
from retrieval import retrieve_relevant_docs
from config import OPENAI_API_KEY

# Initialize the language model
llm = ChatOpenAI(api_key=OPENAI_API_KEY)

# Dictionary to store memory instances for each source
source_memories = {}

# Define a prompt template
prompt_template = PromptTemplate(
    input_variables=["query", "context", "chat_history"],
    template="""
    Instrucción: Según la consulta del usuario, responde de la manera más precisa y estructurada posible.
    
    Contexto relevante obtenido de los documentos:
    {context}

    Historial de conversación:
    {chat_history}

    Basado en la consulta: "{query}", realiza la tarea correspondiente:
    
    - Si la consulta solicita un **resumen**, genera un resumen conciso de la información clave.
    - Si la consulta pide **extracción de información**, extrae nombres, fechas o eventos importantes.
    - Si la consulta menciona **comparación**, compara los documentos identificando diferencias y similitudes.
    - Si la consulta es una **pregunta sobre el contenido**, proporciona una respuesta clara y detallada.
    - Si la consulta es ambigua, intenta inferir la mejor respuesta posible basándote en el contenido disponible.
    
    Respuesta:
    """,
)

def format_context(docs):
    """
    Extrae y formatea el contenido relevante de los documentos recuperados.
    """
    formatted_context = "\n\n".join([f"(Página {doc.metadata['page_label']}) {doc.page_content}" for doc in docs])
    return formatted_context

def format_chat_history(messages):
    """Format chat history for inclusion in the prompt."""
    formatted_history = ""
    for message in messages:
        if isinstance(message, HumanMessage):
            formatted_history += f"Human: {message.content}\n"
        elif isinstance(message, AIMessage):
            formatted_history += f"AI: {message.content}\n"
    return formatted_history

def get_or_create_memory(source):
    """Get existing memory for source or create a new one if it doesn't exist."""
    if source not in source_memories:
        # Initialize new memory for this source
        message_history = ChatMessageHistory()
        source_memories[source] = ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=message_history,
            return_messages=True
        )
    return source_memories[source]

def generate_response(query, source):
    # Get memory for this specific source
    memory = get_or_create_memory(source)
    
    # Retrieve relevant documents for the selected source
    print(f"Retrieving documents for source: {source}")
    context = retrieve_relevant_docs(query, source=source)
    formatted_context = format_context(context)
    
    # Retrieve conversation history from memory
    chat_history = memory.load_memory_variables({}).get("chat_history", [])
    formatted_history = format_chat_history(chat_history)
    
    # Generate a response using the prompt template
    prompt = prompt_template.format(
        query=query, 
        context=formatted_context, 
        chat_history=formatted_history
    )
    
    # Pass the prompt directly as a string
    response = llm.invoke(prompt)
    
    # Update memory with the new interaction
    memory.chat_memory.add_user_message(query)
    memory.chat_memory.add_ai_message(response.content)
    
    return response

# Function to invoke the agent
def agent(query, source):
    return generate_response(query, source)
