import logging
from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.api import transcription as transcription_router
from app.services import transcription as transcription_service # Import the module for the initializer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Context manager for application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    logger.info("Application startup...")
    
    # We provide an initializer function to the ProcessPoolExecutor.
    # This function (transcription_service.init_model) will be called
    # for each worker process when it's created.
    app.state.process_pool = ProcessPoolExecutor(
        max_workers=settings.MAX_WORKERS,
        initializer=transcription_service.init_model
    )
    logger.info(f"Process pool started with {settings.MAX_WORKERS} workers. Model loading will occur in each worker.")

    yield

    # --- Shutdown ---
    logger.info("Application shutdown...")
    app.state.process_pool.shutdown(wait=True)
    logger.info("Process pool shut down gracefully.")

# Create the FastAPI app instance with the lifespan context manager
app = FastAPI(
    title="High-Performance Whisper API",
    description="A production-grade FastAPI service for audio transcription using faster-whisper.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Include Routers ---
app.include_router(
    transcription_router.router,
    prefix="/v1",
    tags=["Transcription"]
)

# --- Health Check ---
@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "ok"}