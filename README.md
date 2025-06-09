# Media2Text

This project provides a backend service for transcription. It is built using Python and organized with a clear modular structure.

## Project Structure

- `app/` - Main application code
  - `main.py` - Entry point of the application
  - `config.py` - Configuration settings
  - `api/` - API route handlers
    - `transcription.py` - API endpoints related to transcription
  - `services/` - Business logic and service layer
    - `transcription.py` - Transcription service implementation
  - `utils/` - Utility modules
    - `file_processing.py` - File processing utilities

## Environment Configuration

- `.env.example` - Example environment variables file

## Docker Support

- `Dockerfile` - Docker image definition for the application
- `docker-compose.yml` - Docker Compose configuration for running the app and dependencies

## Requirements

- `requirements.txt` - Python dependencies list

## Setup and Running

1. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Configure environment variables by copying `.env.example` to `.env` and updating as needed.

3. Run the application:

   ```bash
   uvicorn app.main:app --reload
   ```

## Docker Usage

To build and run the application using Docker:

```bash
docker-compose up --build
```

## API

The project exposes transcription-related API endpoints under `app/api/transcription.py`. Refer to the source code for detailed API routes and usage.

## Contributing

Contributions are welcome. Please fork the repository and submit pull requests.
