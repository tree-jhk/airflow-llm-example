import time
import warnings
from dotenv import load_dotenv
import os

warnings.filterwarnings('ignore')
load_dotenv()  # .env 파일 로드

api_key = os.getenv('OPENAI_API_KEY')  # 환경 변수 읽기
os.environ["OPENAI_API_KEY"] = api_key

model = 'gpt-3.5-turbo'
better_model = 'gpt-4-turbo'


API_MAX_RETRY = 16
API_RETRY_SLEEP = 10
API_ERROR_OUTPUT = "$ERROR$"

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