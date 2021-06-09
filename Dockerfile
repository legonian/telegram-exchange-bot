FROM python:3

COPY . /app
WORKDIR /app

ENV EXCHANGE_TELEGRAM_BOT=secrettokenstring

RUN pip3 install -r requirements.txt
ENTRYPOINT python3 app.py