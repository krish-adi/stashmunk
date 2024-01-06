from dotenv import dotenv_values
from litellm import embedding, aembedding, EmbeddingResponse


env_vars = dotenv_values(".env")


class TextEmbeddingAgent:
    def __init__(self, model: str = 'text-embedding-ada-002'):
        self._model = model
        self._dim = 1536

    def execute(self, input: str):

        response: EmbeddingResponse = embedding(
            model=self._model,
            input=[input],
            api_key=env_vars['OPENAI_API_KEY'],
        )

        return response.data[0]['embedding']

    async def aexecute(self, input: str):

        response: EmbeddingResponse = await aembedding(
            model=self._model,
            input=[input],
            api_key=env_vars['OPENAI_API_KEY'],
        )

        return response.data[0]['embedding']
