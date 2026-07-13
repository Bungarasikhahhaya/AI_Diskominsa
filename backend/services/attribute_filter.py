"""
Attribute Filter

Memfilter hasil retrieval berdasarkan metadata
yang dimiliki setiap dokumen.
"""


# =====================================================
# Fungsi utilitas
# =====================================================

def contains_ignore_case(value, keyword):
    """
    Membandingkan string tanpa memperhatikan huruf besar/kecil.
    """

    if keyword is None:
        return True

    if value is None:
        return False

    return keyword.lower() in str(value).lower()


# =====================================================
# Mencari nilai metadata
# =====================================================

def get_metadata_value(metadata, possible_keys):
    """
    Mengambil nilai metadata berdasarkan beberapa kemungkinan nama kolom.
    """

    for key in possible_keys:

        if key in metadata:

            return metadata[key]

    return None


# =====================================================
# Filter Region
# =====================================================

def filter_region(results, region):

    if region is None:
        return results

    region_fields = [

        "region",
        "kabupaten",
        "kabupaten_kota",
        "nama_kabupaten",
        "nama_kabupaten_kota",
        "kota",
        "wilayah",
        "bps_nama_kabupaten_kota",
        "kemendagri_nama_kabupaten_kota",
        "bps_nama_provinsi",
        "kemendagri_nama_provinsi",
        "provinsi"

    ]

    filtered = []

    for item in results:

        metadata = item.get("metadata", {})

        value = get_metadata_value(
            metadata,
            region_fields
        )

        if contains_ignore_case(value, region):

            filtered.append(item)

    return filtered


# =====================================================
# Filter Tahun
# =====================================================

def filter_year(results, year):

    if year is None:
        return results

    filtered = []

    for item in results:

        metadata = item.get("metadata", {})

        value = metadata.get("tahun")

        if contains_ignore_case(value, year):

            filtered.append(item)

    return filtered


# =====================================================
# Filter Keyword
# =====================================================

def filter_keywords(results, keywords):

    if len(keywords) == 0:
        return results

    filtered = []

    for item in results:

        text = item["document"].lower()

        metadata = item.get("metadata", {})

        score = 0

        # ==============================
        # Keyword pada dokumen
        # ==============================

        for keyword in keywords:

            if keyword.lower() in text:

                score += 5

        # ==============================
        # Keyword pada metadata
        # ==============================

        for value in metadata.values():

            value = str(value).lower()

            for keyword in keywords:

                if keyword.lower() in value:

                    score += 2

        item["keyword_score"] = score

        filtered.append(item)

    filtered.sort(

        key=lambda x: x["keyword_score"],

        reverse=True

    )

    return filtered


# =====================================================
# Filter Utama
# =====================================================

def apply_filters(results, parsed_query):

    # ===========================
    # Filter Region
    # ===========================

    results = filter_region(

        results,

        parsed_query.get("region")

    )

    # ===========================
    # Filter Tahun
    # ===========================

    results = filter_year(

        results,

        parsed_query.get("year")

    )

    # ===========================
    # Filter Keyword
    # ===========================

    results = filter_keywords(

        results,

        parsed_query.get("keywords", [])

    )

    return results