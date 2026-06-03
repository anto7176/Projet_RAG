import os
import shutil
import streamlit as st
from RAG import ingest_documents, purge_document, chemin_corpus


# création du dossier du corpus
def add_corpus(nom):
    if nom in get_corpus_list():
        return
    os.makedirs(os.path.join(chemin_corpus, nom), exist_ok=True)

# récupération de tous les dossiers du répertoire corpus
def get_corpus_list():
    liste = ["Aucun"]
    liste += [d for d in os.listdir(chemin_corpus)
              if os.path.isdir(os.path.join(chemin_corpus, d))]
    return liste


def add_documents_to_corpus(nom_corpus, uploaded_files):
    dest = os.path.join(chemin_corpus, nom_corpus)
    os.makedirs(dest, exist_ok=True)

    # sauvegarde du fichier dans le dossier du corpus
    saved_names = []
    for doc in uploaded_files:
        content = doc.read()
        dest_path = os.path.join(dest, doc.name)
        with open(dest_path, "wb") as f:
            f.write(content)
        saved_names.append(doc.name)

    # indexation des documents dans ChromaDB
    ingest_documents(nom_corpus, saved_names)


# récupération des fichiers uniquement, pas les sous-dossiers
def get_documents_from_corpus(corpus):
    corpus_path = os.path.join(chemin_corpus, corpus)
    return [f for f in os.listdir(corpus_path)
            if os.path.isfile(os.path.join(corpus_path, f))]

# suppression des chunks dans ChromaDB puis du fichier
def delete_document_from_corpus(nom_corpus, nom_document):
    purge_document(nom_corpus, nom_document)
    corpus_path = os.path.join(chemin_corpus, nom_corpus, nom_document)
    os.remove(corpus_path)

 # suppression de chaque document un par un puis du dossier
def delete_corpus(nom_corpus):
    for doc in get_documents_from_corpus(nom_corpus):
        delete_document_from_corpus(nom_corpus, doc)
    os.rmdir(os.path.join(chemin_corpus, nom_corpus))


if __name__ == "__main__":
    add_corpus("test")