import json
from ..utils.errors import AppError, error_to_http_payload
from ..rag.query import query_rag
from ..voice.voice import process_audio, generate_audio

def make_chat_handler(vector_store, cfg, logger):
    async def handler(req, res):
        try:
            question = (req.body or {}).get("question")
            if not question or not isinstance(question, str) or not question.strip():
                raise AppError("QUESTION_REQUIRED", "Question is required.", 400)
            answer = await query_rag(vector_store, question, cfg, logger)
            status, headers, body = res.json(200, {"success": True, "answer": answer})
            return status, headers, [body]
        except Exception as e:
            payload = error_to_http_payload(e)
            status, headers, body = payload["status"], payload["headers"], json.dumps(payload["body"]).encode("utf-8")
            return status, headers, [body]
    return handler

def make_voice_handler(vector_store, cfg, logger):
    async def handler(req, res):
        try:
            audio_bytes = req.audio_bytes
            if not audio_bytes or not isinstance(audio_bytes, (bytes, bytearray)):
                raise AppError("AUDIO_REQUIRED", "audio bytes are required in request.", 400)

            logger("[DEBUG] Received audio, length=%s bytes" % len(audio_bytes))

            # Step 1: STT
            transcription = await process_audio(audio_bytes, cfg)
            logger(f"[DEBUG] Transcription result: {transcription}")

            # Step 2: RAG
            answer = await query_rag(vector_store, transcription, cfg, logger)
            logger(f"[DEBUG] RAG answer: {answer}")

            # Step 3: TTS
            audio_b64 = await generate_audio(answer, cfg)
            logger(f"[DEBUG] Generated audio length={len(audio_b64)} base64 chars")

            status, headers, body = res.json(200, {
                "success": True,
                "transcription": transcription,
                "answer": answer,
                "audio": audio_b64,
            })
            return status, headers, [body]

        except Exception as e:
            import traceback
            traceback.print_exc()
            logger(f"[ERROR] Exception in voice_handler: {e}")
            payload = error_to_http_payload(e)
            status, headers, body = (
                payload["status"],
                payload["headers"],
                json.dumps(payload["body"]).encode("utf-8"),
            )
            return status, headers, [body]
    return handler

