import os
import shutil
from RAG import ingest_documents, purge_document

chemin_corpus = r"D:\Antoine_Vadot\Projet_RAG\corpus"

def add_corpus(nom):
    return os.makedirs(os.path.join(chemin_corpus, nom), exist_ok=True)


def get_corpus_list():
    liste = ["Aucun"]
    liste += [d for d in os.listdir(chemin_corpus)
              if os.path.isdir(os.path.join(chemin_corpus, d))]
    return liste


def add_documents_to_corpus(nom_corpus, uploaded_files):
    dest = os.path.join(chemin_corpus, nom_corpus)
    os.makedirs(dest, exist_ok=True)

    saved_names = []
    for doc in uploaded_files:
        dest_path = os.path.join(dest, doc.name)
        with open(dest_path, "wb") as f:
            f.write(doc.read())
        saved_names.append(doc.name)

    ingest_documents(nom_corpus, saved_names)         # doc.read() = contenu binaire


def get_documents_from_corpus(corpus):
    corpus_path = os.path.join(chemin_corpus, corpus)
    return [f for f in os.listdir(corpus_path)
        if os.path.isfile(os.path.join(corpus_path, f))]


def delete_document_from_corpus(nom_corpus, nom_document):
    purge_document(nom_corpus, nom_document) 
    corpus_path = os.path.join(chemin_corpus, nom_corpus, nom_document)
    os.remove(corpus_path)

def delete_corpus(nom_corpus):
    corpus_path = os.path.join(chemin_corpus, nom_corpus)
    shutil.rmtree(corpus_path)


if __name__ == "__main__":
    add_corpus("test")
