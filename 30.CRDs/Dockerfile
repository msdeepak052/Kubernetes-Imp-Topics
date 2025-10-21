# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY crontab-controller.py .
RUN pip install kubernetes

CMD ["python", "crontab-controller.py"]
