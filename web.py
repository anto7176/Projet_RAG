from ddgs import DDGS 
import httpx
from bs4 import BeautifulSoup
import ollama
import streamlit as st


def get_URL(mots_cles, max_results=3):
    urls = []
    with DDGS() as ddgs:
        results = ddgs.text(mots_cles, max_results=max_results)
        for r in results:
            urls.append(r["href"])
    return urls

def get_page_content(url, max_chars=4000):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = httpx.get(url, headers=headers, timeout=10, follow_redirects=True)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "nav", "header", "footer"]):
                tag.decompose()
            texte = soup.get_text(separator=" ", strip=True)
            return texte[:max_chars]
    except Exception as e:
        print(f"[Web] Erreur sur {url} : {e}")
    return ""

def web_query(urls):
    contexte = ""
    for url in urls:
        st.caption(f"Lecture de : {url}")
        contenu = get_page_content(url)
        if contenu:
            st.caption(f"Résumé de : {url}")
            resume = get_resume(contenu)
            contexte += f"<source>{url}</source>\n<contenu>{resume}</contenu>\n\n"
    return contexte


def get_resume(texte):
    response = ollama.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "Tu es un assistant qui résume des textes de manière concise."},
            {"role": "user", "content": f"Résume ce texte en quelques phrases :\n{texte}"}
        ],
        stream=False
    )
    return response.message.content