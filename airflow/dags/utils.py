# -*- coding: utf-8 -*- 
# 위에거 주석 아니에요. 빼지 마세요 (for 한글)

import json
from dotenv import load_dotenv
# from langchain.text_splitter import SpacyTextSplitter
import warnings
warnings.filterwarnings('ignore')
import os
import time
from openai import OpenAI
import uuid
from datetime import datetime


load_dotenv()  # .env 파일 로드
api_key = os.getenv('OPENAI_API_KEY')  # 환경 변수 읽기

if api_key is None:
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
os.environ["OPENAI_API_KEY"] = api_key

# text_splitter = SpacyTextSplitter(chunk_size=500, pipeline="ko_core_news_sm")
model = 'gpt-3.5-turbo'
client = OpenAI(api_key=os.environ.get(api_key))

embedding_model="text-embedding-ada-002"

API_MAX_RETRY = 16
API_RETRY_SLEEP = 10
API_ERROR_OUTPUT = "$ERROR$"


def get_file_name(**context):
    execution_date = context['execution_date']
    start_date = context['dag'].default_args['start_date']

    # execution_date와 start_date가 datetime 객체인지 확인
    print(execution_date)
    print(start_date)
    if isinstance(execution_date, datetime) and isinstance(start_date, datetime):
        diff_days = (execution_date - start_date).days + 1
        print(f"Execution date는 다음과 같아: {execution_date}")
        print(f"Diff date는 다음과 같아: {diff_days}")
        return f"day{diff_days}"
    else:
        raise ValueError("execution_date와 start_date는 datetime 객체여야 합니다.")

def extract_text(dir_path, **context): # Extract
    file_name = get_file_name(**context) + '.txt'
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    print(f"읽은 텍스트는 다음과 같아: {text}")
    return text

def extract_text1(dir_path, file_name): # Extract
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def embed_texts(documents:str)->list: # Transform
    embed_documents = []
    documents = [documents]
    for doc in documents:
        embedding = client.embeddings.create(input=doc,
                                 model='text-embedding-ada-002')
        embed_doc = {'text': doc, 'embedding': embedding.data[0].embedding}
        embed_documents.append(embed_doc)
    return embed_documents

def get_text_embedding(document:str): # Transform
    embedding = client.embeddings.create(input=document,
                                 model='text-embedding-ada-002').data[0].embedding
    return embedding

def store_embeddings(embed_documents, vectorDB): # Load
    for idx, embed_doc in enumerate(embed_documents):
        # doc, embedding = embed_doc['text'], embed_doc['embedding'].data[0].embedding
        doc, embedding = embed_doc['text'], embed_doc['embedding']
        vectorDB.add(
            ids=str(uuid.uuid4()),
            documents=doc,
            embeddings=embedding
        )

def store_embedding(embed_document, document, vectorDB): # Load
    vectorDB.add(
        ids=str(uuid.uuid4()),
        documents=document,
        embeddings=embed_document
    )
    print(vectorDB.peek())

def openai_api_messages(prompt, status='user', chat_history=list()):
    if status == 'user':
        next_chat = [{"role": "user", "content": prompt}]
    elif status == 'system':
        next_chat = [{"role": "system", "content": prompt}]
    chat_history.extend(next_chat)
    return chat_history

def openai_output(client, model, query, chat_history=list()):
    openai_input = openai_api_messages(query, chat_history=chat_history)
    model = model
    output = API_ERROR_OUTPUT
    for _ in range(API_MAX_RETRY):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=openai_input,
                n=1,
                temperature=0,
            )
            output = response.choices[0].message.content
            break
        except:
            print("ERROR DURING OPENAI API")
            time.sleep(API_RETRY_SLEEP)
    return output