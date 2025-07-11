# Redis Customized RAG

This is a Python project designed to analyze historical documents using a LangGraph-based pipeline. It integrates Redis for structured storage and supports querying of processed document data, including transcription, translation, and keyword extraction.

> A .env file with GOOGLE_API_KEY and REDIS_URL (see .env.example) have to be configured in the source folder (LangChain key optional for graph tracking).

## Features

- **Document Processing Pipeline**: Process images or documents using LangGraph to extract and store evaluations.
- **LLM-Powered Querying**: Natural language queries over Redis-stored evaluations using an intelligent query agent, which include a relationship graph about the queried subject by ending the query with "-g".
- **Redis Integration**: Efficient storage and retrieval of structured data (e.g., `book_id`, `image_id`).
- **Modular Architecture**: Separate modules for graph definition, Redis store logic, and query handling.

## Installation

```bash
docker run -d --name redis-rag -p 6379:6379 redis:latest
uv venv
source venv/bin/activate
uv pip install -r requirements.txt
```

Linux (Debian/Ubuntu):

```bash
sudo apt install poppler-utils
```

MacOS:

```bash
brew install poppler
```

## Execution

### Data Processing

```bash
python graph.py
```

This will process the documents and store the evaluations in the Redis server.

### Storage and Querying

```bash
python query_agent.py
```

This will connect to the Redis server and allow you to query the processed documents through natural language or display all the available documents and pages, including all their stored metadata.

### Redis server management

```bash
Stop: docker stop redis-rag
Start: docker start redis-rag
Logs: docker logs -f redis-rag
```
