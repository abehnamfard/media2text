from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Model configuration
    WHISPER_MODEL: str = "large-v3"
    
    # Options: "float16", "int8_float16", "int8"
    # For CPU, "int8" is recommended. For GPU, "float16" is standard.
    COMPUTE_TYPE: str = "int8"
    
    # "cuda" for GPU, "cpu" for CPU
    DEVICE: str = "cpu"

    # Concurrency control for the transcription service
    # This should be tuned based on your machine's resources (CPU cores, RAM)
    MAX_WORKERS: int = 2

    # For pydantic-settings to find the .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="ignore")

settings = Settings()