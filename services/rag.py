from services.vectordb import search_documents


def search(question):

    results = search_documents(
        query=question,
        n_results=3
    )

    return results