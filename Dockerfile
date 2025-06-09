# ---- Builder Stage ----
# This stage installs dependencies, including system-level ones like ffmpeg.
FROM python:3.10-slim as builder

# Set environment variables to prevent interactive prompts during installation
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies required for ffmpeg and building python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy and install Python requirements
COPY requirements.txt .
# We install pytorch separately for CPU or GPU builds if needed, but faster-whisper handles it.
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ---- Final Stage ----
# This stage creates the final, lean production image.
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install ffmpeg from the builder stage
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the installed python packages from the builder stage
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy the application code
COPY ./app ./app

# Expose the port the app runs on
EXPOSE 8000

# Run the application
# We use uvicorn with multiple workers. The number of workers should ideally be (2 * CPU_CORES) + 1
# However, for a CPU-bound app like this, it's better to use a single uvicorn worker
# and let our ProcessPoolExecutor manage concurrency.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]