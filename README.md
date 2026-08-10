# Projet RAG : assistant conversationnel local avec LLM

Interface web permettant de dialoguer avec un LLM exécuté **en local** (via Ollama), enrichi par un système de **RAG** (Retrieval-Augmented Generation) et plusieurs sources de contexte : documents locaux, Wikipedia et recherche web.

L'objectif : obtenir des réponses fondées sur des sources choisies plutôt que sur les seules connaissances du modèle, le tout sans dépendre d'une API cloud.

## Fonctionnalités

- **Chat avec un LLM local** via Ollama (modèle sélectionnable, réponses en streaming).
- **RAG sur documents locaux** : import de fichiers (txt, pdf, csv, xlsx), découpage en chunks, indexation vectorielle avec ChromaDB, recherche par similarité.
- **Sources de contexte cumulables** : corpus local, Wikipedia et recherche web.
- **Gestion de corpus** : créer, modifier, ajouter ou supprimer des documents.
- **Préprompt personnalisable** (system prompt).
- **Sessions** : sauvegarder, charger et supprimer des conversations.

## Architecture

| Fichier | Rôle |
|---------|------|
| `app.py` | Interface web Streamlit (chat, barre latérale, gestion des sessions et corpus) |
| `LLM.py` | Orchestration : assemble le contexte (RAG + Wikipedia + web) et interroge le LLM |
| `RAG.py` | Indexation et recherche vectorielle (ChromaDB, embeddings, découpage en chunks) |
| `corpus.py` | Gestion des corpus et des documents |
| `wikipedia.py` | Récupération de contexte depuis Wikipedia |
| `web.py` | Récupération de contexte depuis une recherche web |
| `session.py` | Sauvegarde et chargement des sessions |

## Technologies

Python · Streamlit · Ollama · LangChain · ChromaDB · embeddings (nomic-embed-text)

## Prérequis

- **Python 3.11**
- **[Ollama](https://ollama.com/download)** installé sur la machine
- Les modèles Ollama nécessaires téléchargés :

```bash
ollama pull mistral            # le LLM (ou un autre modèle de ton choix)
ollama pull nomic-embed-text   # le modèle d'embeddings pour le RAG
```

## Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/anto7176/Projet_RAG.git
cd Projet_RAG

# 2. (Recommandé) créer un environnement virtuel
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Installer les dépendances
pip install streamlit ollama langchain langchain-core langchain-community langchain-chroma langchain-ollama langchain-text-splitters chromadb pandas pypdf
```

## Lancement

Le projet a besoin de **deux processus** en parallèle : le serveur Ollama et l'application Streamlit.

```bash
# Terminal 1 : démarrer le serveur Ollama
ollama serve

# Terminal 2 : lancer l'interface
streamlit run app.py
```

L'interface s'ouvre alors dans le navigateur (par défaut sur http://localhost:8501).

## Utilisation

1. Dans la barre latérale, choisir le **modèle** Ollama.
2. (Optionnel) définir un **préprompt** pour orienter le comportement de l'assistant.
3. Choisir une **base de connaissances** : un corpus local, activer Wikipedia, ou la recherche web.
4. Poser une question dans le chat : la réponse s'appuie sur le contexte récupéré.
5. Sauvegarder la conversation via le bouton **Enregistrer** si besoin.

## Limitation connue

Les chemins des dossiers `corpus` et `tmp` sont actuellement définis en dur dans `RAG.py`. Pour faire tourner le projet sur une autre machine, il faut les adapter (ou les remplacer par des chemins relatifs).
