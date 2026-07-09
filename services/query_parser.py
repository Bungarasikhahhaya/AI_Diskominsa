"""
Query Parser

Mengekstrak informasi penting dari pertanyaan pengguna.
"""

import re
from . import data_facts

# =====================================
# Daftar Kabupaten/Kota Aceh
# =====================================

ACEH_REGIONS = [

    "Aceh Barat",
    "Aceh Barat Daya",
    "Aceh Besar",
    "Aceh Jaya",
    "Aceh Selatan",
    "Aceh Singkil",
    "Aceh Tamiang",
    "Aceh Tengah",
    "Aceh Tenggara",
    "Aceh Timur",
    "Aceh Utara",

    "Bener Meriah",
    "Bireuen",
    "Gayo Lues",
    "Nagan Raya",
    "Pidie",
    "Pidie Jaya",
    "Simeulue",

    "Banda Aceh",
    "Langsa",
    "Lhokseumawe",
    "Sabang",
    "Subulussalam"
]

# =====================================
# Stopwords
# =====================================

STOPWORDS = {

    "berapa",
    "apa",
    "adalah",
    "jumlah",
    "data",
    "yang",
    "di",
    "ke",
    "dari",
    "untuk",
    "pada",
    "tahun",
    "kabupaten",
    "kota",
    "provinsi",
    "aceh",
    "menurut"
}


# =====================================
# Cari Kabupaten/Kota
# =====================================

def extract_region(question):

    q = question.lower()

    for region in ACEH_REGIONS:

        if region.lower() in q:

            return region

    return None


# =====================================
# Cari Tahun
# =====================================

def extract_year(question):

    match = re.search(r"\b(20\d{2})\b", question)

    if match:

        return match.group(1)

    return None


# =====================================
# Ambil Keyword
# =====================================

SYNONYM_MAP = {
    "disabilitas": "cacat",
    "penyandang": "cacat",
}


def extract_keywords(question):

    words = re.findall(r"\w+", question.lower())

    keywords = []

    for word in words:

        if word not in STOPWORDS:

            keywords.append(SYNONYM_MAP.get(word, word))

    return keywords


# =====================================
# Parse Question
# =====================================

def parse_question(question):

    result = {

        "region": extract_region(question),

        "year": extract_year(question),

        "keywords": extract_keywords(question)

    }

    return result


def answer_question(question):
    """Attempt to produce a short factual answer with source link.

    Returns a tuple (answer_text, source_path) or (None, None) when no fact found.
    """
    parsed = parse_question(question)
    # First try domain-specific fast facts
    ans, src = data_facts.answer(question, parsed.get("region"), parsed.get("year"))
    if ans:
        return ans, src

    # fallback: no direct fact found
    return None, None