FROM python:3.11-slim

WORKDIR /app

COPY validate-pod.py /app/
COPY tls/ /certs/

RUN chmod 644 /certs/tls.crt /certs/tls.key

RUN pip install flask

EXPOSE 8443

CMD ["python3", "validate-pod.py"]