# api.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
from dotenv import load_dotenv
from src.chat_model import ChatModel
from src.db_handler import QdrantDBHandler
from langchain_core.prompts import PromptTemplate
from utils.logger import logging

load_dotenv()

app = FastAPI()

class QueryRequest(BaseModel):
    user_query: str

def query_rag_system(query: str):
    qdrant = QdrantDBHandler()
    docs = qdrant.search(query_text=query)
    logging.info("Retrieved Documents:")
    for doc in docs:
        logging.info(f"Doc: {doc}")
    return docs

@app.post("/query")
async def query_response(req: QueryRequest):
    user_query = req.user_query
    retrieved_data = query_rag_system(user_query)

    message_prompt = PromptTemplate.from_template(
        """
        You are an helpful AI assistant
        Answer the following question: {user_query}
        Use the following information to answer: {retrieved_data}
        Remember to include the source in your answer at the very end and hyperlink it. I mean the link to where user can explore more or where you got the answer from.
        If you do not find answer, say 'You do not have the answer, politely". Do not hallucinate or make up answers.
        Make the answer short and crisp
        """
    )

    chat_model = ChatModel()
    message_chain = message_prompt | chat_model.groq

    response = message_chain.invoke(
        input={"user_query": user_query, "retrieved_data": retrieved_data}
    )

    return {"response": response.content}
