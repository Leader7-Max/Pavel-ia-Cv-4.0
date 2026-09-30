"""Module de gestion de l'IA pour Pavel IA CV Pro."""
import os
import streamlit as st

# Importation sécurisée selon la bibliothèque Google GenAI ou OpenAI utilisée
try:
    from google import genai
    from google.genai import errors
    USE_NEW_GENAI = True
except ImportError:
    USE_NEW_GENAI = False

class AIError(Exception):
    """Exception personnalisée pour les erreurs de l'IA."""
    pass

def get_client():
    """Initialise le client API."""
    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        raise AIError("Clé API Gemini introuvable. Configurez GEMINI_API_KEY dans les secrets Streamlit.")
    if USE_NEW_GENAI:
        return genai.Client(api_key=api_key)
    return None

def call_llm(prompt: str) -> str:
    """Fonction générique pour appeler le modèle Gemini."""
    try:
        if USE_NEW_GENAI:
            client = get_client()
            response = client.models.generate_content(
                model="gemini-2.5-flash",  # Utilise le modèle standard performant
                contents=prompt,
            )
            return response.text
        else:
            raise AIError("La bibliothèque 'google-genai' n'est pas installée correctement.")
    except Exception as e:
        raise AIError(f"Erreur lors de la génération par l'IA : {str(e)}")

# --- Fonctions d'assistance pour le CV ---

def suggest_summary(poste: str, sector: str, level: str) -> str:
    """Génère un profil professionnel accrocheur."""
    prompt = (
        f"Rédige un profil professionnel ou une accroche de CV percutante et professionnelle "
        f"en français pour un poste de {poste} dans le secteur de {sector}, avec un niveau {level}. "
        f"Fais 3 ou 4 phrases maximum, orientées résultats et dynamiques."
    )
    return call_llm(prompt)

def suggest_bullets(poste: str, raw_desc: str) -> str:
    """Transforme des notes brutes en missions de CV percutantes."""
    prompt = (
        f"Transforme ces notes brutes d'expériences pour le poste de {poste} "
        f"en puces (bullet points) professionnelles de CV, orientées réalisations et compétences :\n{raw_desc}"
    )
    return call_llm(prompt)

def suggest_skills(poste: str, sector: str) -> str:
    """Suggère des compétences clés."""
    prompt = (
        f"Liste les compétences techniques et soft skills indispensables et recherchées "
        f"pour un poste de {poste} dans le secteur de {sector}."
    )
    return call_llm(prompt)

# --- Autres fonctions de base de l'application (à conserver ou fusionner) ---

def improve(text: str) -> str:
    """Améliore un texte d'expérience professionnelle."""
    prompt = fAméliore et professionalise le texte suivant pour un CV :\n\n{text}"
    return call_llm(prompt)

def make_cv(cv_data: dict) -> str:
    """Génère un CV complet formaté."""
    prompt = fGénère un CV professionnel formaté en Markdown à partir de ces données : {cv_data}"
    return call_llm(prompt)

def make_letter(data: dict) -> str:
    """Génère une lettre de motivation."""
    prompt = fGénère une lettre de motivation professionnelle avec ces informations : {data}"
    return call_llm(prompt)

def analyze(cv_text: str) -> str:
    """Analyse un CV."""
    prompt = fAnalyse ce CV et donne des axes d'amélioration précis :\n\n{cv_text}"
    return call_llm(prompt)

def improve_cv(cv_text: str, analysis: str) -> str:
    """Corrige un CV selon une analyse."""
    prompt = fCorrige et optimise ce CV:\n{cv_text}\n\nEn tenant compte de cette analyse:\n{analysis}"
    return call_llm(prompt)

def match(cv_text: str, offer: str) -> str:
    """Compare un CV à une offre d'emploi."""
    prompt = fCompare ce CV :\n{cv_text}\n\nÀ cette offre d'emploi :\n{offer}\n\nDonne un pourcentage de correspondance et des conseils."
    return call_llm(prompt)

def adapt(cv_text: str, offer: str) -> str:
    """Adapte un CV à une offre."""
    prompt = fAdapte ce CV :\n{cv_text}\n\nPour qu'il corresponde au mieux à cette offre :\n{offer}"
    return call_llm(prompt)

def translate(text: str, lang: str) -> str:
    """Traduit un CV."""
    prompt = fTraduis ce CV en {lang} :\n\n{text}"
    return call_llm(prompt)

def extract(free_text: str) -> str:
    """Extrait des informations d'un texte libre."""
    prompt = fExtrait les informations clés (nom, poste, compétences, expériences) de ce texte :\n\n{free_text}"
    return call_llm(prompt)

def from_facts(facts: str, doc_type: str, lang: str, country: str) -> str:
    """Génère un document à partir de faits extraits."""
    prompt = fGénère un {doc_type} en {lang} pour le pays {country} basé sur ces faits :\n\n{facts}"
    return call_llm(prompt)

def ats(cv_text: str, offer: str = "") -> str:
    """Simule un score ATS."""
    prompt = fÉvalue la compatibilité ATS de ce CV (et de l'offre si présente) sous forme de scores chiffrés sur 100 :\nCV:\n{cv_text}\nOffre:\n{offer}"
    return call_llm(prompt)

def pdf_text(pdf_bytes: bytes) -> str:
    """Extrait le texte d'un PDF (méthode de secours ou implémentation existante)."""
    # Si tu as déjà une fonction d'extraction PDF dans ton code, garde-la, sinon retourne une chaîne vide ou utilise pypdf
    return "Contenu extrait du PDF"
