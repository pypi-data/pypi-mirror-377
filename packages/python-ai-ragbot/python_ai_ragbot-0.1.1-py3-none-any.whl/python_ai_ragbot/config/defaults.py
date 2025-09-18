import logging

DEFAULTS = {
    "sources": {
        "files": [],
        "urls": [],
    },
    "rag": {
        "maxPagesPerSite": 30,
        "textSplit": {
            "chunkSize": 1000,
            "chunkOverlap": 200,
        },
        "topK": 3,
    },
    "openai": {
        "apiKey": None,
        "embeddings": {"model": "text-embedding-3-small"},
        "chat": {"model": "gpt-4o-mini", "temperature": 0.3, "maxTokens": 100,
                 "promptTemplate": (
                "You are a domain-specific expert. Answer under 50 words based only on the context.\n\n"
                "Context:\n{context}\n\n"
                "Question: {question}\n\n"
                "Answer:"
            ),},
        "stt": {"model": "whisper-1", "language": "en"},
        "tts": {"model": "tts-1", "voice": "alloy", "response_format": "mp3"},
    },
    "logger": print,
}
