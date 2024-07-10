import os
from openai import AzureOpenAI, AsyncAzureOpenAI

from faker import Faker
import random

from collections import namedtuple

MocResponse = namedtuple('MocResponse', 'choices')
MocChoice = namedtuple('MocMessage', 'message')
MocMessage = namedtuple('MocContent', 'content')

class MocCompletions:
    def create(self, model, messages, *args, **kwargs):
        fake = Faker('ja-JP')
        choices = [ MocChoice(message=MocMessage(content=fake.text())) for _ in range(random.randint(1, 5)) ]
        # choices = [ MocChoice(
        #     message = MocMessage("\n\n".join([msg["role"] + ": " + msg["content"] for msg in messages]))
        # )]

        return MocResponse(choices=choices)


class MocChat:
    def __init__(self, *args, **kwargs):
        self.completions = MocCompletions()


class MocApi:
    def __init__(self):
        self.chat = MocChat()


class ApiClientHandler:
    api_name_list = [
        "dev",
        "azure",
        "async-azure",
    ]
    
    @property
    def api_name(self):
        return self._api_name

    @property
    def api(self):
        return self._api

    @classmethod
    def get_api_client(cls, api_name:str = "azure"):
        if api_name == "azure":
            api_client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            )
        elif api_name == "async-azure":
            api_client = AsyncAzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            )
        elif api_name == "dev":
            api_client = MocApi()
        else:
            raise ValueError("Not Valid API. Choose from followings: {api_name_list}".format(api_name_list=", ".join(cls.api_name_list)))

        return api_client
    
    def __init__(self, api_name:str):
        self._api_name = api_name
        self._api = self.get_api_client(api_name)
    