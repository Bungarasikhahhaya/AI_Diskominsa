from fastapi import APIRouter

from pydantic import BaseModel

from services.chatbot import ask

router=APIRouter()

class ChatRequest(BaseModel):

    question:str

@router.post("/chat")

def chat(req:ChatRequest):

    answer=ask(req.question)

    return{

        "answer":answer

    }