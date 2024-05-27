from webvtt import WebVTT, read
from typing import Dict
from pathlib import Path
import os
from dotenv import load_dotenv


def webvtt_extract_notes(file: WebVTT | str) -> str:
    transctipt = file if not isinstance(file, str) else read(file)
    return '\n'.join([caption.text for caption in transctipt])

def load_env_variables() -> Dict[str, str]:
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)

    model_name = os.getenv('MODEL_NAME')
    open_ai_key = os.getenv('OPENAI_API_KEY')
    langchain_api_key = os.getenv('LANGCHAIN_API_KEY')
    langchain_project = os.getenv('LANGCHAIN_PROJECT')
    consumer_id = os.getenv('CONSUMER_ID')
    consumer_secret = os.getenv('CONSUMER_SECRET')
    instance_url = os.getenv('INSTANCE_URL')
    
    return {
        'MODEL_NAME': model_name,
        'OPENAI_API_KEY': open_ai_key,
        'LANGCHAIN_API_KEY': langchain_api_key,
        'LANGCHAIN_PROJECT': langchain_project, 
        'CONSUMER_ID': consumer_id,
        'CONSUMER_SECRET': consumer_secret,
        'INSTANCE_URL': instance_url
    }
