FROM python:3.10.9-slim-bullseye

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY whereisit .

CMD ["python", "main.py"]