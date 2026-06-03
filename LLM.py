import streamlit as st
import ollama
from RAG import query_RAG
from wikipedia import wikipedia_query
from web import get_URL, web_query

# initialisation de l'historique des messages
def session_init():
    if 'message' not in st.session_state:
        st.session_state['message'] = []


def query(user_input, corpus=None, wikipedia_keywords=None, model='mistral', system_prompt='', web_search=False):
    # ajout du message utilisateur à l'historique
    st.session_state["message"].append({"role": "user", "content": user_input})

    contexte = ""

     # récupération du contexte RAG si un corpus est sélectionné
    if corpus and corpus != "Aucun":
        contexte += query_RAG(corpus, user_input)

    # récupération du contexte Wikipedia si activé
    if wikipedia_keywords and wikipedia_keywords.strip():
        with st.spinner("Recherche Wikipedia en cours..."):
            wiki_ctx = wikipedia_query(wikipedia_keywords, user_input)
            if wiki_ctx:
                contexte += "\n" + wiki_ctx

    # récupération du contexte Web si activé
    if web_search:
        with st.spinner("Recherche Web en cours..."):
            urls = get_URL(user_input)
            st.caption(f"🌐 URLs : {', '.join(urls)}")
            web_ctx = web_query(urls)
            if web_ctx:
                contexte += "\n" + web_ctx

    # construction du message augmenté avec le contexte
    input_augmente = (
        f"En utilisant les informations suivantes :\n{contexte}\nRéponds à la question : {user_input}"
        if contexte else user_input
    )

    sys_msg = system_prompt.strip() if system_prompt.strip() else "Tu es un assistant IA utile, précis et concis qui répond en français."

    # récupération de l'historique sans le dernier message
    historique = [{"role": m["role"], "content": m["content"]}
                  for m in st.session_state["message"][:-1]]

    messages = [{"role": "system", "content": sys_msg}] + historique + [{"role": "user", "content": input_augmente}]

    # génération de la réponse en streaming
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        for chunk in ollama.chat(model=model, messages=messages, stream=True):
            full_response += chunk.message.content
            response_placeholder.write(full_response + "|")
        response_placeholder.write(full_response)

        # sauvegarde de la réponse dans l'historique
        st.session_state["message"].append({"role": "assistant", "content": full_response})