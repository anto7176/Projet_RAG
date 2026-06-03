import wikipediaapi
import io
import os
import uuid
import shutil


from corpus import add_corpus, add_documents_to_corpus
from RAG import query_RAG, chemin_corpus

# récupération de la page Wikipedia
def get_wikipedia_page(mots_cles):
    wiki = wikipediaapi.Wikipedia(language='fr', user_agent='MonAppRAG/1.0')
    page = wiki.page(mots_cles)
    if not page.exists():
        results = wiki._query({
            "action": "query", "list": "search",
            "srsearch": mots_cles, "srlimit": 1
        })
        hits = results.get("query", {}).get("search", [])
        if hits:
            page = wiki.page(hits[0]["title"])
    if not page.exists():
        print(f"[Wikipedia] Page non trouvée : {mots_cles}")
        return None
    print(f"[Wikipedia] Page trouvée : {page.title}")
    return page

# récupération de toutes les sections de la page
def recursive_sections_check(page_or_section):
    result = []
    for section in page_or_section.sections:
        result.append(section)
        result.extend(recursive_sections_check(section))
    return result

# création du corpus Wikipedia
def create_corpus(mots_cles, page):
    
    nom_corpus = f"Wikipedia_{mots_cles.replace(' ', '_')}"
    add_corpus(nom_corpus)

    tmp_dir = os.path.join(r"D:\Antoine_Vadot\Projet_RAG\tmp", str(uuid.uuid4()))
    os.makedirs(tmp_dir, exist_ok=True)

    # création d'un fichier txt par section et ajout au corpus
    all_sections = recursive_sections_check(page)
    for section in all_sections:
        if not section.text:
            continue
        
        chemin = os.path.join(tmp_dir, section.title + ".txt")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(section.text)

        with open(chemin, "rb") as f:
            uploaded_file = io.BytesIO(f.read())
        uploaded_file.name = section.title + ".txt"
        add_documents_to_corpus(nom_corpus, [uploaded_file])

    # suppression du dossier temporaire
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return nom_corpus


# si le corpus n'existe pas encore on le crée
def wikipedia_query(mots_cles, user_input):
    nom_corpus = f"Wikipedia_{mots_cles.replace(' ', '_')}"
    corpus_path = os.path.join(chemin_corpus, nom_corpus)
    chroma_path = os.path.join(corpus_path, "chroma_db")

    if not os.path.exists(chroma_path):
        page = get_wikipedia_page(mots_cles)
        if page:
            create_corpus(mots_cles, page)
        else:
            return ""
            
    # requête RAG sur le corpus Wikipedia
    return query_RAG(nom_corpus, user_input)


if __name__ == "__main__":
    page = get_wikipedia_page("ESEO")
    if page:
        nom = create_corpus("ESEO", page)
        print(f"Corpus créé : {nom}")