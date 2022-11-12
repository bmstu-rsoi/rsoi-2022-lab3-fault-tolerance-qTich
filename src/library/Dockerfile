FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR .
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8060
CMD python3 manage.py makemigrations && \
    python3 manage.py migrate && \
    python3 manage.py loaddata ./initial_data.json && \
    python3 manage.py runserver 0.0.0.0:8060
