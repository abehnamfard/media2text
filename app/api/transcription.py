import os
import asyncio
import logging
from typing import Dict, Any

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    status,
    Request
)
from pydantic import BaseModel

# Import the service module itself
from app.services import transcription as transcription_service
from app.utils.file_processing import save_upload_file_tmp, extract_audio_from_video

router = APIRouter()
logger = logging.getLogger(__name__)

class TranscriptionResponse(BaseModel):
    language: str
    language_probability: float
    text: str
    segments: list[Dict[str, Any]]


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_file(request: Request, file: UploadFile = File(...)):
    if not file.content_type.startswith(('audio/', 'video/')):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Please upload an audio or video file."
        )

    tmp_path = None
    audio_path = None

    try:
        tmp_path = await save_upload_file_tmp(file)
        is_video = file.content_type.startswith('video/')

        if is_video:
            audio_path = extract_audio_from_video(tmp_path)
        else:
            audio_path = tmp_path

        loop = asyncio.get_running_loop()
        process_pool = request.app.state.process_pool
        
        # We now call the module-level function, not a class method.
        # Python pickles the function and its arguments (just the audio_path string),
        # which is perfectly fine. The function then executes in a worker process
        # that already has the model loaded in its own memory.
        result = await loop.run_in_executor(
            process_pool,
            transcription_service.transcribe_audio,
            audio_path
        )
        
        return result

    except Exception as e:
        logger.error(f"An error occurred during transcription: {e}")
        # This is a safe way to show the error from the worker process
        # without exposing too much detail in a production environment.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during transcription: {e}"
        )
    finally:
        # Clean up temporary files
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
        if audio_path and audio_path != tmp_path and os.path.exists(audio_path):
            os.remove(audio_path)