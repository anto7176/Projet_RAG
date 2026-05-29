from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import os
import pdfplumber
import pandas as pd

os.environ["TMPDIR"] = r"D:\Antoine_Vadot\Projet_RAG\tmp"
os.environ["TEMP"] = r"D:\Antoine_Vadot\Projet_RAG\tmp"
os.environ["TMP"] = r"D:\Antoine_Vadot\Projet_RAG\tmp"

chemin_corpus = r"D:\Antoine_Vadot\Projet_RAG\corpus"
EMBEDDING_MODEL = "nomic-embed-text"


def _read_file(doc_path):
    ext = os.path.splitext(doc_path)[1].lower()
    if ext == ".pdf":
        with pdfplumber.open(doc_path) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(doc_path)
        return df.to_string()
    elif ext == ".csv":
        df = pd.read_csv(doc_path)
        return df.to_string()
    else:
        try:
            with open(doc_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            with open(doc_path, "r", encoding="latin-1") as f:
                return f.read()


def ingest_documents(nom_corpus, list_doc):
    chroma_path = os.path.join(chemin_corpus, nom_corpus, "chroma_db")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    db = Chroma(persist_directory=chroma_path, embedding_function=embeddings)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    for nom_doc in list_doc:
        doc_path = os.path.join(chemin_corpus, nom_corpus, nom_doc)
        content = _read_file(doc_path)
        doc = Document(page_content=content, metadata={"source": nom_doc})
        chunks = splitter.split_documents([doc])
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

    return contexte