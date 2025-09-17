from .config.defaults import DEFAULTS
from .config.validate import normalize_config
from .rag.builder import build_vector_store
from .http.handlers import make_chat_handler, make_voice_handler
import asyncio


async def init_rag_voice_bot_async(user_config=None):
    user_config = user_config or {}
    cfg = normalize_config(user_config, DEFAULTS)
    vector_store = await build_vector_store(cfg, cfg["logger"])
    chat_handler = make_chat_handler(vector_store, cfg, cfg["logger"])
    voice_handler = make_voice_handler(vector_store, cfg, cfg["logger"])
    return {
        "vector_store": vector_store,
        "cfg": cfg,
        "chat_handler": chat_handler,
        "voice_handler": voice_handler,
    }


def init_rag_voice_bot(config=None):
    return asyncio.run(init_rag_voice_bot_async(config))