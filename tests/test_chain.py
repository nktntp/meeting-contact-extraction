from langsmith import unit
import pytest
from src.utils import load_env_variables
from src.summarizer.chain import SummarizerChain
import json


INPUT = """John Doe: Hello everyone, thank you for joining us today.
    My name is John Doe, and I'm here with Jane Smith from our
    Product Team. We're excited to have this opportunity to discuss
    how Revenue Grid can support your sales operations.
"""


@unit
@pytest.mark.asyncio
async def test_summarizer_chain(output_keys=["user_input"]):
    envs = load_env_variables()
    
    with open('example/contact_schema.json') as f:
        contact_chema = json.load(f)
    with open('example/zoom_meeting.json') as f:
        meeting_info = json.load(f)
       
    # test1 
    chain = SummarizerChain(
        envs['MODEL_NAME'], envs['OPENAI_API_KEY'], contact_chema)
    result = await chain.ainvoke(INPUT, meeting_info)
    assert len(result) == 2
    
    # test2
    names = [contact['FirstName'] for contact in result]
    assert set(names) == {'John', 'Jane'}
