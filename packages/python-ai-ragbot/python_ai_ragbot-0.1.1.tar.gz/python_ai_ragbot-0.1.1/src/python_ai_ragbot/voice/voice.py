import base64
import io
from openai import OpenAI
from ..utils.errors import AppError

async def process_audio(audio_bytes, cfg):
    client = OpenAI(api_key=cfg["openai"]["apiKey"])
    try:
        # Wrap bytes with a filename to hint OpenAI about the format
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "input.webm"

        transcription = client.audio.transcriptions.create(
            model=cfg["openai"].get("stt", {}).get("model", "whisper-1"),
            file=audio_file
        )
        return transcription.text
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
