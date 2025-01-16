FROM python:3.8

WORKDIR /src

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

