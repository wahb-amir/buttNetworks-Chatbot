# Website Chatbot RAG System

A production-oriented Retrieval-Augmented Generation (RAG) chatbot built with **FastAPI**, **Supabase pgvector**, **Groq**, and **local embeddings**.

The system stores conversation history, retrieves relevant knowledge chunks using semantic search, and generates grounded responses using a large language model. It is designed for website integration, internal support assistants, documentation chatbots, and business knowledge bases.

---

# Features

- REST API chatbot endpoint for website integration
- FastAPI backend
- Internal token authentication for server-to-server communication
- Rate limiting for abuse protection
- Groq-powered response generation
- Supabase-backed conversation memory
- pgvector semantic retrieval
- Local embedding generation
- Markdown-aware document ingestion
- Heading-aware section tracking
- Context-preserving chunk overlap
- Duplicate chunk detection and filtering
- Retrieval debugging utilities
- Modular RAG architecture
- Docker-friendly project structure

---

# Architecture Overview

```text
User
 │
 ▼
Website Frontend
 │
 ▼
FastAPI Chat Endpoint
 │
 ├── Authentication
 ├── Rate Limiting
 └── Session Handling
 │
 ▼
RAG Pipeline
 │
 ├── Query Embedding
 ├── Vector Retrieval (pgvector)
 ├── Context Construction
 └── Prompt Assembly
 │
 ▼
Groq LLM
 │
 ▼
Grounded Response
 │
 ▼
Frontend
```

---

# Project Structure

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

---

# How It Works

1. The frontend sends a message to the chatbot API.
2. The request is authenticated using an internal API token.
3. The user's message is stored in chat history.
4. The query is normalized and embedded using a local embedding model.
5. Supabase pgvector performs semantic similarity search.
6. The most relevant knowledge chunks are returned.
7. Recent conversation history is loaded.
8. Context and history are combined into a prompt.
9. Groq generates a grounded response.
10. The response is returned to the frontend.

---

# Main Components

## `app/api/v1/chat.py`

Responsible for:

- Receiving chatbot requests
- Validating authentication
- Loading conversation history
- Running the RAG pipeline
- Returning responses as JSON

---

## `app/repositories/chat_repository.py`

Responsible for:

- Creating conversations
- Storing chat messages
- Loading previous messages
- Managing chat persistence

---

## `app/repositories/knowledge_repository.py`

Responsible for:

- Knowledge chunk storage
- Vector search operations
- Retrieval-related database access

---

## `app/services/rag/retriever.py`

Responsible for:

- Query normalization
- Query embedding generation
- Supabase vector search
- Similarity validation
- Retrieval debugging utilities

Returned chunks contain:

- Chunk ID
- Source
- Content
- Metadata
- Similarity score

---

## `app/services/rag/pipeline.py`

Responsible for:

- Retrieval orchestration
- Context formatting
- Prompt construction
- Response generation flow

---

## `app/services/llm/groq_client.py`

Responsible for:

- Groq API communication
- Model invocation
- Response handling

---

## `app/services/embeddings/local_embeddings.py`

Responsible for:

- Local embedding generation
- Embedding model abstraction

---

# Retrieval Design

The retrieval layer is based on semantic vector search.

## Retrieval Flow

```text
User Query
     │
     ▼
Query Normalization
     │
     ▼
Embedding Generation
     │
     ▼
Supabase pgvector Search
     │
     ▼
Top Matching Chunks
     │
     ▼
Context Builder
     │
     ▼
LLM
```

## Retrieval Features

- Query normalization
- Similarity threshold filtering
- Top-K retrieval
- Metadata-aware results
- Source tracking
- Retrieval debugging support

---

# Ingestion Pipeline

The ingestion pipeline converts Markdown documentation into searchable vector chunks.

## Processing Steps

1. Normalize text
2. Extract Markdown headings
3. Preserve section hierarchy
4. Build logical content blocks
5. Split oversized blocks
6. Create overlapping chunks
7. Generate embeddings
8. Store chunks in Supabase

---

## Markdown-Aware Chunking

Instead of blindly splitting text, the ingestion system:

- Preserves heading context
- Tracks nested sections
- Keeps related paragraphs together
- Minimizes context fragmentation

Example:

```markdown
# Authentication

## JWT Setup

Explanation...

## OAuth Setup

Explanation...
```

Stored metadata:

```json
{
  "section": "Authentication / JWT Setup"
}
```

---

## Chunk Metadata

Each chunk stores:

```json
{
  "chunk_index": 0,
  "source_file": "docs/auth.md",
  "source_name": "auth.md",
  "section": "Authentication / JWT Setup",
  "char_length": 820,
  "content_hash": "...",
  "embedding_model": "...",
  "embedding_dim": 384
}
```

---

## Duplicate Detection

The ingestion pipeline computes a content hash for every chunk.

Benefits:

- Prevents duplicate storage
- Saves vector space
- Improves retrieval quality
- Reduces ingestion mistakes

---

# Setup

## 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Configure Environment Variables

Create a `.env` file:

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

---

# Database Setup

Run:

```sql
-- app/db/schema.sql
```

Required tables:

- conversations
- chat_messages
- knowledge_chunks

---

# Ingest Knowledge

Default:

```bash
python3 scripts/ingest_docs.py
```

Custom:

```bash
python3 scripts/ingest_docs.py \
  --file docs/product.md \
  --source product-docs \
  --max-chars 1000 \
  --overlap-chars 150
```

---

# Test Retrieval

```bash
python3 -m scripts.retival_test
```

The output includes:

- chunk id
- source
- similarity score
- chunk index
- content preview

---

# Simulate a Chat Request

```bash
python3 scripts/test.py
```

---

# Run the API

```bash
uvicorn app.main:app --reload
```

---

# API Endpoint

## Request

```http
POST /api/v1/chat
```

Headers:

```http
Authorization: Bearer YOUR_INTERNAL_API_TOKEN
Content-Type: application/json
```

Body:

```json
{
  "session_id": "web-session-123",
  "message": "Hello, can you help me?"
}
```

---

## Response

Example:

```json
{
  "response": "Yes, I can help you with that."
}
```

---

# Current Status

Implemented:

- FastAPI chatbot API
- Internal token authentication
- Rate limiting
- Supabase chat memory
- Semantic retrieval
- Groq integration
- Markdown-aware chunking
- Section metadata tracking
- Chunk overlap support
- Duplicate chunk filtering
- Retrieval testing utilities

---

# Future Improvements

## Retrieval

- Hybrid search (vector + keyword)
- Reranking
- Parent-child retrieval
- Multi-query retrieval
- Query rewriting

## Memory

- Long-term memory summaries
- User preference memory
- Session summarization

## Infrastructure

- Redis-backed distributed rate limiting
- Background job processing
- Retry queues
- Monitoring and observability

## Evaluation

- Retrieval evaluation suite
- Grounding checks
- Hallucination detection
- Query analytics

---

# License

No license has been added yet.