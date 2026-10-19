# Chatbot IA - Hôpital Universitaire International Mohammed VI (HUIM6)
*Projet réalisé dans le cadre du parcours Lkhibra Academy.*

## Description
Assistant virtuel interactif développé en Python, utilisant **Streamlit** pour l'interface utilisateur et l'API **Gemini** (`gemini-2.5-flash`) via le SDK `google-genai`. Le chatbot répond en français en s'appuyant strictement sur une base de connaissances structurée (`hospital.json`) tout en conservant le contexte de la session.

## Prérequis et Installation
1. Cloner le dépôt et placer le fichier `hospital.json` à la racine.
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt