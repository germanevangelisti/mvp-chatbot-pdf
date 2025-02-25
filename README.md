# MVP RAG Agent

This is a system based on LangGraph and ChromaDB for Retrieval-Augmented Generation (RAG).

## Description

The MVP RAG Agent is an application designed to enhance text generation by retrieving relevant documents. It uses ChromaDB to store and manage documents, and LangGraph to process queries and generate responses.

## Features

- **Document Upload**: Allows users to upload documents that are processed and stored in ChromaDB.
- **Document Query**: Users can query the stored documents to obtain generated responses.
- **Conversation History**: Maintains a history of user interactions with the agent.
- **Web Interface**: Provides a web interface to interact with the system.

## Requirements

- Python 3.8 or higher
- FastAPI
- ChromaDB
- LangGraph

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your_username/mvp-rag-agent.git
   cd mvp-rag-agent
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the FastAPI server:
   ```bash
   uvicorn src.web_server:app --reload
   ```

2. Open your browser and visit `http://localhost:8000` to access the web interface.

3. Use the interface to upload documents, make queries, and view conversation history.

## Project Structure

- `src/`: Contains the project's source code.
  - `web_server.py`: Defines the API endpoints and handles requests.
  - `file_processing.py`: Processes files and adds them to ChromaDB.
  - `retrieval.py`: Handles document retrieval from ChromaDB.
  - `templates/`: Contains HTML templates for the web interface.
  - `conversation_histories/`: Stores conversation histories in JSON format.

## Contributions

Contributions are welcome. Please open an issue or a pull request to discuss significant changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact

For more information, contact [your_email@example.com](mailto:your_email@example.com).