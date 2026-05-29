import wikipediaapi
import io
import os
from RAG import query_RAG, chemin_corpus

def get_wikipedia_page(mots_cles):
    wiki = wikipediaapi.Wikipedia(
        language='fr',
        user_agent='MonAppRAG/1.0'
    )
    page = wiki.page(mots_cles)
    if not page.exists():
        print(f"[Wikipedia] Page non trouvée : {mots_cles}")
        return None
    print(f"[Wikipedia] Page trouvée : {page.title}")
    return page
    

def create_corpus(mots_cles, page):
    from corpus import add_corpus, add_documents_to_corpus

    nom_corpus = f"Wikipedia_{mots_cles.replace(' ', '_')}"
    add_corpus(nom_corpus)

    os.makedirs("tmp", exist_ok=True)

    for section in page.sections:
        if section.text.strip():
            chemin = os.path.join("tmp", section.title.replace(' ', '_') + ".txt")
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(section.text)

    for file in os.listdir("tmp"):
        file_path = os.path.join("tmp", file)
        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                uploaded_file = io.BytesIO(f.read())
            uploaded_file.name = file
            add_documents_to_corpus(nom_corpus, [uploaded_file])

    return nom_corpus


def wikipedia_query(mots_cles, user_input):
    nom_corpus = f"Wikipedia_{mots_cles.replace(' ', '_')}"
    corpus_path = os.path.join(chemin_corpus, nom_corpus)
    
    if not os.path.exists(corpus_path):
        page = get_wikipedia_page(mots_cles)
        if page:
            create_corpus(mots_cles, page)
        else:
            return ""
    
    return query_RAG(nom_corpus, user_input)


    




if __name__ == "__main__":
    page = get_wikipedia_page("ESEO")
    if page:
        nom = create_corpus("ESEO", page)
        print(f"Corpus créé : {nom}")

