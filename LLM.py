import streamlit as st
import ollama
from RAG import query_RAG

def session_init():
    if 'message' not in st.session_state:
        st.session_state['message'] = []



def get_previous_messages():
    if "message" in st.session_state:
        return st.session_state["message"]
    else:
        return []
    

def query(user_input, corpus=None, wikipedia_keywords=None):
    msg = {"role": "user", "content": user_input}
    st.session_state["message"].append(msg)

    contexte = ""

    if corpus and corpus != "Aucun":
        contexte += query_RAG(corpus, user_input)

    if wikipedia_keywords and wikipedia_keywords.strip():
        from wikipedia import wikipedia_query
        st.caption("Recherche Wikipedia en cours...")
        contexte += wikipedia_query(wikipedia_keywords, user_input)
        st.caption("Recherche Wikipedia terminée.")

    input_augmente = (
        f"En utilisant les informations suivantes :\n{contexte}\nRéponds à la question : {user_input}"
        if contexte else user_input
    )

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        response = ollama.chat(
            model='mistral',
            messages=[
                {'role': 'system', 'content': 'Tu es un assistant IA utile, précis et concis qui répond en français.'},
                {'role': 'user', 'content': input_augmente}
            ],
            stream=True,
        )
        for chunk in response:
            full_response += chunk['message']['content']
            response_placeholder.write(full_response + "|")
        response_placeholder.write(full_response)
        st.session_state["message"].append({"role": "assistant", "content": full_response})
 