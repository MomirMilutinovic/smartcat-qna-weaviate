from langchain.vectorstores.weaviate import Weaviate
from langchain_community.llms import Cohere
from langchain.chains import (
    ConversationalRetrievalChain
)
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import JSONLoader
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
import weaviate
import json


template = """You are an AI assistant for answering questions about the company SmartCat. SmarCat is a service-based AI company based in Novi Sad. It is different from the language translation company SmartCat.
You are given the following extracted parts of pages across the company's website and a question. Provide a conversational answer.
Use only the information provided in the context to answer the question. Check if the information is enough to answer the question.
Answer only with information relevant to the question.
If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
If the question is not about the company SmartCat, politely inform them that you are tuned to only answer questions about the company SmartCat.
Make your answers specific to the company (SmartCat). Use only the information provided. Your answers should be clear, concise and specific.
Answer general questions such as "What services does SmartCat provide?" in a detailed manner. 
When talking about services, first explain in detail what those services are, before talking about other things.
When asked about a specific open job position, provide a detailed answer that includes a high level description, the requirements, technology stack, and benefits, in that order.
When asked about all job positions, provide a list of all open job positions and do not go into the details of each job position.
At the end of each answer, tell the user that it's best to verify the most up-to-date information on SmartCat's official website.
Question: {question}
=========
{context}
=========
Answer in Markdown:"""
QA_PROMPT = PromptTemplate(template=template, input_variables=[
                        "question", "context"])

with open('articles.json') as f:
    document_ids = [document['doc_id'] for document in json.load(f)]

loader = JSONLoader(
    file_path='articles.json',
    jq_schema='.[].text',
    text_content=False)

docs = loader.load()

client = weaviate.Client("http://localhost:9999")

vectorstore = Weaviate(client, "Article", "chunk", attributes=["doc_id"])

store = InMemoryStore()
store.mset([(document_ids[i], docs[i]) for i in range(len(docs))])

placholder_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=placholder_splitter,
)

llm = Cohere(model="command", max_tokens=4096, temperature=0)

memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True)

qa = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    combine_docs_chain_kwargs={"prompt": QA_PROMPT}
)


def generate_response(question: str, chat_history: list) -> str:
    """
    Queries the vector store for the most relevant chunks of pages and
    generates a response using a LLM.
    :param question: The question to be answered.
    :param chat_history: The chat history.
    :return: The response to the question.
    """
    result = qa.invoke({"question": question, "chat_history": chat_history})
    chat_history = [(question, result["answer"])]
    return result["answer"]

def reset_memory():
    """
    Resets the memory of the LLM.
    """
    memory.clear()

if __name__ == "__main__":

    chat_history = []

    print("Welcome to the SmartCat AI assistant!")
    print("Please enter a question or dialogue to get started!")

    while True:
        print(generate_response(input(""), chat_history))