from services.query_parser import answer_question, parse_question
from services.search_engine import search
from services.llm import generate_answer, generate_grounded_explanation
import services.data_facts as data_facts


def build_answer(item):

    metadata = item["metadata"]

    document = item["document"]

    dataset = metadata.get("dataset", "Dataset")

    response = []

    response.append(f"Berdasarkan dataset **{dataset}**, diperoleh informasi berikut:\n")

    response.append(document)

    if metadata.get("url"):

        response.append(f"\nSumber data: {metadata['url']}")

    return "\n".join(response)


def ask(question):

    parsed = parse_question(question)
    metric_token = data_facts._find_metric_token(parsed.get("keywords", []))

    answer_text, source_path = answer_question(question)

    if answer_text:
        explanation = generate_grounded_explanation(question, answer_text)
        if not explanation:
            explanation = (
                "Bagian detail di bawah menunjukkan baris data yang cocok dengan parameter "
                "pada pertanyaan Anda. Setiap bidang—indikator, wilayah, periode, dan nilai—"
                "hanya ditampilkan apabila tersedia pada hasil lookup dataset. Hasil ini "
                "bukan perbandingan antarwilayah, analisis penyebab, maupun proyeksi."
            )

        response = (
            "**Penjelasan berbasis dataset**\n"
            f"{explanation}\n\n"
            "**Jawaban dari dataset**\n"
            f"{answer_text}\n\n"
            "_Nilai di atas diambil langsung dari dataset yang tersedia; "
            "SADA-AI tidak menambahkan atau mengubah fakta statistik._"
        )
        if source_path:
            response += f"\n\n**Sumber dataset**\n{source_path}"
        return response

    # A recognized statistical metric must only be answered by the factual
    # CSV lookup above.  Semantic retrieval can return a row with the same
    # year/region from an unrelated dataset, so it is unsafe as a fallback.
    if metric_token is not None:
        period = ""
        if parsed.get("month") and parsed.get("year"):
            period = f" untuk {parsed['month'].capitalize()} {parsed['year']}"
        elif parsed.get("year"):
            period = f" untuk tahun {parsed['year']}"
        return f"Maaf, data {metric_token}{period} tidak ditemukan pada dataset yang tersedia."

    # Do not attempt dataset/semantic fallback for general knowledge questions
    if metric_token is None:
        return (
            "Maaf, saya hanya memberikan jawaban ketika pertanyaan berhubungan dengan data/statistik yang ada di dataset. "
            "Untuk pertanyaan umum (mis. 'siapa presiden'), coba mesin pencari atau ajukan pertanyaan terkait data."
        )

    results = search(question)

    if len(results) == 0:

        return (
            "Maaf, saya tidak menemukan data yang sesuai "
            "dengan pertanyaan Anda."
        )

    answer = generate_answer(question, results[:3])

    if answer:

        return answer

    best_result = results[0]

    return build_answer(best_result)
