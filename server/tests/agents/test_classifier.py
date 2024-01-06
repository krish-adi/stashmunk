from server.agents.usefull_classifier import UsefullClassificationAgent
import asyncio
import json

usefull_classifier = UsefullClassificationAgent()

text = 'l u J 4 1 ] O R . s c ['

_res = asyncio.run(usefull_classifier.aexecute(text))

print(type(_res))
_use = json.loads(_res)
print(not _use['useful'])