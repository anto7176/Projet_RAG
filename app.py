from LLM import *
import streamlit as st
from corpus import *
import pandas as pd
from wikipedia import *
from session import *
# "C:\Users\vadotant\AppData\Local\Programs\Ollama\ollama.exe" serve
# & "C:/Program Files/Python311/python.exe" -m streamlit run app.py

# saisie du nom du nouveau corpus
@st.dialog("Ajouter un nouveau corpus")
def popup_ajout_corpus():
    Nom_corpus = st.text_area(label="Nom du nouveau corpus :")
    col1, col2 = st.columns(2)
    with col1:
        if Nom_corpus:
            if st.button('Valider', width="stretch", disabled=False):
                add_corpus(Nom_corpus)
                st.rerun()
        else:
            st.button('Valider', width="stretch", disabled=True)
    with col2:
        if st.button('Annuler', width="stretch", disabled=False):
            st.rerun()


@st.dialog("Modifier le corpus")
def popup_corpus(selected_corpus):
    st.write(f"Corpus : **{selected_corpus}**")
    list_doc = get_documents_from_corpus(selected_corpus)
    df = pd.DataFrame({"Sélectionner": [False] * len(list_doc), "Document": list_doc})
    edited = st.data_editor(df, use_container_width=True, hide_index=True)
    if st.button("Supprimer la sélection", width="stretch"):
        to_delete = edited[edited["Sélectionner"]]["Document"].tolist()
        for doc in to_delete:
            delete_document_from_corpus(selected_corpus, doc)
        st.rerun()
    st.write("Ajouter des documents a ce corpus")
    uploaded_files = st.file_uploader("Upload data", accept_multiple_files=True, type=["txt", "pdf", "csv", "xlsx"])
    if uploaded_files:
        if st.button('Charger les documents dans le corpus', width="stretch"):
            add_documents_to_corpus(selected_corpus, uploaded_files)
            st.rerun()
    if st.button('Supprimer ce corpus', width="stretch"):
        delete_corpus(selected_corpus)
        st.rerun()

# sauvegarde de la session avec un nom
@st.dialog("Enregistrer la session")
def popup_enregistrer():
    nom = st.text_input("Nom de la session :")
    if st.button("Enregistrer", width="stretch", disabled=not nom):
        save_session(nom)
        st.session_state["session_name"] = nom
        st.rerun()

# chargement d'une session sauvegardée
@st.dialog("Charger une session")
def popup_charger():
    sessions = get_all_sessions()
    if not sessions:
        st.write("Aucune session sauvegardée.")
        return
    selected = st.selectbox("Sélectionnez une session :", options=sessions)
    if st.button("Charger la session", width="stretch"):
        load_session(selected)
        st.rerun()

# suppression d'une session sauvegardée
@st.dialog("Supprimer la session")
def popup_supprimer():
    sessions = get_all_sessions()
    if not sessions:
        st.write("Aucune session sauvegardée.")
        return
    selected = st.selectbox("Sélectionnez une session à supprimer :", options=sessions)
    st.write(f"Voulez-vous supprimer la session **{selected}** ?")
    if st.button("Confirmer", width="stretch"):
        delete_session(selected)
        st.rerun()


def sidebar():
    with st.sidebar:
        # affichage du nom de session ou titre par défaut
        session_name = st.session_state.get("session_name", "")
        if session_name:
            st.subheader(f"Session : {session_name}")
        else:
            st.subheader("Paramètres")
            
        # boutons de gestion des sessions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Nouvelle", width="stretch"):
                reset_session()
                st.rerun()
        with col2:
            if st.button("Enregistrer", width="stretch"):
                popup_enregistrer()
        col3, col4 = st.columns(2)
        with col3:
            if st.button("Charger", width="stretch"):
                popup_charger()
        with col4:
            if st.button("Supprimer", width="stretch"):
                popup_supprimer()

        st.divider()
        # sélection du modèle
        models_data = ollama.list()
        model_list = [model['model'] for model in models_data.get('models', []) 
              if 'embed' not in model['model']]
        selected_model = st.selectbox("Choisissez un modèle Ollama", options=model_list,index=model_list.index(st.session_state["model"]) if st.session_state.get("model") in model_list else 0)

        # Def Preprompt
        st.write("Préprompt")
        system_prompt = st.text_area(label="Définissez le préprompt (System Prompt) :", height=150,value=st.session_state.get("system_prompt", ""))

        # sélection du corpus RAG
        st.write("Bases de connaissances")
        corpus_list = get_corpus_list()
        selected_corpus = st.selectbox("Corpus local :", options=corpus_list,index=corpus_list.index(st.session_state["corpus"]) if st.session_state.get("corpus") in corpus_list else 0)
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Nouveau', width="stretch"):
                popup_ajout_corpus()
        with col2:
            if selected_corpus == "Aucun":
                st.button('Modifier', width="stretch", disabled=True)
            else:
                if st.button('Modifier', width="stretch", disabled=False):
                    popup_corpus(selected_corpus)

        st.divider()

        # config Wikipedia
        col1, col2 = st.columns([3, 1])
        with col1:
            wikipedia_keywords = st.text_input("Wikipedia :", placeholder="ex: ESEO",value=st.session_state.get("wikipedia_keywords", ""))
        with col2:
            st.write("")
            wikipedia_active = st.toggle("Activer", key="toggle_wiki",
                value=st.session_state.get("wikipedia_active", False),
                label_visibility="collapsed")

        # config recherche web
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Recherche Web")
        with col2:
            web_search = st.toggle("Activer", key="toggle_web",
                value=st.session_state.get("web_search", False),
                label_visibility="collapsed")

        st.divider()
        st.info("Toutes modifications ici sera prise en compte des le prochain message")
        st.caption(f"Version : {st.__version__}")
    
    # sauvegarde des paramètres dans le session_state
    st.session_state["model"] = selected_model
    st.session_state["system_prompt"] = system_prompt
    st.session_state["corpus"] = selected_corpus
    st.session_state["wikipedia_keywords"] = wikipedia_keywords
    st.session_state["wikipedia_active"] = wikipedia_active
    st.session_state["web_search"] = web_search

    return {
        "model": selected_model,
        "system_prompt": system_prompt,
        "corpus": selected_corpus,
        "wikipedia_keywords": wikipedia_keywords if wikipedia_active else "",
        "web_search": web_search,
    }


def main():
    st.title("Interface LLM Antoine VADOT")
    session_init()
    params = sidebar()

    # affichage de l'historique des messages
    for msg in st.session_state["message"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

     # envoi d'un nouveau message
    requete = st.chat_input(placeholder="Your message")
    if requete:
        with st.chat_message("user"):
            st.write(requete)
        query(requete, corpus=params["corpus"], wikipedia_keywords=params["wikipedia_keywords"],
              model=params["model"], system_prompt=params["system_prompt"], web_search=params["web_search"])


if __name__ == "__main__":
    main()