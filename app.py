import os
import json
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

# Charger les variables d'environnement depuis .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Assistant HUIM6 - Lkhibra Academy",
    page_icon="🏥",
    layout="centered"
)

# Avertissement de prototype pédagogique non officiel requis par le barème
st.markdown(
    """
    <div style="background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-size: 14px; border: 1px solid #ffeeba;">
        <strong>Prototype pédagogique non officiel</strong>, sans affiliation avec l'entreprise.
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🏥 Assistant - Hôpital Universitaire International Mohammed VI")
st.markdown("Posez vos questions sur les services, spécialités, horaires et démarches pratiques de l'hôpital.")

# 1. Chargement sécurisé du fichier hospital.json
@st.cache_data
def load_knowledge_base():
    try:
        if not os.path.exists("hospital.json"):
            return None
        with open("hospital.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

kb_data = load_knowledge_base()

# Gestion des erreurs : Vérification de la clé API et du fichier JSON
if not api_key:
    st.error("❌ Erreur : La clé `GEMINI_API_KEY` est introuvable dans le fichier `.env` ou l'environnement.")
    st.stop()

if kb_data is None:
    st.error("❌ Erreur : Le fichier `hospital.json` est introuvable ou corrompu à la racine du projet.")
    st.stop()

# Initialisation du client Gemini (SDK google-genai)
try:
    client = genai.Client(api_key=api_key)
    # Modèle recommandé pour les textes
    MODEL_ID = "gemini-2.5-flash"
except Exception as e:
    st.error(f"❌ Erreur lors de l'initialisation du client Gemini : {e}")
    st.stop()

# 2. Construction des instructions système et des connaissances de référence
system_instructions_list = kb_data.get("system_instructions", [])
knowledge_records = kb_data.get("knowledge", [])

# Conversion propre de la base de connaissances en texte contextuel pour le modèle
kb_text = "\n".join([f"- [{item.get('category')}] {item.get('fact')}" for item in knowledge_records])

base_system_prompt = (
    "Tu es l'assistant virtuel de l'Hôpital Universitaire International Mohammed VI (HUIM6). "
    "Réponds en français clair, de manière courtoise, concise et honnête sur l'incertitude. "
    "Règles et limites strictes à respecter obligatoirement :\n"
    "1. Utilise UNIQUEMENT les faits de la base de connaissances fournie ci-dessous. N'invente aucun fait, prix, horaire ou disponibilité.\n"
    "2. Si une information est absente de la base, dis-le clairement et oriente vers les canaux officiels ou un humain.\n"
    "3. INTERDICTION ABSOLUE de fournir des conseils cliniques, diagnostics, prescriptions, dosages ou interprétations de résultats médicaux. En cas d'urgence, conseille de contacter immédiatement les services d'urgence.\n"
    "4. Ne collecte aucune donnée de santé personnelle.\n\n"
    f"Base de connaissances de référence :\n{kb_text}"
)

# 3. Gestion de la mémoire de session (st.session_state)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Bouton pour effacer la conversation (exigé par le cahier des charges)
if st.sidebar.button("🗑️ Effacer la conversation"):
    st.session_state.messages = []
    st.rerun()

# Affichage de l'historique des messages dans l'interface Streamlit
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Saisie utilisateur et interaction avec l'API Gemini
if user_prompt := st.chat_input("Écrivez votre question ici..."):
    # Ajout du message utilisateur à l'historique de session
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Construction de l'historique complet pour maintenir le contexte avec Gemini
    contents_history = []
    
    # On intègre les tours précédents stockés dans st.session_state
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        contents_history.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    # Appel à l'API Gemini avec indicateur de chargement
    with st.chat_message("assistant"):
        with st.spinner("Recherche des informations et génération de la réponse..."):
            try:
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=contents_history,
                    config={
                        "system_instruction": base_system_prompt,
                        "temperature": 0.2, # Température basse pour privilégier la fidélité aux faits
                    }
                )
                assistant_response = response.text
            except APIError as api_err:
                assistant_response = f"⚠️ Erreur de l'API Gemini : {api_err.message}"
            except Exception as e:
                assistant_response = f"⚠️ Une erreur technique est survenue lors de la communication avec le modèle : {e}"
            
            st.markdown(assistant_response)
    
    # Enregistrement de la réponse du modèle dans l'historique de session
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})