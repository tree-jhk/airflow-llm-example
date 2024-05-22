# Dockerfile
FROM apache/airflow:2.9.1-python3.10

USER root

RUN apt-get update && apt-get install -y build-essential
RUN apt-get install -y default-libmysqlclient-dev

COPY requirements.txt /requirements.txt

USER airflow
RUN pip install --no-cache-dir -r /requirements.txt
RUN pip install --upgrade spacy
RUN python -m spacy download ko_core_news_sm

CMD ["webserver"]