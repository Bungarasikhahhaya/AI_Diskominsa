import os
import re

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


def generate_grounded_explanation(question, verified_fact):
    """Explain a verified lookup without allowing the LLM to add new facts.

    ``verified_fact`` is the exact result returned by the CSV lookup. It is
    the sole factual context supplied to the model. The output is discarded
    when it contains a number not present in that result or an unsupported
    interpretation; the application will then use its deterministic fallback.
    """
    try:
        llm = create_chat_model()
        system_message = SystemMessage(content=(
            "Kamu adalah asisten penjelas data statistik Aceh. Jawab dalam Bahasa "
            "Indonesia yang jelas, profesional, dan mudah dipahami. Gunakan HANYA "
            "fakta pada bagian FAKTA TERVERIFIKASI. Buat 1 sampai 2 paragraf pendek "
            "yang menjelaskan jawaban untuk pertanyaan pengguna. Jelaskan hubungan "
            "antara indikator, wilayah, periode, dan nilai HANYA jika bidang tersebut "
            "ada pada fakta. Akhiri dengan batasan singkat bahwa hasil adalah satu "
            "lookup data dan bukan perbandingan, analisis penyebab, atau proyeksi. "
            "Kamu boleh mengulang nilai hanya persis seperti pada fakta. Jangan menambah angka, periode, wilayah, "
            "definisi, perbandingan, sebab-akibat, tren, atau kesimpulan baru. "
            "Jangan menulis tautan atau menyebut sumber di luar fakta. Jika faktanya "
            "hanya satu nilai, katakan secara eksplisit bahwa data tersebut adalah "
            "hasil lookup yang tersedia, bukan proyeksi atau perbandingan."
        ))
        user_message = HumanMessage(content=(
            f"PERTANYAAN PENGGUNA:\n{question}\n\n"
            f"FAKTA TERVERIFIKASI (satu-satunya sumber):\n{verified_fact}"
        ))
        response = llm.generate([[system_message, user_message]])
        generations = getattr(response, "generations", None)
        if not generations:
            return None
        explanation = getattr(generations[0][0], "text", None)
        if not explanation:
            return None
        explanation = explanation.strip()
        if len(explanation) > 1400 or re.search(r"https?://|www\.", explanation, re.IGNORECASE):
            return None

        # Any figures in the prose must already occur in the verified lookup.
        fact_numbers = set(re.findall(r"\d+(?:[.,]\d+)*", verified_fact))
        answer_numbers = set(re.findall(r"\d+(?:[.,]\d+)*", explanation))
        if not answer_numbers.issubset(fact_numbers):
            return None

        # Interpretive claims are only permitted when the exact fact itself
        # contains that wording (for example, an explicitly retrieved trend).
        for term in ("meningkat", "menurun", "tertinggi", "terendah", "dibandingkan", "diperkirakan", "penyebab"):
            if term in explanation.lower() and term not in verified_fact.lower():
                return None
        return explanation
    except Exception as exc:
        print("LLM generate_grounded_explanation error:", repr(exc))
        return None
