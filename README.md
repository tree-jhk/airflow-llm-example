# BOAZ - Airflow 실습 시간 (실습 설명 및 개발: 권준혁)
## 부제: Airflow를 활용해서, LLM RAG에서의 ETL을 경험하자!
![Boaz-llm-airflow (1)](https://github.com/tree-jhk/boaz-airflow-llm-example/assets/97151660/8d96aeb0-fe5c-4431-ae90-fadb5ab297ef)  
(전체 파이프라인)
## 실습 setting
```python
git clone https://github.com/tree-jhk/boaz-airflow-llm-example.git
```

```python
cd boaz-airflow-llm-example
```

- boaz-airflow-llm-example 디렉토리에 `.env` 파일 추가하기
    
    ```python
    OPENAI_API_KEY=YOUR_API_KEY
    AIRFLOW_UID=50000
    AIRFLOW__CORE__DEFAULT_TIMEZONE=UTC
    TZ=UTC
    ```
    

## Docker 켜기

```python
docker-compose up -d
```

## 코드 채우기

### PythonOperator 사용하기

```python
# Extract
extract_texts_task = PythonOperator(
    task_id='extract_texts',
    provide_context=True,  # DAG 실행 컨텍스트를 함수에 전달
    python_callable=extract_texts_task_callable,
    dag=dag,
)

# Transform
embed_texts_task = PythonOperator(
    task_id='embed_texts',
    provide_context=True,  # DAG 실행 컨텍스트를 함수에 전달
    python_callable=embed_texts_task_callable,
    dag=dag,
)

# Load
store_embedding_task = PythonOperator(
    task_id='store_embedding',
    provide_context=True,  # DAG 실행 컨텍스트를 함수에 전달
    python_callable=store_embedding_task_callable,
    op_kwargs={'vectorDB': vectorDB},  # vectorDB를 함수 인자로 전달
    dag=dag,
)
```

### 3.3.2 Task 의존성 정의하기

```python
# Task Dependencies
extract_texts_task >> embed_texts_task >> store_embedding_task
```

## 장애 대응하기

- 20% 확률로 장애가 발생하는 2개 task를 대응하자.
- retry!
```python
default_args = {
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 5,
    'retry_delay': timedelta(seconds=10),
}
```

## RAG chatting 해보기

```python
docker exec -it boaz-airflow-llm-airflow-webserver-1 /bin/bash
```

```python
cd dags
python chat.py
```

- data 파일에 있는 데이터를 기반으로 채팅해보기
