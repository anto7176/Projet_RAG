from LLM import *
import streamlit as st
from corpus import *
import pandas as pd
from wikipedia import *



def main():
    st.title("Interface LLM")

    session_init()

    @st.dialog("Ajouter un nouveau corpus")
    def popup_ajout_corpus():
        Nom_corpus = st.text_area(label="Nom du nouveau corpus :")
        col1,col2 = st.columns(2)
        with col1:
            if Nom_corpus :
                if st.button('Valider', width="stretch", disabled=False):
                    add_corpus(Nom_corpus)
                    st.rerun()
            else:
                st.button('Valider', width="stretch", disabled=True)
        with col2:
            if st.button('Annuler', width="stretch", disabled=False) :
                st.rerun()


    @st.dialog("Modifier le corpus")
    def popup_corpus():
        st.write(f"Corpus : **{selected_corpus}**")
        list_doc = get_documents_from_corpus(selected_corpus)
        df = pd.DataFrame({"Sélectionner": [False] * len(list_doc), "Document": list_doc})
        edited = st.data_editor(df, use_container_width=True, hide_index=True)
        if st.button("Supprimer la sélection",width="stretch"):
            to_delete = edited[edited["Sélectionner"]]["Document"].tolist()
            for doc in to_delete:
                delete_document_from_corpus(selected_corpus, doc)
            st.rerun()
        st.write("Ajouter des documents a ce corpus")
        uploaded_files = st.file_uploader("Upload data", accept_multiple_files=True, type=["txt","pdf","csv","xlsx"])
        if uploaded_files:
            if st.button('Charger les documents dans le corpus', width="stretch", disabled=False):
                add_documents_to_corpus(selected_corpus, uploaded_files)
                st.rerun()
        if st.button('Supprimer ce corpus', width="stretch", disabled=False):
            delete_corpus(selected_corpus)
            st.rerun()
    

    requete = st.chat_input(placeholder="Your message")
    if requete:
        with st.chat_message("user"):
            st.write(requete)
        query(requete, corpus=selected_corpus)




    with st.sidebar:
        st.write("Paramètres")

        models_data = ollama.list()
        model_list = [model['model'] for model in models_data.get('models', [])]
        selected_model = st.selectbox("Choisissez un modèle Ollama",options=model_list,index=0 if model_list else None)

        st.write("Préprompt")

        system_prompt = st.text_area(
            label="Définissez le préprompt (System Prompt) :",
            height=150
        )

        st.write("Bases de connaissances")

        #Corpus
        corpus_list = get_corpus_list()
        selected_corpus = st.selectbox("Corpus local :",options=corpus_list,index=0 if corpus_list else None)

        # Wikipedia
        Mots_Cles_wiki = st.text_area(
            label="Wikipedia :",
            height=10
        )
        if Mots_Cles_wiki :
            if requete :
                wikipedia_query(Mots_Cles_wiki,requete)

        col1,col2 = st.columns(2)
        with col1:
            if st.button('Nouveau',width="stretch"):
                popup_ajout_corpus()
        with col2:
            if selected_corpus == "Aucun":
                st.button('Modifier', width="stretch", disabled=True)
            else:
                if st.button('Modifier', width="stretch", disabled=False):
                    popup_corpus()

        st.info("Toutes modifications ici sera prise en compte dés le prochain message")

        st.write("version :",st.__version__)


    for msg in st.session_state["message"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])


    


if __name__ == "__main__":
    main()
