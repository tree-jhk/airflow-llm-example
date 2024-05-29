import os
from prompts import boaz_qa
from utils2 import *
from chromadb.config import Settings
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from openai import OpenAI
from dotenv import load_dotenv


def initialize_openai():
    load_dotenv()  # .env 파일 로드
    api_key = os.getenv('OPENAI_API_KEY')  # 환경 변수 읽기
    os.environ["OPENAI_API_KEY"] = api_key
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    return client, api_key


def initialize_chroma(api_key, embedding_model="text-embedding-ada-002", collection_name='BOAZ_data'):
    embedding_function = OpenAIEmbeddingFunction(api_key=api_key, model_name=embedding_model)
    chroma_client = chromadb.HttpClient(host="host.docker.internal", port=8000, settings=Settings(allow_reset=True, anonymized_telemetry=False))
    collection = chroma_client.get_collection(name=collection_name, embedding_function=embedding_function)
    return chroma_client, collection


def query_documents(collection, message, n_results=2):
    documents = collection.query(query_texts=message, n_results=n_results)
    return '\n\n'.join([documents['documents'][0][i] for i in range(len(documents['documents'][0]))])


def generate_response(client, model, context, question):
    llm_query = boaz_qa.format(context=context, question=question)
    response = openai_output(client=client, model=model, query=llm_query)
    return llm_query, response


if __name__ == '__main__':
    client, api_key = initialize_openai()
    chroma_client, collection = initialize_chroma(api_key)
    model = 'gpt-3.5-turbo'
    better_model = 'gpt-4-turbo'

    while True:
        message = input("질문을 입력해주세요: ")
        documents = query_documents(collection, message)
        llm_query, response = generate_response(client, model, context=documents, question=message)
        print(f"LLM 입력 프롬프트:\n\n{llm_query}")
        print(f"LLM 답변:\n\n{response}\n\n")
