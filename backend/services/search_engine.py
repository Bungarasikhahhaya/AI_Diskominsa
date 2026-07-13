"""
Search Engine

Melakukan pencarian menggunakan:
1. Semantic Search (ChromaDB)
2. Metadata Filtering
3. Keyword Re-ranking
"""

import re

from services.vectordb import search_documents
from services.query_parser import parse_question
from services.attribute_filter import apply_filters


# =====================================================
# Stopwords
# =====================================================

STOPWORDS = {
    "berapa",
    "apa",
    "siapa",
    "dimana",
    "yang",
    "dan",
    "atau",
    "di",
    "ke",
    "dari",
    "adalah",
    "data",
    "tahun",
    "pada",
    "untuk",
    "dengan",
    "menurut",
    "kabupaten",
    "kota",
    "provinsi",
    "ada",
    "terdapat",
    "jumlah"
}


# =====================================================
# Keyword Extraction
# =====================================================

def extract_keywords(question):

    words = re.findall(r"\w+", question.lower())

    keywords = []

    for word in words:

        if word in STOPWORDS:
            continue

        if len(word) <= 2:
            continue

        keywords.append(word)

    return keywords


# =====================================================
# Hitung Keyword Score
# =====================================================

def keyword_score(text, keywords):

    score = 0

    text = text.lower()

    for keyword in keywords:

        if keyword in text:
            score += 10

    return score


# =====================================================
# Bonus Metadata Score
# =====================================================

def metadata_score(metadata, parsed_query):

    score = 0

    region = parsed_query.get("region")
    year = parsed_query.get("year")

    if region:

        if metadata.get("region", "").lower() == region.lower():
            score += 50

    if year:

        if metadata.get("tahun", "") == year:
            score += 30

    return score


# =====================================================
# Total Score
# =====================================================

def calculate_score(document, metadata, distance, keywords, parsed_query):

    score = 0

    # Semantic similarity
    score += (1 - distance) * 100

    # Keyword match
    score += keyword_score(document, keywords)

    # Metadata bonus
    score += metadata_score(metadata, parsed_query)

    return score


# =====================================================
# Search
# =====================================================

def search(question):

    parsed_query = parse_question(question)

    print("=" * 70)
    print("Parsed Query")
    print(parsed_query)
    print("=" * 70)

    result = search_documents(
        query=question,
        n_results=50
    )

    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]

    keywords = extract_keywords(question)

    ranked = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        score = calculate_score(
            document=document,
            metadata=metadata,
            distance=distance,
            keywords=keywords,
            parsed_query=parsed_query
        )

        ranked.append({

            "score": score,

            "distance": distance,

            "document": document,

            "metadata": metadata

        })

    ranked = apply_filters(
        ranked,
        parsed_query
    )

    ranked.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked