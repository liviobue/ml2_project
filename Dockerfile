FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0

ARG API_KEY
ARG CONNECTION_STRING

ENV API_KEY=$API_KEY
ENV CONNECTION_STRING=$CONNECTION_STRING

WORKDIR /usr/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501
CMD ["sh", "-c", "streamlit run --server.port 8501 /usr/app/app.py"]