FROM python
ENV PYTHONUNBUFFERRED 1
WORKDIR /web
COPY . .
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt
CMD ["python3", "manage.py", "runserver", "0:8000"]
EXPOSE 8000
