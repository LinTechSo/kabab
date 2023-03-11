FROM hub.hamdocker.ir/python:3.11-alpine

WORKDIR /app

ADD ./requirements.txt ./
RUN pip install -r ./requirements.txt

COPY ./ ./

