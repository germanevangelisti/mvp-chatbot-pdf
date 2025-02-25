from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from retrieval import retrieve_relevant_docs
from config import OPENAI_API_KEY

# Initialize the language model
llm = ChatOpenAI(api_key=OPENAI_API_KEY)

# Define a prompt template
prompt_template = PromptTemplate(
    input_variables=["query", "context"],
    template="""
    Instrucción: Según la consulta del usuario, responde de la manera más precisa y estructurada posible.
    
    Contexto relevante obtenido de los documentos:
    {context}

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

def generate_response(query, source):
    # Retrieve relevant documents for the selected source
    print(f"Retrieving documents for source: {source}")
    context = retrieve_relevant_docs(query, source=source)
    formatted_context = format_context(context)
    # Generate a response using the prompt template
    prompt = prompt_template.format(query=query, context=formatted_context)
    # Pass the prompt directly as a string
    return llm.invoke(prompt)

# Function to invoke the agent
def agent(query, source):
    return generate_response(query, source)
