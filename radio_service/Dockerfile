FROM python:3.12-alpine

RUN apk add --no-cache \
    ffmpeg \
    font-dejavu \
    && pip install --no-cache-dir yt-dlp Pillow

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/music /app/submissions /app/data /app/assets

VOLUME ["/app/music", "/app/submissions", "/app/data", "/app/assets"]

CMD ["python", "stream.py"]
