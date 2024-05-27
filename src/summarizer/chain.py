from langchain_text_splitters import CharacterTextSplitter
from langchain.chains import (
    LLMChain, StuffDocumentsChain, ReduceDocumentsChain,
    MapReduceDocumentsChain
)
from langchain_community.chat_models import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Dict, Any, Optional
import json

from src.templates import ExtractTemplate, ReduceTemplate
from src.utils import load_env_variables

import os

envs = load_env_variables()
os.environ['LANGCHAIN_API_KEY'] = envs['LANGCHAIN_API_KEY']
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
project_name = envs['LANGCHAIN_PROJECT']


class SummarizerChain:
    def __init__(
        self,
        model_name: str,
        api_key: str,
        contact_schema: List[Dict[str, str]]
    ) -> None:
        self.contact_schema = contact_schema
        # init model
        self.model = self._init_model(model_name, api_key)
        # init prompts
        self.parser = JsonOutputParser()
        self.map_template = ExtractTemplate(contact_schema)
        self.reduce_template = ReduceTemplate(
            format_instructions=self.parser.get_format_instructions())

    @staticmethod
    def _init_model(model_name: str, api_key: str) -> ChatOpenAI:
        return ChatOpenAI(
            model=model_name, api_key=api_key, temperature=0
        )
    
    @staticmethod
    def find_participant_by_name(meeting_info: Dict[str, Any], 
                                 name: str) -> Optional[Dict[str, str]]:
        for participant in meeting_info['participants']:
            if participant['name'] == name:
                return participant
        
    def _refine_with_meeting_info(
        self,
        summary: List[Dict[str, str]],
        meeting_info: Dict[str, Any],
        add_email: bool = True
    ) -> List[Dict[str, str]]:
        refine_summary = []
        for contact in summary:
            if 'FirstName' in contact and 'LastName' in contact:
                participant = self.find_participant_by_name(
                    meeting_info, f'{contact["FirstName"]} {contact["LastName"]}')

                if add_email and participant is not None \
                    and ('Email' not in contact or contact['Email'] == ''):
                    contact['Email'] = participant['email']
                    
            refine_summary.append(contact)
            
        return refine_summary
    
    async def ainvoke(
        self,
        transcript: str,
        meeting_info: Dict[str, Any]
    ) -> Dict[str, str]:
        # Transcript split:
        # Split meeting transcript into smaller chunks to be proccesed 
        # individually because of a limited context window size of LLMs
        text_splitter = CharacterTextSplitter(
            separator          = '\n',
            chunk_size         = 1000,
            chunk_overlap      = 200,
            length_function    = len,
            is_separator_regex = False
        )
        texts = text_splitter.create_documents([transcript])

        # MapReduce:
        # Summarize each document individually (map step) and then combine
        # these summaries into a final summary (reduce step)
        map_chain = LLMChain(llm=self.model, prompt=self.map_template.prompt)
        reduce_chain = LLMChain(
            llm=self.model, prompt=self.reduce_template.prompt, output_parser=self.parser)
        

        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_chain, document_variable_name='text')

        reduce_documents_chain = ReduceDocumentsChain(
            combine_documents_chain  = combine_documents_chain,
            collapse_documents_chain = combine_documents_chain,
            token_max                = 4000
        )

        map_reduce_chain = MapReduceDocumentsChain(
            llm_chain                 = map_chain,
            reduce_documents_chain    = reduce_documents_chain,
            document_variable_name    = 'text',
            return_intermediate_steps = False
        )
        chain = map_reduce_chain
        
        answer = await chain.ainvoke(texts)
        # Add zoom meeting metadata like email address to the final summary
        answer = self._refine_with_meeting_info(answer['output_text'], meeting_info)
        return answer
