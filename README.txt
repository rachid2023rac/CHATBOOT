# 💻 Assistant Virtuel - Worklab Coworking Space

Un prototype d'assistant virtuel intelligent développé avec **Python**, **Streamlit** et l'**API Google Gemini**, conçu pour répondre aux questions pratiques des membres et visiteurs d'un espace de coworking (tarifs, horaires, équipements, abonnements).

> **Avertissement :** Prototype pédagogique non officiel, développé dans le cadre de la formation Lkhibra Academy.

---

## 🎯 Objectifs du Projet

- **Assistance 24/7 :** Répondre de manière claire, courtoise et rapide aux demandes d'informations fréquentes.
- **Fiabilité des réponses (RAG-lite) :** Intégrer la base de connaissances directement dans le prompt système pour limiter les hallucinations et garantir des faits exacts.
- **Respect strict des règles :** Refuser poliment les demandes hors périmètre (gestion de réservations directes, collecte de données bancaires).
- **Gestion de la mémoire :** Maintenir l'historique de conversation durant la session avec possibilité de réinitialisation.

---

## 🛠️ Stack Technique

- **Langage :** Python 3.10+
- **Interface Utilisateur :** [Streamlit](https://streamlit.io/)
- **Modèle d'IA :** Google Gemini (`google-genai` SDK, modèle `gemini-3.8-flash`)
- **Déploiement :** Streamlit Community Cloud
- **Gestion des variables d'environnement :** `python-dotenv` (local) et `st.secrets` (Cloud)

---

## 📁 Structure du Projet

```text
├── app.py              # Application principale Streamlit & logique d'appel Gemini
├── requirements.txt    # Dépendances Python du projet
├── .env.example        # Modèle de configuration de la clé API (pour le dev local)
└── README.md           # Documentation du projet