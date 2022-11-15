FROM python:3
ENV PYTHONUNBUFFERRED 1
WORKDIR /web
COPY . .
RUN pip install -r requirements.txt