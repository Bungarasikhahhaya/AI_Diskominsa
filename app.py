from fastapi import FastAPI

from routes.chat import router

app=FastAPI(
    title="AI Chatbot Statistik Aceh"
)

app.include_router(router)