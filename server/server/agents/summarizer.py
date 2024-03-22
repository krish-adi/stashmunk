from litellm import completion, acompletion
from dotenv import dotenv_values

env_vars = dotenv_values(".env")


class SummarizationAgent:
    def __init__(self, model: str = 'gpt-3.5-turbo-0125'):
        self._model = model

    def _make_messages(self, input: str):
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Summarize the following text delimited by three backticks in a "
                "clear and concise manner that preserves the main entities mentioned in the "
                "text and their relation. Present only the summarization, and no not mention "
                "the source of the text such as ir being a paper, article, post, comment or blog."
                "\n"
                "```"
                f"\n{input}"
                "```"
            }
        ]

        return messages

    def execute(self, input: str):

        messages = self._make_messages(input)

        response = completion(
            model=self._model,
            messages=messages,
            api_key=env_vars['OPENAI_API_KEY'],
            # max_tokens=10,
        )

        return response.choices[0].message.content
    
    async def aexecute(self, input: str):

        messages = self._make_messages(input)

        response = await acompletion(
            model=self._model,
            messages=messages,
            api_key=env_vars['OPENAI_API_KEY'],
            # max_tokens=10,
        )

        return response.choices[0].message.content
