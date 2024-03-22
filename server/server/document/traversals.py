from server.document.node import Node
from server.document import Document
from server.agents.summarizer import SummarizationAgent
from server.agents.usefull_classifier import UsefullClassificationAgent
from server.agents.text_embedding import TextEmbeddingAgent
import json

summarizer = SummarizationAgent()
usefull_classifier = UsefullClassificationAgent()


async def summarize_doc(node: Node, document: Document):
    _branch_text = ''

    # Find if Node contains something usefull
    usefullness = await usefull_classifier.aexecute(node.text)
    node._filter = not json.loads(usefullness)['useful']
    if not node._filter:
        # This is a direct summary of the node
        node.summary = await summarizer.aexecute(node.text)
        _branch_text += f"\n{node.summary}"

    for child in node.children:
        child_node = document.find_node(child)
        if child_node.branch_summary:
            _branch_text += f"\n{child_node.branch_summary}"

    if _branch_text != '':
        node.branch_summary = await summarizer.aexecute(_branch_text)


text_embedding = TextEmbeddingAgent()


async def embed_doc(node: Node, document: Document):
    if node.text:
        node.text_embedding = await text_embedding.aexecute(node.text)
    if node.summary:
        node.summary_embedding = await text_embedding.aexecute(node.summary)
    if node.branch_summary:
        node.branch_embedding = await text_embedding.aexecute(node.branch_summary)
