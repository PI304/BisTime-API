FROM python:3.10

COPY ./ /home/convey/

WORKDIR /home/convey/

RUN apt-get update

RUN pip install --no-cache-dir -r requirements.txt