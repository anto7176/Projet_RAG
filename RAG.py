from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
import os
import streamlit as st

# configuration des dossiers temporaires et du chemin des corpus
os.environ["TMPDIR"] = r"D:\Antoine_Vadot\Projet_RAG\tmp"
os.environ["TEMP"] = r"D:\Antoine_Vadot\Projet_RAG\tmp"
os.environ["TMP"] = r"D:\Antoine_Vadot\Projet_RAG\tmp"

chemin_corpus = r"D:\Antoine_Vadot\Projet_RAG\corpus"

EMBEDDING_MODEL = "nomic-embed-text"


def ingest_documents(nom_corpus, list_doc):
    # connexion à la base ChromaDB du corpus
    chroma_path = os.path.join(chemin_corpus, nom_corpus, "chroma_db")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    db = Chroma(
        persist_directory=chroma_path,
        embedding_function=embeddings
    )

    # découpage en chunks avec overlap
    # chunk_size : taille d'un chunk en caractères
    # chunk_overlap : chevauchement entre les chunks
    # si le modèle répond à côté → augmenter chunk_size
    # si le modèle dépasse sa fenêtre de contexte → diminuer chunk_size 
    # si le modèle répète des infos → diminuer chunk_overlap
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    for nom_doc in list_doc:
        doc_path = os.path.join(chemin_corpus, nom_corpus, nom_doc)
        extension = os.path.splitext(nom_doc)[1].lower()

        if extension == ".pdf":
            # chargement du PDF page par page
            loader = PyPDFLoader(doc_path)
            docs = loader.load()
            for d in docs:
                d.metadata["source"] = nom_doc
        else:
            # lecture du fichier texte avec fallback latin-1
            try:
                with open(doc_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(doc_path, "r", encoding="latin-1") as f:
                    content = f.read()
            docs = [Document(page_content=content, metadata={"source": nom_doc})]

        # indexation des chunks dans ChromaDB
        chunks = splitter.split_documents(docs)
        db.add_documents(chunks)
        print(f"[ingest] {nom_doc} → {len(chunks)} chunks indexés")


def purge_document(nom_corpus, nom_doc):
    # connexion à la base ChromaDB du corpus
    chroma_path = os.path.join(chemin_corpus, nom_corpus, "chroma_db")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    db = Chroma(persist_directory=chroma_path, embedding_function=embeddings)

    # récupération des ids des chunks du document puis suppression
    results = db.get(where={"source": nom_doc})
    ids = results.get("ids", [])
    if ids:
        db.delete(ids=ids)
        print(f"[purge] {nom_doc} → {len(ids)} chunks supprimés")


def query_RAG(nom_corpus, user_input):
    # connexion à la base ChromaDB du corpus
    chroma_path = os.path.join(chemin_corpus, nom_corpus, "chroma_db")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    db = Chroma(persist_directory=chroma_path, embedding_function=embeddings)

    # recherche des 3 chunks les plus proches de la question
    # k : nombre de chunks envoyés au modèle
    # si pas assez d'infos → augmenter k 
    # si contexte trop long → diminuer k
    chunks = db.similarity_search(user_input, k=3)

    # construction du contexte avec la source et le contenu de chaque chunk
    contexte = ""
    for chunk in chunks:
        contexte += f"<source>{chunk.metadata['source']}</source>\n"
        contexte += f"<contenu>{chunk.page_content}</contenu>\n\n"

    return contexte