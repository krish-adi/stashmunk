from litellm import completion, acompletion
from dotenv import dotenv_values

env_vars = dotenv_values(".env")


class ClassificationSummarizationAgent:
    def __init__(self, model: str = 'gpt-3.5-turbo-1106'):
        self._model = model

    def _make_messages(self, input: str):

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. You will provide your response "
                "in JSON format."
            },
            {
                "role": "user",
                "content": "You are provided with a text delimited by three backticks. You task"
                "is to classify the text as containing useful information or not. You will do so "
                "by also providing a confidence percentage. You will provide your reponse "
                "in JSON format only. Here is a example of a response: "
                "\n"
                "{'useful': True, 'confidence': 90}"
                "\n"
                "Here is the text to classify:"
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
            response_format={"type": "json_object"}
        )

        return response.choices[0].message.content
    
    async def aexecute(self, input: str):

        messages = self._make_messages(input)

        response = await acompletion(
            model=self._model,
            messages=messages,
            api_key=env_vars['OPENAI_API_KEY'],
            # max_tokens=10,
            response_format={"type": "json_object"}
        )

        return response.choices[0].message.content
