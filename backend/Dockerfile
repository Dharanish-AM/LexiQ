FROM python:3.10-slim

RUN apt-get update && apt-get install -y build-essential tesseract-ocr poppler-utils

WORKDIR /app

# copy requirements file
COPY app/requirements.txt /app/requirements.txt

# install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy rest of the backend code
COPY app /app

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]