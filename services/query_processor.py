import re

# ==========================================
# Daftar wilayah Aceh
# ==========================================

REGIONS = [
    "aceh barat",
    "aceh barat daya",
    "aceh besar",
    "aceh jaya",
    "aceh selatan",
    "aceh singkil",
    "aceh tamiang",
    "aceh tengah",
    "aceh tenggara",
    "aceh timur",
    "aceh utara",
    "bener meriah",
    "bireuen",
    "gayo lues",
    "nagan raya",
    "pidie",
    "pidie jaya",
    "simeulue",
    "langsa",
    "lhokseumawe",
    "banda aceh",
    "sabang",
    "subulussalam"
]


# ==========================================
# Normalisasi pertanyaan
# ==========================================

def normalize_question(question: str):
    """
    Membersihkan pertanyaan pengguna.
    """

    question = question.lower()

    question = re.sub(r"[^\w\s]", " ", question)

    question = re.sub(r"\s+", " ", question)

    return question.strip()


# ==========================================
# Ekstrak tahun
# ==========================================

def extract_year(question):

    match = re.search(r"(20\d{2})", question)

    if match:
        return match.group(1)

    return None


# ==========================================
# Ekstrak kabupaten/kota
# ==========================================

def extract_region(question):

    question = question.lower()

    for region in REGIONS:

        if region in question:
            return region.title()

    return None


# ==========================================
# Ekstrak keyword
# ==========================================

STOPWORDS = {

    "berapa",
    "berapa banyak",
    "jumlah",
    "data",
    "di",
    "kabupaten",
    "kota",
    "tahun",
    "ada",
    "yang",
    "untuk",
    "dengan",
    "pada",
    "provinsi",
    "aceh"

}


def extract_keywords(question):

    words = normalize_question(question).split()

    keywords = []

    for word in words:

        if word in STOPWORDS:
            continue

        if len(word) <= 2:
            continue

        keywords.append(word)

    return keywords


# ==========================================
# Parse Query
# ==========================================

def parse_query(question):

    question = normalize_question(question)

    return {

        "original": question,

        "region": extract_region(question),

        "year": extract_year(question),

        "keywords": extract_keywords(question)

    }