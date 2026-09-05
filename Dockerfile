FROM python:3.12-slim

WORKDIR /app-python

COPY requirements-dev.txt .
COPY requirements.txt .
RUN pip install -r requirements-dev.txt
COPY . .

EXPOSE 8080

CMD  ["python3","app.py"]

#Prueba PR
