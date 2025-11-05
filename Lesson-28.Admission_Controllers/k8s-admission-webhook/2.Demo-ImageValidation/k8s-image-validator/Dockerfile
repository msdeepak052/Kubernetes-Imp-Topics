FROM python:3.11-slim

WORKDIR /app

COPY image-validator.py /app/
COPY tls/ /certs/

RUN pip install flask

EXPOSE 8443

CMD ["python3", "image-validator.py"]