import streamlit as st
import ollama
from RAG import query_RAG
from wikipedia import wikipedia_query

def session_init():
    if 'message' not in st.session_state:
        st.session_state['message'] = []


def query(user_input, corpus=None, wikipedia_keywords=None, model='mistral', system_prompt=''):
    st.session_state["message"].append({"role": "user", "content": user_input})

    contexte = ""

    if corpus and corpus != "Aucun":
        contexte += query_RAG(corpus, user_input)

    if wikipedia_keywords and wikipedia_keywords.strip():
        with st.spinner("Recherche Wikipedia en cours..."):
            contexte += wikipedia_query(wikipedia_keywords, user_input)

    input_augmente = (
        f"En utilisant les informations suivantes :\n{contexte}\nRéponds à la question : {user_input}"
        if contexte else user_input
    )

    sys_msg = system_prompt.strip() if system_prompt.strip() else "Tu es un assistant IA utile, précis et concis qui répond en français."

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        for chunk in ollama.chat(
            model=model,
            messages=[
                {'role': 'system', 'content': sys_msg},
                {'role': 'user', 'content': input_augmente}
            ],
            stream=True,
        ):
            full_response += chunk.message.content
            response_placeholder.write(full_response + "|")
        response_placeholder.write(full_response)
        st.session_state["message"].append({"role": "assistant", "content": full_response})
