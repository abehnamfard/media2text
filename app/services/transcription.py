import logging
import os
from faster_whisper import WhisperModel
from app.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Module-level global variable to hold the model
# This will be initialized in each worker process
_model: WhisperModel = None


def init_model():
    """
    This function is called by the ProcessPoolExecutor's initializer.
    It loads the Whisper model into the global `_model` variable in each worker process.
    """
    global _model
    # Get the process ID for logging
    pid = os.getpid()
    
    if _model is None:
        logger.info(f"[Worker PID: {pid}] Loading model '{settings.WHISPER_MODEL}' on device '{settings.DEVICE}' with compute_type '{settings.COMPUTE_TYPE}'...")
        try:
            _model = WhisperModel(
                settings.WHISPER_MODEL,
                device=settings.DEVICE,
                compute_type=settings.COMPUTE_TYPE
            )
            logger.info(f"[Worker PID: {pid}] Model loaded successfully.")
        except Exception as e:
            logger.error(f"[Worker PID: {pid}] Failed to load model: {e}")
            # Re-raise the exception to indicate a failed worker initialization
            raise
    else:
        logger.info(f"[Worker PID: {pid}] Model already loaded.")


def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribes an audio file using the model loaded in the current worker process.
    This is the function that will be executed by the ProcessPoolExecutor.
    """
    pid = os.getpid()
    if _model is None:
        # This should not happen if the initializer is set up correctly
        logger.error(f"[Worker PID: {pid}] Model is not loaded! This indicates an issue with the ProcessPoolExecutor initializer.")
        raise RuntimeError("Model is not loaded in this worker process.")

    logger.info(f"[Worker PID: {pid}] Starting transcription for {audio_path}...")
    try:
        segments, info = _model.transcribe(audio_path, task='transcribe', beam_size=5)

        logger.info(f"Detected language '{info.language}' with probability {info.language_probability}")

        result_segments = []
        full_text = ""
        for segment in segments:
            result_segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            })
            full_text += segment.text + " "

        logger.info(f"[Worker PID: {pid}] Transcription for {audio_path} completed.")
        return {
            "language": info.language,
            "language_probability": info.language_probability,
            "text": full_text.strip(),
            "segments": result_segments
        }
    except Exception as e:
        logger.error(f"Error during transcription in worker {pid} for {audio_path}: {e}")
        raise