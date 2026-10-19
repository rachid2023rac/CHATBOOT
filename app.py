import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

# 1. Charger les variables d'environnement (.env en local)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Récupération de secours via st.secrets pour Streamlit Cloud
if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass

# 2. Configuration de la page Streamlit
st.set_page_config(
    page_title="Assistant Coworking - Wavestart",
    page_icon="💻",
    layout="centered"
)

# Avertissement prototype pédagogique obligatoire
st.markdown(
    """
    <div style="background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-size: 14px; border: 1px solid #ffeeba;">
        <strong>Prototype pédagogique non officiel</strong>, sans affiliation avec l'entreprise.
    </div>
    """,
    unsafe_allow_html=True
)

st.title("💻 Assistant - Wavestart Coworking Space")
st.markdown("Posez vos questions sur nos espaces, nos tarifs, les horaires et nos services.")

# 3. Base de connaissances structurée pour le Coworking
KB_DATA = {
    "system_instructions": [
        "Tu es l'assistant virtuel d'un espace de coworking. Réponds en français clair.",
        "Utilise uniquement les faits de la base de connaissances. N'invente aucun tarif ou horaire.",
        "Si une information est absente, dis-le clairement et invite à contacter l'accueil."
    ],
    "knowledge": [
        {"id": "address", "category": "contact", "fact": "Adresse : Boulevard Mohammed V, Casablanca, Maroc."},
        {"id": "contact_phone", "category": "contact", "fact": "Téléphone de l'accueil : +212 5 22 00 11 22."},
        {"id": "opening_hours", "category": "hours", "fact": "L'espace est ouvert du lundi au vendredi de 08:00 à 20:00, et le samedi de 09:00 à 15:00."},
        {"id": "wifi_speed", "category": "services", "fact": "Un réseau Wi-Fi haut débit fibre optique est inclus pour tous les résidents et nomades."},
        {"id": "pricing_nomad", "category": "pricing", "fact": "Le pass journalier (Open Space) est listé à 150 MAD par jour."}
    ]
}

# Validation de la clé API
if not api_key:
    st.error("❌ Erreur : La clé `GEMINI_API_KEY` est introuvable. Configurez-la dans vos secrets Streamlit Cloud ou dans un fichier `.env`.")
    st.stop()

# 4. Initialisation du client Gemini (SDK google-genai)
try:
    client = genai.Client(api_key=api_key)
    MODEL_ID = "gemini-3-flash-preview"
except Exception as e:
    st.error(f"❌ Erreur lors de l'initialisation du client Gemini : {e}")
    st.stop()

# 5. Construction du prompt système avec les connaissances
knowledge_records = KB_DATA.get("knowledge", [])
kb_text = "\n".join([f"- [{item.get('category')}] {item.get('fact')}" for item in knowledge_records])

base_system_prompt = (
    "Tu es l'assistant virtuel de l'espace de coworking Wavestart. "
    "Réponds en français clair, de manière courtoise, concise et honnête sur l'incertitude. "
    "Règles et limites strictes à respecter obligatoirement :\n"
    "1. Utilise UNIQUEMENT les faits de la base de connaissances fournie ci-dessous. N'invente aucun tarif, horaire ou service.\n"
    "2. Si une information est absente de la base, dis-le clairement et oriente vers l'accueil.\n"
    "3. Ne demande jamais de données bancaires ou sensibles.\n\n"
    f"Base de connaissances de référence :\n{kb_text}"
)

# 6. Gestion de la mémoire de session (st.session_state)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Bouton pour effacer la conversation
if st.sidebar.button("🗑️ Effacer la conversation"):
    st.session_state.messages = []
    st.rerun()

# Affichage des messages passés
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Saisie utilisateur et envoi à l'API Gemini
if user_prompt := st.chat_input("Écrivez votre question ici..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    contents_history = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        contents_history.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    with st.chat_message("assistant"):
        with st.spinner("Recherche des informations et génération de la réponse..."):
            try:
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=contents_history,
                    config={
                        "system_instruction": base_system_prompt,
                        "temperature": 0.2,
                    }
                )
                assistant_response = response.text
            except APIError as api_err:
                assistant_response = f"⚠️ Erreur de l'API Gemini : {api_err.message}"
            except Exception as e:
                assistant_response = f"⚠️ Une erreur technique est survenue : {e}"
            
            st.markdown(assistant_response)
    
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})