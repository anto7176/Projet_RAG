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
    

def query(user_input, corpus=None):

    msg = {"role" : "user", "content" : user_input} 
    st.session_state["message"].append(msg)

    """
    msg_bot = {"role" : "assistant", "content" : "test"}
    st.session_state["message"].append(msg_bot)  
    """
    if corpus and corpus != "Aucun":
        contexte = query_RAG(corpus, user_input)
        input_augmente = (
            f"En utilisant les informations suivantes :\n{contexte}\n"
            f"Réponds à la question : {user_input}"
        )
    else:
        input_augmente = user_input  

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        response = ollama.chat(
            model='mistral',
            messages=[{'role': 'system', 'content': 'préprompt'}, {'role': 'user', 'content': input_augmente}],
            stream=True,
        )

        for chunk in response:
            full_response += chunk['message']['content']
            response_placeholder.write(full_response + "|")

        response_placeholder.write(full_response)

        st.session_state["message"].append({"role": "assistant", "content": full_response})


