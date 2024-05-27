from simple_salesforce import Salesforce
import requests
from typing import List, Dict, Any, Self

from src.constants import (
    SALESFORCE_GRANT_TYPE, SALESFORCE_OAUTH2_URL, SALESFORCE_ID_FIELD,
    SALESFORCE_BULCK_BATCH
)
from src.utils import load_env_variables

envs = load_env_variables()


class Client:
    _instance = None
    
    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super(Client, cls).__new__(cls)
            cls._instance.sf = None
            cls._instance.history = dict()
        return cls._instance

    def authenticate(self, username: str, password: str) -> None:
        oauth2_params = {
            'grant_type': SALESFORCE_GRANT_TYPE,
            'client_id': envs['CONSUMER_ID'],
            'client_secret': envs['CONSUMER_SECRET'],
            'username': username, # Email address
            'password': password # Concat your password and your security token
        }
        response = requests.post(SALESFORCE_OAUTH2_URL, params=oauth2_params)
        return response.json()
    
    def get_salesforce_instance(self, token: str) -> Self:
        if self.sf is None:
            self.sf = Salesforce(instance_url=envs['INSTANCE_URL'],
                                 session_id=token)
        return self.sf
    
    def upsert_contracts(self, contracts: List[Dict[str, Any]], token: str) -> List[Dict]:
        sf_instance = self.get_salesforce_instance(token)
        created = sf_instance.bulk.Contact.upsert(
            contracts, SALESFORCE_ID_FIELD, batch_size=SALESFORCE_BULCK_BATCH, use_serial=True)
        return created
