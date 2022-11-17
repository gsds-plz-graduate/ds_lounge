FROM python:3
ENV PYTHONUNBUFFERRED 1
WORKDIR /web
COPY . .
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt