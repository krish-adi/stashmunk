import os
import requests
from dotenv import dotenv_values

env_vars = dotenv_values(".env")


class EntityRecognizerClient:
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
