FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

ENV REDIS_URL=redis://0.0.0.0:6379/1

COPY . .

RUN pip3 install -r requirements.txt

CMD ["flask", "run", "--host=0.0.0.0"]
