FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential tesseract-ocr poppler-utils curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements file
COPY app/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install spaCy English model
RUN python -m spacy download en_core_web_sm

# Copy backend code
COPY app /app

# Expose port
EXPOSE 8000

# Start the backend server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
