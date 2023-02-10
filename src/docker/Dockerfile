FROM python:3.9-slim-bullseye

RUN apt-get update -y
RUN apt-get install -y git

COPY src/docker/requirements.txt /code/requirements.txt
RUN pip3 install -r /code/requirements.txt

COPY src/docker/src /code/src
#RUN echo "$(ls /app/src)" > /tmp/log
ENTRYPOINT ["python3", "/code/src/main.py"]
