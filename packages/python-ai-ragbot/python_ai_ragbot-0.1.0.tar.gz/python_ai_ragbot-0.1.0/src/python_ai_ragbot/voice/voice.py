import base64
from openai import OpenAI
from ..utils.errors import AppError

async def process_audio(audio_bytes: bytes, cfg) -> str:
    try:
        client = OpenAI(api_key=cfg["openai"]["apiKey"])
        # OpenAI transcriptions expects file-like; use bytes with a name hint
        transcription = client.audio.transcriptions.create(
            file=("audio.webm", audio_bytes, "audio/webm"),
            model=cfg["openai"]["whisper"]["model"],
            language=cfg["openai"]["whisper"].get("language", "en"),
            response_format="verbose_json",
        )
        # transcription could be dict-like depending on SDK version
        text = getattr(transcription, "text", None) or transcription.get("text", "")
        return (text or "").strip()
    except Exception as e:
        raise AppError("OPENAI_TRANSCRIPTION_FAILED", f"Audio transcription failed: {e}", 500)

async def generate_audio(text: str, cfg) -> str:
    try:
        client = OpenAI(api_key=cfg["openai"]["apiKey"])
        resp = client.audio.speech.create(
            model=cfg["openai"]["tts"]["model"],
            voice=cfg["openai"]["tts"]["voice"],
            input=text,
            response_format=cfg["openai"]["tts"].get("response_format", "mp3"),
        )
        # SDK returns binary-like payload
        data = resp.read() if hasattr(resp, "read") else resp  # fallback
        if isinstance(data, (bytes, bytearray)):
            return base64.b64encode(data).decode("utf-8")
        # Some SDK variants return .content or .array_buffer()
        try:
            ab = resp.array_buffer()  # may raise
            return base64.b64encode(bytes(ab)).decode("utf-8")
        except Exception:
            pass
        raise RuntimeError("Unexpected TTS response type")
    except Exception as e:
        raise AppError("OPENAI_TTS_FAILED", f"Text-to-speech failed: {e}", 500)
