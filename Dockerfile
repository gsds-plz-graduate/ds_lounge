FROM python:3.11.1

WORKDIR /web

ENV GOOGLE_APPLICATION_CREDENTIALS "./application_default_credentials.json"
ENV GOOGLE_CLOUD_PROJECT "ornate-shine-367407"

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get autoremove -y \
    && apt-get install -y \
        gcc \
        build-essential \
        zlib1g-dev \
        wget \
        unzip \
        cmake \
        python3-dev \
        gfortran \
        libblas-dev \
        liblapack-dev \
        libatlas-base-dev \
    && apt-get clean

COPY . .
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -U scikit-learn==1.1.3
EXPOSE 8000
#CMD ["python3", "manage.py", "runserver", "0:8000"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "group_project.wsgi:application"]
