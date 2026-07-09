from services.query_parser import answer_question, parse_question
from services.search_engine import search
from services.llm import generate_answer
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
        response = (
            f"Berdasarkan hasil pencarian langsung di dataset, jawabannya adalah: {answer_text}"
        )
        if source_path:
            response += f"\nSumber data: {source_path}"
        return response

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