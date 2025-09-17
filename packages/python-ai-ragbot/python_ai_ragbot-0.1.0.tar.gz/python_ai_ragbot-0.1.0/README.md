# python-ai-ragbot

`python-ai-ragbot` is a modular and framework-agnostic Python package for building intelligent chatbots and voicebots with **Retrieval-Augmented Generation (RAG)**, powered by **OpenAI** and **LangChain**.

It provides a simple interface to attach ready-made request handlers into popular frameworks (FastAPI, Flask, Django, Starlette, WSGI, ASGI). You can quickly add both text chat (`/chat`) and voice (`/voice`) endpoints into your app.

---

## Features

- Supports knowledge sources:
  - Local files (`.pdf`, `.docx`, `.txt`, `.md`)
  - Website scraping (URLs, sitemaps)
- `/chat` endpoint (text query → answer)
- `/voice` endpoint (speech-to-text via Whisper, TTS for responses)
- Fully configurable models, embeddings, voices, chunking, logging
- In-memory FAISS vector store via LangChain
- Adapters for:
  - FastAPI
  - Starlette
  - Flask
  - Django
  - Raw WSGI
  - Raw ASGI
- Sync (`init_rag_voice_bot`) and Async (`init_rag_voice_bot_async`) APIs

---

## Requirements

- Python 3.9+
- An OpenAI API key (`OPENAI_API_KEY` in `.env`)

---

## Installation

```bash
pip install python-ai-ragbot
```

For local development:

```bash
git clone https://github.com/your-org/python-ai-ragbot.git
cd python-ai-ragbot
pip install -e .
```

---

## Quick Start (FastAPI)

```python
# examples/server.py
from fastapi import FastAPI
from python_ai_ragbot import init_rag_voice_bot_async
from python_ai_ragbot.http.adapters import use_in_fastapi
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    bot = await init_rag_voice_bot_async({
        "sources": {"files": ["examples/knowledge.txt"]},
        "openai": {
            "apiKey": os.getenv("OPENAI_API_KEY"),
            "chat": {"model": "gpt-4o"},
            "whisper": {"model": "whisper-1"},
            "tts": {"model": "tts-1-hd", "voice": "nova"},
        }
    })
    use_in_fastapi(app, bot["chat_handler"], bot["voice_handler"], prefix="/api/bot")
```

Run:

```bash
uvicorn examples.server:app --reload --port 3001
```

Endpoints:

- `POST /api/bot/chat`
- `POST /api/bot/voice`

---

## Usage with Other Frameworks

### Starlette

```python
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from python_ai_ragbot import init_rag_voice_bot_async
from python_ai_ragbot.http.adapters import use_in_starlette
import os, asyncio

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.on_event("startup")
async def startup():
    bot = await init_rag_voice_bot_async({
        "sources": {"files": ["examples/knowledge.txt"]},
        "openai": {"apiKey": os.getenv("OPENAI_API_KEY")},
    })
    use_in_starlette(app, bot["chat_handler"], bot["voice_handler"], prefix="/api/bot")
```

---

### Flask

```python
from flask import Flask
from python_ai_ragbot import init_rag_voice_bot
from python_ai_ragbot.http.adapters import use_in_flask
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

bot = init_rag_voice_bot({
    "sources": {"files": ["examples/knowledge.txt"]},
    "openai": {"apiKey": os.getenv("OPENAI_API_KEY")},
})
use_in_flask(app, bot["chat_handler"], bot["voice_handler"], prefix="/api/bot")

if __name__ == "__main__":
    app.run(port=3001)
```

---

### Django

```python
# myproject/urls.py
from django.urls import path
from python_ai_ragbot import init_rag_voice_bot
from python_ai_ragbot.http.adapters import use_in_django
import os
from dotenv import load_dotenv

load_dotenv()
urlpatterns = []

bot = init_rag_voice_bot({
    "sources": {"files": ["examples/knowledge.txt"]},
    "openai": {"apiKey": os.getenv("OPENAI_API_KEY")},
})
use_in_django(urlpatterns, bot["chat_handler"], bot["voice_handler"], prefix="/api/bot")
```

---

### Raw WSGI

```python
from wsgiref.simple_server import make_server
from python_ai_ragbot import init_rag_voice_bot
from python_ai_ragbot.http.adapters import use_in_wsgi
import os

bot = init_rag_voice_bot({
    "sources": {"files": ["examples/knowledge.txt"]},
    "openai": {"apiKey": os.getenv("OPENAI_API_KEY")},
})

app = {}
use_in_wsgi(app, bot["chat_handler"], bot["voice_handler"], prefix="/api/bot")

with make_server("", 3001, app["wsgi"]) as httpd:
    print("Serving on port 3001...")
    httpd.serve_forever()
```

---

### Raw ASGI

```python
import uvicorn
from python_ai_ragbot import init_rag_voice_bot_async
from python_ai_ragbot.http.adapters import use_in_starlette
from starlette.applications import Starlette
import os

app = Starlette()

@app.on_event("startup")
async def startup():
    bot = await init_rag_voice_bot_async({
        "sources": {"files": ["examples/knowledge.txt"]},
        "openai": {"apiKey": os.getenv("OPENAI_API_KEY")},
    })
    use_in_starlette(app, bot["chat_handler"], bot["voice_handler"], prefix="/api/bot")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3001)
```

---

## Configuration

```python
{
  "sources": {
    "files": ["knowledge.txt", "knowledge.pdf"],
    "urls": ["https://docs.example.com"]
  },
  "rag": {
    "textSplit": {"chunkSize": 1000, "chunkOverlap": 200},
    "topK": 3
  },
  "openai": {
    "apiKey": "...",
    "embeddings": {"model": "text-embedding-3-small"},
    "chat": {"model": "gpt-4o", "temperature": 0.3},
    "whisper": {"model": "whisper-1"},
    "tts": {"model": "tts-1-hd", "voice": "nova"}
  },
  "logger": "console"
}
```

---

## Endpoints

### `/chat`
- **POST** JSON
```json
{"question": "What is in the knowledge base?"}
```

### `/voice`
- **POST** raw audio (`audio/webm`, `audio/wav`, etc.)

---

## Example Project Structure

```
my-app/
├── examples/
│   ├── server.py
│   ├── knowledge.txt
├── src/
│   └── python_ai_ragbot/
├── .env
└── pyproject.toml
```

---

## Notes

- Use **`init_rag_voice_bot_async`** in **ASGI frameworks** (FastAPI, Starlette).  
- Use **`init_rag_voice_bot`** in **WSGI frameworks** (Flask, Django, raw WSGI).  
- Vector store is in-memory only; data is reloaded on each startup.  

---
