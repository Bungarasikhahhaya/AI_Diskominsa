import os

from config import GOOGLE_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

MODEL_NAME = "gemini-3.1-pro-preview"


def _build_system_prompt():
    return (
        "Kamu adalah asisten data statistik Aceh. "
        "Beri jawaban singkat, akurat, dan gunakan hanya informasi yang ada di konteks. "
        "Tuliskan sumber dataset jika tersedia. "
        "Jika data tidak ada, katakan bahwa informasi tidak ditemukan."
    )


def _build_user_prompt(question, results):
    prompt_parts = [
        f"Pertanyaan: {question}",
        "Berikut adalah data relevan dari dataset:",
    ]
    for idx, item in enumerate(results, start=1):
        metadata = item.get("metadata", {})
        dataset = metadata.get("dataset", "Dataset")
        url = metadata.get("url") or metadata.get("source") or ""
        source = f"Sumber: {url}" if url else "Sumber: tidak tersedia"
        prompt_parts.append(
            f"[{idx}] {dataset}\n{item.get('document', '').strip()}\n{source}"
        )
    prompt_parts.append(
        "Jawab pertanyaan menggunakan data di atas. Jika jawaban hanya bisa diberikan sebagai data numerik, sebutkan nilai dan sumber datasetnya."
    )
    return "\n\n".join(prompt_parts)


def create_chat_model():
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY tidak ditemukan. Set environment variable atau .env sebelum menggunakan LLM."
        )

    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        api_key=GOOGLE_API_KEY,
        temperature=0.2,
        top_p=0.95,
        max_tokens=512,
    )


def generate_answer(question, results):
    if len(results) == 0:
        return None

    try:
        llm = create_chat_model()
        system_message = SystemMessage(content=_build_system_prompt())
        user_message = HumanMessage(content=_build_user_prompt(question, results))

        response = llm.generate([[system_message, user_message]])

        generations = getattr(response, "generations", None)
        if not generations:
            return None

        first = generations[0][0]
        return getattr(first, "text", None) or str(first)
    except Exception as exc:
        # Jika model LLM gagal karena kuota atau kesalahan lain,
        # kembalikan None agar chatbot fallback ke jawaban default.
        print("LLM generate_answer error:", repr(exc))
        return None


def generate_factual_intro(question):
    """Generate a short natural-language introduction for a verified fact.

    The numeric value, period, and source are rendered by application code,
    not by the model.  This keeps the response conversational without giving
    the model an opportunity to change the retrieved fact.
    """
    try:
        llm = create_chat_model()
        system_message = SystemMessage(content=(
            "Kamu adalah asisten data statistik Aceh. Buat penjelasan singkat "
            "dalam Bahasa Indonesia untuk jawaban data yang sudah diverifikasi. "
            "Gunakan tepat dua kalimat: kalimat pertama mengaitkan hasil dengan "
            "pertanyaan pengguna, dan kalimat kedua menjelaskan secara sederhana "
            "kegunaan atau makna indikatornya. Bersikap ramah dan profesional. Jangan "
            "menulis angka, tahun, tanggal, nilai, satuan, tautan, atau sumber; "
            "semua fakta tersebut akan ditampilkan oleh sistem. Jangan membuat "
            "klaim tambahan yang tidak ada pada pertanyaan."
        ))
        user_message = HumanMessage(content=f"Pertanyaan pengguna: {question}")
        response = llm.generate([[system_message, user_message]])
        generations = getattr(response, "generations", None)
        if not generations:
            return None
        intro = getattr(generations[0][0], "text", None)
        if not intro:
            return None
        intro = intro.strip()
        # Do not display model output that may accidentally restate or alter a
        # verified number; the application renders factual values itself.
        if re.search(r"\d|https?://", intro, re.IGNORECASE):
            return None
        return intro
    except Exception as exc:
        print("LLM generate_factual_intro error:", repr(exc))
        return None
