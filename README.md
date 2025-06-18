# Redis Customized RAG (WIP)

This is a Python project designed to analyze historical documents using a LangGraph-based pipeline. It integrates Redis for structured storage and supports querying of processed document data, including transcription, translation, and keyword extraction.

> A .env file with GOOGLE_API_KEY and REDIS_URL (see .env.example) have to be configured in the source folder.

## Features

- 📄 **Document Processing Pipeline**: Process images or documents using LangGraph to extract and store evaluations.
- 🧠 **LLM-Powered Querying**: Natural language queries over Redis-stored evaluations using an intelligent query agent, which include custom graphs on the searched subject by ending the query with "-g".
- 💾 **Redis Integration**: Efficient storage and retrieval of structured data (e.g., `book_id`, `image_id`).
- ⚙️ **Modular Architecture**: Separate modules for graph definition, Redis store logic, and query handling.

## Project Structure

```
/
│
├── .env                 # Environment variables (API keys, Redis config, etc.)
├── .gitignore           # Git ignore rules
├── LICENSE              # License file
├── __init__.py          # Package init
├── graph.py             # LangGraph pipeline definition
├── langgraph.json       # LangGraph configuration file
├── query_agent.py       # LLM-powered query agent
└── redis_store.py       # Redis storage check
```
