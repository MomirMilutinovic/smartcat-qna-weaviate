from langchain.vectorstores.weaviate import Weaviate
from langchain_community.llms import Cohere
from langchain.chains import (
    ConversationalRetrievalChain
)
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import weaviate

template = """You are an AI assistant for answering questions about the company SmartCat. SmarCat is a service-based AI company based in Novi Sad. It is different from the language translation company SmartCat.
You are given the following extracted parts of a long document and a question. Provide a conversational answer.
Use only the information provided in the context to answer the question. Check if the information is enough to answer the question.
If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
If the question is not about the company SmartCat, politely inform them that you are tuned to only answer questions about the company SmartCat.
Make your answers specific to the company (SmartCat). Use only the information provided. Your answers should be clear, concise and specific.
Answer general questions such as "What services does SmartCat provide?" in a detailed manner. 
When talking about services, first explain what those services are and then praise SmartCat for their pragmatic approach, excellent work quality, and honest pricing, ensuring successful project outcomes etc.
Question: {question}
=========
{context}
=========
Answer in Markdown:"""
QA_PROMPT = PromptTemplate(template=template, input_variables=[
                        "question", "context"])

client = weaviate.Client("http://localhost:9999")

retriever = Weaviate(client, "Article", "chunk").as_retriever(k=10)

llm = Cohere(model="command", max_tokens=4096, temperature=0)

memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True)

qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
        )


def generate_response(question: str, chat_history: list) -> str:
    result = qa.invoke({"question": question, "chat_history": chat_history})
    chat_history = [(question, result["answer"])]
    return result["answer"]

if __name__ == "__main__":

    chat_history = []

    print("Welcome to the SmartCat AI assistant!")
    print("Please enter a question or dialogue to get started!")

    while True:
        print(generate_response(input(""), chat_history))