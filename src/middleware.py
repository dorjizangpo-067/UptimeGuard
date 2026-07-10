import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.requests import Request

logger = logging.getLogger("uvicorn.access")
logger.disabled = True


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def custome_logging(request: Request, call_next):
        start_time = time.time()

        responses = await call_next(request)
        processing_time = time.time() - start_time

        # Handle case where request.client might be None
        client_info = (
            f"{request.client.host}:{request.client.port}"
            if request.client
            else "unknown"
        )

        message = f"{client_info} - {request.method} - {request.url.path} - {responses.status_code} completed after: {processing_time}s"
        print(message)  # type : ignore T201

        return responses

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
