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
    page_title="Assistant HUIM6 - Lkhibra Academy",
    page_icon="🏥",
    layout="centered"
)

# Avertissement prototype pédagogique obligatoire (selon le barème Lkhibra Academy)
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

# 3. Base de connaissances structurée intégrée directement (solution infaillible sur le Cloud)
KB_DATA = {
    "system_instructions": [
        "You are an unofficial educational prototype, not an employee or authorised representative of the company.",
        "Respond in clear French for the user interaction while respecting company facts."
    ],
    "knowledge": [
        {"id": "identity", "category": "identity", "fact": "HUIM6 is a private, non-profit hospital."},
        {"id": "university", "category": "identity", "fact": "It belongs to an ecosystem centred on Université Mohammed VI des Sciences et de la Santé."},
        {"id": "values", "category": "identity", "fact": "The hospital lists excellence, ethics, empathy, innovation and commitment among its values."},
        {"id": "published_capacity", "category": "identity", "fact": "The about page states 325 beds and places; this is capacity, not live bed availability."},
        {"id": "address", "category": "contact", "fact": "Address: Route P 3011, Bouskoura, Morocco."},
        {"id": "appointment_phone", "category": "contact", "fact": "Appointments: +212 5 29 09 11 11."},
        {"id": "information_phone", "category": "contact", "fact": "General information: +212 5 29 09 22 22."},
        {"id": "emergency_phone", "category": "contact", "fact": "Hospital emergency contact: +212 5 29 09 33 33; this is not a national emergency number."},
        {"id": "administration_phone", "category": "contact", "fact": "Administration: +212 5 29 09 44 44."},
        {"id": "consult_weekdays", "category": "hours", "fact": "The homepage lists consultations Monday-Friday, 08:30-18:00."},
        {"id": "consult_saturday", "category": "hours", "fact": "The homepage lists Saturday consultations, 08:30-12:30."},
        {"id": "emergency_hours", "category": "hours", "fact": "Adult and paediatric emergency services are listed as operating 24/7."},
        {"id": "appointment_inperson", "category": "patient_services", "fact": "Consultation appointments can be requested in person at the consultation service."},
        {"id": "appointment_web", "category": "patient_services", "fact": "The FAQ describes an appointment request form on the hospital website."},
        {"id": "doctor_directory", "category": "patient_services", "fact": "Use the website specialty pages or switchboard for the doctor directory."},
        {"id": "doctor_choice", "category": "patient_services", "fact": "Advance appointment requests can specify a doctor; availability is not guaranteed."},
        {"id": "doctor_substitute", "category": "patient_services", "fact": "Emergencies or exceptional circumstances may require a different doctor."},
        {"id": "cafe", "category": "patient_services", "fact": "A cafeteria is described on the medical hall’s ground floor."},
        {"id": "shop", "category": "patient_services", "fact": "The FAQ describes a ground-floor shop for groceries, drinks and hygiene items."},
        {"id": "room_types", "category": "patient_services", "fact": "The FAQ describes individual rooms, double rooms and suites."},
        {"id": "room_amenities", "category": "patient_services", "fact": "Listed room amenities include television, Wi-Fi and air conditioning."},
        {"id": "records_request", "category": "patient_services", "fact": "Medical-record copies require a signed written request and identity evidence through the hospital."},
        {"id": "records_destination", "category": "patient_services", "fact": "Requests go to the Direction de l’Information Médicale; never upload records to this chatbot."},
        {"id": "billing_office", "category": "patient_services", "fact": "The Bureau des Admissions et Facturation handles admission administration and stay charges."},
        {"id": "welcome_booklet", "category": "patient_services", "fact": "A welcome booklet is provided for an inpatient stay."},
        {"id": "accessible_parking", "category": "patient_services", "fact": "The FAQ describes dedicated parking spaces for reduced-mobility visitors."},
        {"id": "lost_property", "category": "patient_services", "fact": "Lost property can be reported to the hospital’s régie."},
        {"id": "preadmission", "category": "admission", "fact": "Scheduled hospitalisation or surgery requires pre-admission at the admissions office."},
        {"id": "estimate", "category": "admission", "fact": "An estimate can be requested before admission; the final amount may change."},
        {"id": "id_document", "category": "admission", "fact": "The published admission list includes a copy of the patient’s CIN."},
        {"id": "doctor_order", "category": "admission", "fact": "A doctor’s prescription or hospitalisation letter is listed for admission."},
        {"id": "insurance_documents", "category": "admission", "fact": "Insurance or mutual-insurance documents may be required for coverage processing."},
        {"id": "minor_documents", "category": "admission", "fact": "A minor must be accompanied by a parent/legal guardian with supporting identity/family documents."},
        {"id": "medical_documents", "category": "admission", "fact": "Bring the medical documents requested by the hospital; never send them through this prototype."},
        {"id": "insurance_named", "category": "admission", "fact": "The page names CNOPS, CNSS and private insurers; individual approval must be confirmed."},
        {"id": "linen", "category": "admission", "fact": "The page describes hospital-provided pyjamas and bed linen."},
        {"id": "laundry", "category": "admission", "fact": "Laundry service is described as paid and added to the bill."},
        {"id": "international_unit", "category": "international_support", "fact": "A dedicated international unit supports international patients."},
        {"id": "international_plan", "category": "international_support", "fact": "The unit can help plan consultations and care."},
        {"id": "international_estimate", "category": "international_support", "fact": "The unit can prepare and update estimated care costs."},
        {"id": "international_transfer", "category": "international_support", "fact": "Airport/station reception and transfer arrangements can be discussed with the unit."},
        {"id": "international_lodging", "category": "international_support", "fact": "The unit describes help arranging hotels, apartments and car hire."},
        {"id": "international_language", "category": "international_support", "fact": "Interpreter assistance is described among international-patient services."},
        {"id": "international_admin", "category": "international_support", "fact": "The unit assists with administrative and financial formalities."},
        {"id": "international_departure", "category": "international_support", "fact": "Departure support can include reports, return arrangements and follow-up planning."},
        {"id": "obstetrics", "category": "listed_specialties", "fact": "The women/mother/child unit lists gynaecology and obstetrics."},
        {"id": "neonatology", "category": "listed_specialties", "fact": "The unit lists neonatology."},
        {"id": "paediatrics", "category": "listed_specialties", "fact": "The unit lists paediatrics."},
        {"id": "paediatric_icu", "category": "listed_specialties", "fact": "The unit lists paediatric intensive care."},
        {"id": "paediatric_surgery", "category": "listed_specialties", "fact": "The unit lists paediatric surgery."},
        {"id": "neurosurgery", "category": "listed_specialties", "fact": "The head-and-neck unit lists neurosurgery."},
        {"id": "ent", "category": "listed_specialties", "fact": "The unit lists ENT and cervicofacial surgery."},
        {"id": "maxillofacial", "category": "listed_specialties", "fact": "The unit lists maxillofacial surgery."},
        {"id": "ophthalmology", "category": "listed_specialties", "fact": "The unit lists ophthalmology."},
        {"id": "anaesthesia", "category": "listed_specialties", "fact": "The medical-specialties page lists anaesthesia and intensive care."},
        {"id": "cardiology", "category": "listed_specialties", "fact": "The page lists cardiology."},
        {"id": "dental", "category": "listed_specialties", "fact": "Dental care includes orthodontics and paediatric dentistry."},
        {"id": "dermatology", "category": "listed_specialties", "fact": "The page lists dermatology."},
        {"id": "endocrinology", "category": "listed_specialties", "fact": "The page lists endocrinology and diabetology."},
        {"id": "general_surgery", "category": "listed_specialties", "fact": "The surgical specialties page lists general surgery."},
        {"id": "gyn_surgery", "category": "listed_specialties", "fact": "The page lists gynaecological surgery."},
        {"id": "eye_surgery", "category": "listed_specialties", "fact": "The page lists eye surgery."},
        {"id": "skin_surgery", "category": "listed_specialties", "fact": "The page lists dermatological surgery."},
        {"id": "imaging", "category": "imaging_and_laboratory", "fact": "Imaging services include MRI, CT, ultrasound/Doppler and conventional radiology."},
        {"id": "mammography", "category": "imaging_and_laboratory", "fact": "The imaging page also lists mammography and dental panoramic imaging."},
        {"id": "lab_disciplines", "category": "imaging_and_laboratory", "fact": "Laboratory disciplines include biochemistry, haematology, bacteriology, pathology and immunology."},
        {"id": "exam_preparation", "category": "imaging_and_laboratory", "fact": "Some tests require preparation; contact the laboratory for instructions specific to the prescribed test."}
    ]
}

# Validation de la clé API
if not api_key:
    st.error("❌ Erreur : La clé `GEMINI_API_KEY` est introuvable. Configurez-la dans vos secrets Streamlit Cloud ou dans un fichier `.env`.")
    st.stop()

# 4. Initialisation du client Gemini (SDK google-genai)
try:
    client = genai.Client(api_key=api_key)
 #   MODEL_ID = "gemini-2.5-flash"
 MODEL_ID = "gemini-3.8-flash"
except Exception as e:
    st.error(f"❌ Erreur lors de l'initialisation du client Gemini : {e}")
    st.stop()

# 5. Construction du prompt système avec les connaissances
knowledge_records = KB_DATA.get("knowledge", [])
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