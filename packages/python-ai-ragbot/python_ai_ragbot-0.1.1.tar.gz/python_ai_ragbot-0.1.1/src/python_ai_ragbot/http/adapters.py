import json
from .types import PortableRequest, ResponseWriter

def _collect_body(environ_or_req):
    """
    Returns (body_dict, audio_bytes, headers, method, path, query_dict)
    Implemented per adapter using the raw framework objects.
    """
    raise NotImplementedError

# ---------- FastAPI ----------
def use_in_fastapi(app, chat_handler, voice_handler, prefix=""):
    from fastapi import Request, FastAPI
    from fastapi.responses import JSONResponse
    from starlette.responses import Response

    base = prefix or ""

    @app.post(f"{base}/chat")
    async def chat_route(request: Request):
        headers = dict(request.headers)
        method = request.method
        path = str(request.url.path)
        query = dict(request.query_params)

        # Prefer existing parser; fallback to raw
        body = {}
        try:
            body = await request.json()
        except Exception:
            try:
                raw = await request.body()
                if raw:
                    body = json.loads(raw.decode("utf-8"))
            except Exception:
                body = {}

        preq = PortableRequest(method, path, headers, query, body, None, request)
        pres = ResponseWriter(Response)
        status, hdrs, chunks = await chat_handler(preq, pres)
        return Response(content=b"".join(chunks), status_code=status, headers=hdrs)

    @app.post(f"{base}/voice")
    async def voice_route(request: Request):
        headers = dict(request.headers)
        method = request.method
        path = str(request.url.path)
        query = dict(request.query_params)

        ctype = headers.get("content-type", "")
        raw = await request.body()
        body = {}
        audio_bytes = None
        if ctype.startswith("audio/"):
            audio_bytes = raw
        else:
            # best-effort JSON
            try:
                body = json.loads(raw.decode("utf-8"))
            except Exception:
                body = {}

        preq = PortableRequest(method, path, headers, query, body, audio_bytes, request)
        pres = ResponseWriter(Response)
        status, hdrs, chunks = await voice_handler(preq, pres)
        return Response(content=b"".join(chunks), status_code=status, headers=hdrs)

# ---------- Flask ----------
def use_in_flask(app, chat_handler, voice_handler, prefix=""):
    from flask import request, Response

    base = prefix or ""

    @app.post(f"{base}/chat")
    def chat_route():
        headers = {k.lower(): v for k, v in request.headers.items()}
        method = request.method
        path = request.path
        query = dict(request.args)
        body = {}
        if request.is_json:
            body = request.get_json(silent=True) or {}
        else:
            try:
                body = json.loads(request.data.decode("utf-8"))
            except Exception:
                body = {}
        preq = PortableRequest(method, path, headers, query, body, None, request)
        pres = ResponseWriter(Response)
        status, hdrs, chunks = app.loop.run_until_complete(chat_handler(preq, pres)) if hasattr(app, "loop") else \
                               __import__("asyncio").get_event_loop().run_until_complete(chat_handler(preq, pres))
        return Response(response=b"".join(chunks), status=status, headers=hdrs)

    @app.post(f"{base}/voice")
    def voice_route():
        headers = {k.lower(): v for k, v in request.headers.items()}
        method = request.method
        path = request.path
        query = dict(request.args)
        ctype = headers.get("content-type", "")
        raw = request.get_data()
        body = {}
        audio_bytes = None
        if ctype.startswith("audio/"):
            audio_bytes = raw
        else:
            try:
                body = json.loads(raw.decode("utf-8"))
            except Exception:
                body = {}
        preq = PortableRequest(method, path, headers, query, body, audio_bytes, request)
        pres = ResponseWriter(Response)
        status, hdrs, chunks = __import__("asyncio").get_event_loop().run_until_complete(voice_handler(preq, pres))
        return Response(response=b"".join(chunks), status=status, headers=hdrs)

# ---------- Starlette (ASGI) ----------
def use_in_starlette(app, chat_handler, voice_handler, prefix=""):
    from starlette.requests import Request
    from starlette.responses import Response

    base = prefix or ""

    @app.route(f"{base}/chat", methods=["POST"])
    async def chat_route(request: Request):
        headers = dict(request.headers)
        method = request.method
        path = request.url.path
        query = dict(request.query_params)
        body = {}
        try:
            body = await request.json()
        except Exception:
            try:
                raw = await request.body()
                body = json.loads(raw.decode("utf-8"))
            except Exception:
                body = {}
        preq = PortableRequest(method, path, headers, query, body, None, request)
        pres = ResponseWriter(Response)
        status, hdrs, chunks = await chat_handler(preq, pres)
        return Response(content=b"".join(chunks), status_code=status, headers=hdrs)

    @app.route(f"{base}/voice", methods=["POST"])
    async def voice_route(request: Request):
        headers = dict(request.headers)
        method = request.method
        path = request.url.path
        query = dict(request.query_params)
        ctype = headers.get("content-type", "")
        raw = await request.body()
        body = {}
        audio_bytes = None
        if ctype.startswith("audio/"):
            audio_bytes = raw
        else:
            try:
                body = json.loads(raw.decode("utf-8"))
            except Exception:
                body = {}
        preq = PortableRequest(method, path, headers, query, body, audio_bytes, request)
        pres = ResponseWriter(Response)
        status, hdrs, chunks = await voice_handler(preq, pres)
        return Response(content=b"".join(chunks), status_code=status, headers=hdrs)

# ---------- Raw WSGI ----------
def use_in_wsgi(app, chat_handler, voice_handler, prefix=""):
    # app is a simple dict holding routes, we create a WSGI app
    # Example:
    #   app = {}
    #   use_in_wsgi(app, chat, voice, "/api/bot")
    #   server = make_server(..., app['wsgi'])
    import urllib.parse

    base = prefix or ""

    async def _handle(environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO", "/")
        query_string = environ.get("QUERY_STRING", "")
        query = dict(urllib.parse.parse_qsl(query_string))
        headers = {}
        for k, v in environ.items():
            if k.startswith("HTTP_"):
                hk = k[5:].replace("_", "-").lower()
                headers[hk] = v
        ctype = headers.get("content-type", "")
        try:
            length = int(environ.get("CONTENT_LENGTH", 0))
        except Exception:
            length = 0
        raw = environ["wsgi.input"].read(length) if length else b""

        # Route
        if method == "POST" and path == f"{base}/chat":
            body = {}
            if ctype.startswith("application/json"):
                try:
                    body = json.loads(raw.decode("utf-8"))
                except Exception:
                    body = {}
            else:
                try:
                    body = json.loads(raw.decode("utf-8"))
                except Exception:
                    body = {}
            preq = PortableRequest(method, path, headers, query, body, None, environ)
            res = ResponseWriter(None)
            status, hdrs, chunks = await chat_handler(preq, res)

        elif method == "POST" and path == f"{base}/voice":
            body = {}
            audio_bytes = None
            if ctype.startswith("audio/"):
                audio_bytes = raw
            else:
                try:
                    body = json.loads(raw.decode("utf-8"))
                except Exception:
                    body = {}
            preq = PortableRequest(method, path, headers, query, body, audio_bytes, environ)
            res = ResponseWriter(None)
            status, hdrs, chunks = await voice_handler(preq, res)
        else:
            status = 404
            hdrs = {"Content-Type": "text/plain"}
            chunks = [b"Not Found"]

        status_line = f"{status} {'OK' if status<400 else 'ERROR'}"
        start_response(status_line, list(hdrs.items()))
        return chunks

    app["wsgi"] = _handle


def use_in_asgi(app, chat_handler, voice_handler, prefix=""):
    base = prefix or ""

    async def app_wrapper(scope, receive, send):
        if scope["type"] != "http":
            return

        method = scope["method"]
        path = scope["path"]
        query = dict(scope.get("query_string", b"").decode().split("&"))
        headers = {k.decode(): v.decode() for k, v in scope["headers"]}

        body_bytes = b""
        more_body = True
        while more_body:
            event = await receive()
            body_bytes += event.get("body", b"")
            more_body = event.get("more_body", False)

        ctype = headers.get("content-type", "")
        body = {}
        audio_bytes = None
        if ctype.startswith("audio/"):
            audio_bytes = body_bytes
        else:
            try:
                body = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                body = {}

        if method == "POST" and path == f"{base}/chat":
            preq = PortableRequest(method, path, headers, query, body, None, scope)
            pres = ResponseWriter(None)
            status, hdrs, chunks = await chat_handler(preq, pres)

        elif method == "POST" and path == f"{base}/voice":
            preq = PortableRequest(method, path, headers, query, body, audio_bytes, scope)
            pres = ResponseWriter(None)
            status, hdrs, chunks = await voice_handler(preq, pres)
        else:
            status, hdrs, chunks = 404, {"Content-Type": "text/plain"}, [b"Not Found"]

        await send({
            "type": "http.response.start",
            "status": status,
            "headers": [(k.encode(), v.encode()) for k, v in hdrs.items()],
        })
        await send({
            "type": "http.response.body",
            "body": b"".join(chunks),
        })

    app["asgi"] = app_wrapper



# ---------- Django ----------
def use_in_django(urlpatterns, chat_handler, voice_handler, prefix=""):
    from django.http import HttpResponse
    from django.views.decorators.csrf import csrf_exempt
    from django.urls import path
    import asyncio, json, inspect

    base = prefix or ""

    def _run_async(coro):
        """Run async handler in sync Django WSGI threads."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        if loop.is_running():
            # In ASGI (async Django), just return coroutine
            return coro
        else:
            return loop.run_until_complete(coro)

    @csrf_exempt
    def chat_view(request):
        headers = {k.lower(): v for k, v in request.headers.items()}
        method = request.method
        path_ = request.path
        query = dict(request.GET)
        try:
            body = json.loads(request.body.decode("utf-8"))
        except Exception:
            body = {}

        preq = PortableRequest(method, path_, headers, query, body, None, request)
        pres = ResponseWriter(HttpResponse)

        result = _run_async(chat_handler(preq, pres))

        # If ASGI async view, result is coroutine → Django handles it
        if inspect.iscoroutine(result):
            async def _async_response():
                status, hdrs, chunks = await result
                return HttpResponse(b"".join(chunks), status=status, headers=hdrs)
            return _async_response()
        else:
            status, hdrs, chunks = result
            return HttpResponse(b"".join(chunks), status=status, headers=hdrs)

    @csrf_exempt
    def voice_view(request):
        headers = {k.lower(): v for k, v in request.headers.items()}
        method = request.method
        path_ = request.path
        query = dict(request.GET)
        raw = request.body
        ctype = headers.get("content-type", "")
        body, audio_bytes = {}, None
        if ctype.startswith("audio/"):
            audio_bytes = raw
        else:
            try:
                body = json.loads(raw.decode("utf-8"))
            except Exception:
                body = {}

        preq = PortableRequest(method, path_, headers, query, body, audio_bytes, request)
        pres = ResponseWriter(HttpResponse)

        result = _run_async(voice_handler(preq, pres))

        if inspect.iscoroutine(result):
            async def _async_response():
                status, hdrs, chunks = await result
                return HttpResponse(b"".join(chunks), status=status, headers=hdrs)
            return _async_response()
        else:
            status, hdrs, chunks = result
            return HttpResponse(b"".join(chunks), status=status, headers=hdrs)

    urlpatterns += [
        path(f"{base}/chat", chat_view),
        path(f"{base}/voice", voice_view),
    ]
