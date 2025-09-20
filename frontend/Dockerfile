FROM python:3.10-slim

RUN apt-get update && apt-get install -y build-essential tesseract-ocr poppler-utils

WORKDIR /app

# copy requirements file from the correct path
COPY requirements.txt /app/requirements.txt

# install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy the rest of frontend code
COPY . /app

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]