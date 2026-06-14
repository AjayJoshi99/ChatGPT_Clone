# AI Chatbot with Long-Term Memory and RAG

An AI-powered conversational assistant built using FastAPI, LangChain, Groq LLM, SQLite, and Streamlit.

The application supports:

* Multi-conversation chat
* Long-term memory extraction and retrieval
* Conversation summarization
* Retrieval-Augmented Generation (RAG) using PDF documents
* Vector similarity search
* JWT authentication
* Background document processing
* Streamlit frontend

---

## Features

### Authentication

* User registration
* User login
* JWT access tokens
* Refresh token stored in HTTP-only cookies

### Conversation Management

* Create conversations
* List conversations
* Delete conversations
* Retrieve conversation history

### AI Chat

* Context-aware responses
* Multi-turn conversations
* Automatic conversation summarization
* Long-term memory extraction

### Long-Term Memory

The assistant extracts important user facts and stores them for future retrieval.

Examples:

* User preferences
* Personal goals
* Frequently discussed topics
* Persistent user information

Memory is stored in:

* SQLite database (source of truth)
* Vector store (semantic retrieval)

### RAG (Retrieval-Augmented Generation)

Users can upload PDF documents.

The system:

1. Extracts text from PDFs
2. Splits text into chunks
3. Generates embeddings
4. Stores embeddings in vector storage
5. Retrieves relevant chunks during conversations

This allows the assistant to answer questions about uploaded documents.

### Conversation Summarization

Older messages are automatically summarized to reduce context size while preserving important information.

Benefits:

* Reduced token usage
* Faster responses
* Long conversation support

---

## Tech Stack

### Backend

* FastAPI
* SQLAlchemy
* SQLite
* LangChain
* Groq

### AI Components

* LLM Integration
* Embeddings
* Vector Search
* Long-Term Memory
* Summarization
* RAG

### Frontend

* Streamlit

---

## Project Structure

```text
chatbot/
│
├── routers/
│   ├── auth_router.py
│   └── chat_router.py
│
├── services/
│   ├── chat_services.py
│   ├── conversation_service.py
│   ├── summary_service.py
│   ├── long_term_memory_service.py
│   ├── document_service.py
│   ├── context_builder.py
│   ├── embedding_services.py
│   ├── vector_store_service.py
│   └── groq_services.py
│
├── repositories/
│   ├── conversation_repository.py
│   ├── message_repository.py
│   ├── summary_repository.py
│   ├── long_term_memory_repo.py
│   └── document_repository.py
│
├── database/
├── uploads/
├── frontend/
└── main.py
```

---

## Request Flow

### Chat Request

1. User sends a message
2. Message is stored in database
3. ContextBuilder prepares context using:

   * Recent messages
   * Conversation summary
   * Long-term memory
   * Relevant document chunks
4. LLM generates response
5. Assistant response is stored
6. Summary generation may run
7. Long-term memory extraction may run
8. Response is returned to user

---

## Memory System

The memory layer consists of:

### Database Storage

Stores:

* Original memory text
* Metadata
* Ownership information

Acts as the source of truth.

### Vector Storage

Stores:

* Embeddings
* Semantic representations

Used for similarity search.

Why both?

Database provides durability and management.

Vector store provides semantic retrieval.

---


## Learning Outcomes

This project demonstrates:

* FastAPI architecture
* Repository pattern
* Service layer pattern
* Authentication and authorization
* RAG implementation
* Long-term memory systems
* Vector databases
* Embedding pipelines
* Background task processing
* LLM application development

---

## Author

Ajay Joshi

Built as part of AI Engineering and Backend Development learning journey.
