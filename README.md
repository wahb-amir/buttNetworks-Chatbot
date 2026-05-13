# Website Chatbot RAG System

A website chatbot built with **FastAPI**, **Supabase pgvector**, **Groq**, and **local embeddings**. The system stores conversation history, retrieves relevant knowledge chunks with vector search, and generates grounded replies with an LLM.

## Features

- REST API chatbot endpoint for website integration
- FastAPI backend
- Internal token authentication for server-to-server calls
- Rate limiting for abuse protection
- Groq LLM response generation
- Supabase-backed chat memory
- pgvector retrieval for knowledge chunks
- Local embeddings for chunking and query search
- Retrieval test scripts for debugging and validation
- Docker-ready project structure

## Project Structure

```text
app
├── api
│   └── v1
│       ├── routes.py
│       └── chat.py
├── core
│   └── config.py
├── db
│   ├── schema.sql
│   └── supabase_client.py
├── main.py
├── repositories
│   ├── chat_repository.py
│   └── knowledge_repository.py
└── services
    ├── embeddings
    │   └── local_embeddings.py
    ├── llm
    │   └── groq_client.py
    └── rag
        ├── pipeline.py
        └── retriever.py

scripts
├── deep-research-report.md
├── ingest_docs.py
├── retival_test.py
└── test.py
```

## How It Works

1. The website sends a JSON message to the chatbot REST API.
2. The request is authenticated with an internal token.
3. The user message is saved in chat memory.
4. The user query is embedded with the local embedding model.
5. Supabase pgvector retrieves the most relevant knowledge chunks.
6. The retrieved chunks and recent chat history are passed to Groq.
7. The model generates a grounded reply.
8. The reply is returned as JSON to the frontend.

## Main Components

### `app/api/v1/chat.py`

Handles incoming website chatbot requests, stores user messages, loads recent conversation history, runs the RAG pipeline, and returns the response as JSON.

### `app/repositories/chat_repository.py`

Reads and writes conversation messages and conversation records.

### `app/repositories/knowledge_repository.py`

Inserts knowledge chunks and performs vector search operations.

### `app/services/rag/retriever.py`

Embeds the query and fetches the most relevant chunks from Supabase.

### `app/services/rag/pipeline.py`

Builds the prompt context and coordinates retrieval + generation.

### `app/services/llm/groq_client.py`

Wraps the Groq API call used for answer generation.

### `app/services/embeddings/local_embeddings.py`

Creates local embeddings using the configured embedding model.

### `scripts/ingest_docs.py`

Chunks and ingests markdown content into Supabase.

### `scripts/retival_test.py`

Tests retrieval quality without sending a browser request.

### `scripts/test.py`

Simulates a chatbot API request locally.

## Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root and add:

```env
APP_ENV=dev

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile

INTERNAL_API_TOKEN=your_long_random_internal_secret

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIM=384

RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_MAX_REQUESTS=30
```

## Database Setup

Run the schema file in Supabase SQL editor:

```sql
-- app/db/schema.sql
```

The database should include tables for:

- `conversations`
- `chat_messages`
- `knowledge_chunks`

## Ingest Knowledge Docs

To ingest the markdown knowledge file into Supabase:

```bash
python3 scripts/ingest_docs.py
```

## Test Retrieval

To test the retrieval layer without the frontend:

```bash
python3 -m scripts.retival_test
```

## Simulate a Chatbot Request Locally

```bash
python3 scripts/test.py
```

## Run the App

```bash
uvicorn app.main:app --reload
```

## API Endpoint

Use the chatbot endpoint from your frontend or backend:

```text
POST /api/v1/chat
```

Example JSON body:

```json
{
  "session_id": "web-session-123",
  "message": "Hello, can you help me?"
}
```

Example headers:

```http
Authorization: Bearer YOUR_INTERNAL_API_TOKEN
Content-Type: application/json
```

## Current Status

The project currently supports:

- Website chatbot REST API handling
- Chat persistence in Supabase
- Semantic retrieval with pgvector
- Groq-powered responses
- Internal token protection
- Rate limiting
- Local testing scripts

## Notes

- The bot uses short-term chat memory from recent messages.
- Retrieval quality depends on chunking and embedding quality.
- The current architecture is built to be extended with long-term memory, reranking, and hybrid search.

## Next Improvements

- Add long-term memory summaries
- Add reranking for better retrieval quality
- Add hybrid search (vector + keyword)
- Add Redis-backed distributed rate limiting
- Add retries and queueing for request reliability
- Add observability and query logging
- Add frontend chat UI integration examples

## License

No license has been added yet.
