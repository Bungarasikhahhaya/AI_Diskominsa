from services.query_parser import parse_query
from services.vectordb import search_documents
from services.attribute_filter import apply_filters
from services.search_engine import rerank_results


def search(question):

    # ==========================
    # Parsing Query
    # ==========================

    parsed_query = parse_query(question)

    # ==========================
    # Retrieval Chroma
    # ==========================

    result = search_documents(
        question,
        n_results=30
    )

    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]

    results = []

    for doc, meta, distance in zip(
        documents,
        metadatas,
        distances
    ):

        results.append({

            "document": doc,

            "metadata": meta,

            "distance": distance

        })

    # ==========================
    # Filter Kabupaten/Tahun
    # ==========================

    results = apply_filters(
        results,
        parsed_query
    )

    # ==========================
    # Reranking
    # ==========================

    results = rerank_results(
        results,
        question
    )

    return results