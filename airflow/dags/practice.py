# -*- coding: utf-8 -*- 
# 위에거 주석 아니에요. 빼지 마세요 (for 한글)

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os
import warnings
import random
from utils import extract_text, embed_texts, store_embeddings, store_embedding
from chromadb.config import Settings
import chromadb
import uuid

warnings.filterwarnings('ignore')
COLLECTION_NAME='BOAZ_data'

def set_chromadb_collection():
    chroma_client = chromadb.HttpClient(host="host.docker.internal", port=8000, settings=Settings(allow_reset=True, anonymized_telemetry=False))
    collections = chroma_client.list_collections()
    is_collection_exist = any(collection.name == COLLECTION_NAME for collection in collections)
    if is_collection_exist:
        vectorDB = chroma_client.get_collection(COLLECTION_NAME)
    else:
        vectorDB = chroma_client.create_collection(name=COLLECTION_NAME)
    return vectorDB

def extract_texts_task_callable(**kwargs):
    if random.random() < 0.2:  # 20% 확률로 예외 발생
        raise Exception("Random failure occurred in extract_texts_task_callable")
    else:
        dir_path = os.path.join(os.path.dirname(__file__), '../data') # 텍스트 파일이 위치한 디렉토리 경로
        return extract_text(dir_path, **kwargs)

def embed_texts_task_callable(**kwargs):
    if random.random() < 0.2:  # 20% 확률로 예외 발생
        raise Exception("Random failure occurred in embed_texts_task_callable")
    else:
        ti = kwargs['ti']
        documents = ti.xcom_pull(task_ids='extract_texts')
        embedded_documents = embed_texts(documents)
        ti.xcom_push(key='embedded_documents', value=embedded_documents)
        return embedded_documents

def store_embedding_task_callable(**kwargs):
    ti = kwargs['ti']
    embedded_documents = ti.xcom_pull(task_ids='embed_texts', key='embedded_documents')
    vectorDB = kwargs['vectorDB']

    for embed_doc in embedded_documents:
        document = embed_doc['text']
        embedding = embed_doc['embedding']
        store_embedding(embedding, document, vectorDB)

default_args = {
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 0,
    'retry_delay': timedelta(seconds=10),
}

dag = DAG(
    dag_id='boaz_RAG_ETL',
    default_args=default_args,
    description='Load texts, embed, and store embeddings',
    schedule_interval=timedelta(days=1),
    tags=["BOAZ"],  # 팀별로, 태스크별로 tag 붙일 수 있음 (DAG 수백개 되면 하나하나 기억할 수 없음. tag 필수)
    end_date=datetime(2023, 1, 5),
)

vectorDB = set_chromadb_collection()

# Extract
extract_texts_task = PythonOperator(
    task_id='extract_texts',
    provide_context=True,  # DAG 실행 컨텍스트를 함수에 전달
    python_callable=???,
    dag=dag,
)

# Transform
embed_texts_task = PythonOperator(
    task_id='embed_texts',
    provide_context=True,  # DAG 실행 컨텍스트를 함수에 전달
    python_callable=???,
    dag=dag,
)

# Load
store_embedding_task = PythonOperator(
    task_id='store_embedding',
    provide_context=True,  # DAG 실행 컨텍스트를 함수에 전달
    python_callable=???,
    op_kwargs={'vectorDB': vectorDB},  # vectorDB를 함수 인자로 전달
    dag=dag,
)

# Task Dependencies
??? >> ??? >> ???