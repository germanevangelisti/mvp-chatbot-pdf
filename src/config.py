import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LMSTUDIO_BASE_URL = os.getenv("LMSTUDIO_BASE_URL")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH")
