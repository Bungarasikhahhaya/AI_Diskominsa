from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY
from services.rag import search

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY
)


def ask(question):

    results = search(question)

    documents = results.get("documents", [[]])

    if not documents or not documents[0]:
        return "Maaf, saya tidak menemukan data yang sesuai."

    context = "\n\n".join(documents[0])

    prompt = f"""
Anda adalah AI Chatbot Satu Data Aceh.

Gunakan HANYA informasi yang terdapat pada konteks berikut untuk menjawab pertanyaan.

Jika jawabannya tidak ada pada konteks, jawab:

"Maaf, data yang diminta tidak tersedia pada database."

=====================
KONTEKS

{context}

=====================

Pertanyaan:
{question}
"""

    response = llm.invoke(prompt)

    return response.content