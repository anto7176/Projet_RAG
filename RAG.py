from msilib.schema import Error
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import os
import tempfile
import os
import streamlit as st
    
    
os.environ["TMPDIR"] = r"D:\Antoine_Vadot\Projet_RAG\tmp"
os.environ["TEMP"] = r"D:\Antoine_Vadot\Projet_RAG\tmp"
os.environ["TMP"] = r"D:\Antoine_Vadot\Projet_RAG\tmp"

chemin_corpus = r"D:\Antoine_Vadot\Projet_RAG\corpus"

EMBEDDING_MODEL = "nomic-embed-text"

def ingest_documents(nom_corpus,list_doc):



    chroma_path = os.path.join(chemin_corpus, nom_corpus, "chroma_db")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    db = Chroma(
        persist_directory=chroma_path,
        embedding_function=embeddings
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )



    for nom_doc in list_doc:
        doc_path = os.path.join(chemin_corpus, nom_corpus, nom_doc)

        try:
            with open(doc_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            raise RuntimeError("HERE RAG.py ingest.py")
            # with open(doc_path, "r", encoding=b"latin-1") as f:
                # content = f.read()

        # Création du Document 
        doc = Document(
            page_content=content,
            metadata={"source": nom_doc}
        )

        # Découpage en chunks
        chunks = splitter.split_documents([doc])

        # Ajout à ChromaDB
        db.add_documents(chunks)
        print(f"[ingest] {nom_doc} → {len(chunks)} chunks indexés")


def purge_document(nom_corpus, nom_doc):
    chroma_path = os.path.join(chemin_corpus, nom_corpus, "chroma_db")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    db = Chroma(persist_directory=chroma_path, embedding_function=embeddings)

    results = db.get(where={"source": nom_doc})
    ids = results.get("ids", [])

    if ids:
        db.delete(ids=ids)
        print(f"[purge] {nom_doc} → {len(ids)} chunks supprimés")




def query_RAG(nom_corpus, user_input):
    chroma_path = os.path.join(chemin_corpus, nom_corpus, "chroma_db")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    db = Chroma(persist_directory=chroma_path, embedding_function=embeddings)

    chunks = db.similarity_search(user_input, k=3)

    contexte = ""
    for chunk in chunks:
        contexte += f"<source>{chunk.metadata['source']}</source>\n"
        contexte += f"<contenu>{chunk.page_content}</contenu>\n\n"

    st.write(contexte)
    return contexte