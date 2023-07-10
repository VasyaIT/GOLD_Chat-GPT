FROM python:3.10.8

WORKDIR /bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src/ .

RUN python main.py
