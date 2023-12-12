import os
import requests
from dotenv import dotenv_values

env_vars = dotenv_values(".env")


class Client:
    def __init__(self, model: str = 'text-embedding-ada-002'):
        self._model = model

    def create(self, input: str):

        headers = {
            "Authorization": f"Bearer {env_vars['OPENAI_KEY']}",
            "Content-Type": "application/json"
        }

        data = {
            "input": input,
            "model": self._model,
            "encoding_format": "float"
        }

        response = requests.post(
            "https://api.openai.com/v1/embeddings", headers=headers, json=data).json()

        return response['data'][0]['embedding']

    async def acreate(self, input_url):
        # TODO: Implement asynchronous fetching of embedding using the input URL
        pass
