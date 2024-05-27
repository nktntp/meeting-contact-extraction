from fastapi import (
    FastAPI, UploadFile, HTTPException, Request
)
import json
from webvtt import WebVTT
from io import StringIO

from src.client import Client
from src.utils import webvtt_extract_notes, load_env_variables
from src.summarizer.chain import SummarizerChain


app = FastAPI()


@app.get("/oauth2/access_token")
def access_token(username: str, password: str):
    client = Client()
    try:
        response = client.authenticate(username, password)
        return {
            "message": "Salesforce authenticated successfully!",
            'instance_url': response.get('instance_url'),
            'access_token': response.get('access_token')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/summarize")
async def summarize(
    transcript: UploadFile,
    zoom_meeting: UploadFile,
    contact_schema: UploadFile,
    request: Request
):
    token = request.headers["authorization"]
    envs = load_env_variables()
    
    transcript = transcript.file.read().decode('utf-8')
    transcript = WebVTT.from_buffer(StringIO(transcript))
    meeting_info = json.load(zoom_meeting.file)
    contact_schema = json.load(contact_schema.file)
    
    text = webvtt_extract_notes(transcript)
    chain = SummarizerChain(
        model_name     = envs['MODEL_NAME'], 
        api_key        = envs['OPENAI_API_KEY'], 
        contact_schema = contact_schema
    )
    
    summary = await chain.ainvoke(text, meeting_info)

    try:
        client = Client()
        response = client.upsert_contracts(summary, token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return response


@app.get("/")
def health_check():
    return {"message": "alive"}
