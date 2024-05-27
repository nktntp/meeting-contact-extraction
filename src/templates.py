from typing import List, Dict
from langchain.prompts import PromptTemplate


class ExtractTemplate:
    def __init__(self, contact_schema: List[Dict[str, str]]) -> None:
        self.prompt_template = (
            "You are a helpful assistant that helps sales executives to summarize information from a zoom meeting transcript\n"
            "Your goal is to extract valuable information about meeting participants.\n"
            "Return the response as a list with every participant info as a json object with the below fields:\n"
            + self.get_fields_description(contact_schema) +
            "If some field info is not mentioned in the transcript or you are not sure, assign empty line to it \"\".\n"
            "Return explanation for the answer.\n"
            "{text}\n"
        )

        self.prompt = PromptTemplate.from_template(self.prompt_template)

    @staticmethod
    def get_fields_description(contact_schema: List[Dict[str, str]]) -> str:
        return ''.join([f"\"{field['name']}\": {field['type']} // {field['description']}\n"
                        for field in contact_schema])


class ReduceTemplate:
    def __init__(self, format_instructions) -> None:
        self.prompt_template = (
            "The following is set of summaries of the meeting transcript:\n"
            "Each summary is a list of json objects that describes a meeting participant.\n"
            "{text}\n"
            "Take these and output final list that is a summary of the meeting transcript.\n"
            "Your output must be the list of participants info and nothing else.\n"
            "{format_instructions}"
        )

        self.prompt = PromptTemplate.from_template(
            template=self.prompt_template, 
            partial_variables={"format_instructions": format_instructions},
        )
