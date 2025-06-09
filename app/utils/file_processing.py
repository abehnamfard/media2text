import ffmpeg
import tempfile
import logging
from fastapi import UploadFile

logger = logging.getLogger(__name__)

async def save_upload_file_tmp(upload_file: UploadFile) -> str:
    """Saves an uploaded file to a temporary file and returns the path."""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{upload_file.filename}") as tmp:
            # Write the uploaded file content to the temporary file
            content = await upload_file.read()
            tmp.write(content)
            return tmp.name
    except Exception as e:
        logger.error(f"Could not save uploaded file: {e}")
        raise

def extract_audio_from_video(video_path: str) -> str:
    """Extracts audio from a video file and saves it as a temporary WAV file."""
    logger.info(f"Extracting audio from {video_path}")
    try:
        # Create a temporary file for the audio output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
            audio_path = tmp_audio.name

        # Use ffmpeg to extract audio, converting it to 16kHz mono WAV, which is ideal for Whisper
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, acodec='pcm_s16le', ac=1, ar='16k')
            .run(cmd='ffmpeg', quiet=True, overwrite_output=True)
        )
        logger.info(f"Audio extracted successfully to {audio_path}")
        return audio_path
    except ffmpeg.Error as e:
        logger.error(f"FFmpeg error extracting audio: {e.stderr.decode()}")
        raise
    except Exception as e:
        logger.error(f"Error extracting audio: {e}")
        raise