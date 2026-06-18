FROM python:3.12-slim

WORKDIR /app
COPY receiver.py .

# Default configuration — override in docker-compose.yml or with `docker run -e`.
ENV BIND_HOST=0.0.0.0 \
    PORT=18999 \
    PROTO=both

EXPOSE 18999/udp
EXPOSE 18999/tcp

# -u = unbuffered stdout (live logs in `docker logs`).
CMD ["python", "-u", "receiver.py"]
