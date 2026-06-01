import json
import streamlit as st
import os

SESSIONS_DIR = r"D:\Antoine_Vadot\Projet_RAG\session"


def reset_session():
    st.session_state.clear()


def save_session(nom):
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    data = {
        "message": st.session_state.get("message", []),  # ← sans s
        "model": st.session_state.get("model", ""),
        "system_prompt": st.session_state.get("system_prompt", ""),
        "corpus": st.session_state.get("corpus", "Aucun"),
        "wikipedia_keywords": st.session_state.get("wikipedia_keywords", ""),
        "wikipedia_active": st.session_state.get("wikipedia_active", False),
        "web_search": st.session_state.get("web_search", False),
        "session_name": nom,
    }
    path = os.path.join(SESSIONS_DIR, nom + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_all_sessions():
    return [f.replace(".json", "") for f in os.listdir(SESSIONS_DIR) if f.endswith(".json")]


def load_session(nom):
    path = os.path.join(SESSIONS_DIR, nom + ".json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for key in ["toggle_wiki", "toggle_web"]:
        if key in st.session_state:
            del st.session_state[key]
    for key, value in data.items():
        st.session_state[key] = value
    st.session_state["session_name"] = nom
    # Force la valeur des toggles
    st.session_state["toggle_wiki"] = data.get("wikipedia_active", False)
    st.session_state["toggle_web"] = data.get("web_search", False)

def delete_session(nom):
    path = os.path.join(SESSIONS_DIR, nom + ".json")
    if os.path.exists(path):
        os.remove(path)
    reset_session()