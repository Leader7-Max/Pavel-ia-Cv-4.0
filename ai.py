"""Appels Gemini via SDK google-generativeai et extraction de texte PDF."""
import io
import json

import google.generativeai as genai
import streamlit as st
from pypdf import PdfReader

from config import LANGS

MAX_PDF_BYTES = 5 * 1024 * 1024


class AIError(Exception):
    """Erreur avec un message destiné à l'utilisateur final."""


RULES = (
    "Tu es Pavel IA, assistant carrière. RÈGLE ABSOLUE : n'invente jamais un "
    "diplôme, un emploi, une entreprise, une compétence, une certification, un "
    "salaire, un résultat chiffré, un permis, une langue ou une expérience. "
    "Utilise uniquement les faits fournis ; si une information manque, "
    "n'écris rien à sa place. Tu peux reformuler, restructurer et adapter les "
    "mots-clés. Ne donne aucune garantie d'embauche ou de réussite ATS."
)
FORMAT = (
    "Format de sortie : texte brut. Ligne 1 = PRÉNOM NOM ; ligne 2 = titre du "
    "poste ; ligne 3 = coordonnées ; puis des sections '## Titre' avec des "
    "puces '- '. Pas de gras, pas de tableau."
)


def _secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def _init_genai():
    raw_key = str(_secret("GEMINI_API_KEY") or "")
    key = "".join(raw_key.split()).strip("\"'").strip()
    if not key:
        raise AIError("Clé GEMINI_API_KEY absente : ajoutez-la dans Streamlit Secrets.")
    genai.configure(api_key=key)


def ask(prompt):
    _init_genai()

    # Modèles les plus récents et puissants (Gemini 2.5 Pro & Flash)
    models_to_try = [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite"
    ]
    
    custom_model = str(_secret("GEMINI_MODEL", "") or "").strip().strip("\"'").strip()
    if custom_model:
        if custom_model.startswith("models/"):
            custom_model = custom_model[len("models/"):]
        models_to_try.insert(0, custom_model)

    last_error = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=RULES
            )
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.3}
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            last_error = e
            continue

    err_msg = str(last_error) if last_error else "Erreur inconnue"
    if "API_KEY_INVALID" in err_msg or "400" in err_msg or "403" in err_msg:
        raise AIError("Clé API refusée ou invalide. Regénérez une clé sur Google AI Studio.")
    if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
        raise AIError("Quota IA atteint. Réessayez dans quelques minutes.")
    
    raise AIError(f"Erreur IA ({err_msg}). Vérifiez votre clé API dans Streamlit Secrets.")


@st.cache_data(ttl=600, max_entries=5, show_spinner=False)
def pdf_text(data: bytes):
    if len(data) > MAX_PDF_BYTES:
        raise AIError("PDF trop volumineux (5 Mo maximum).")
    if not data.startswith(b"%PDF"):
        raise AIError("Ce fichier n'est pas un PDF valide.")
    try:
        pages = PdfReader(io.BytesIO(data)).pages[:10]
        text = "\n".join((p.extract_text() or "") for p in pages)
    except Exception:
        raise AIError("Impossible de lire ce PDF.")
    if len(text.strip()) < 50:
        raise AIError("Aucun texte trouvé (PDF scanné ?). Collez le texte du CV à la main.")
    return text[:15000]


def _lang(name):
    return LANGS.get(name, "français")


def make_cv(d):
    return ask(
        f"Rédige un CV complet en {_lang(d.get('lang'))}, style « {d.get('cvtype', '')} », "
        f"pour le marché : {d.get('target_country', '')}. Adapte vocabulaire et structure "
        "sans prétendre qu'une convention est obligatoire. Données (JSON) :\n"
        f"{json.dumps(d, ensure_ascii=False)}\n"
        "Inclus un profil professionnel de 3 à 4 lignes basé uniquement sur ces faits, "
        "puis expériences (puces), formation, compétences, langues, informations "
        f"complémentaires. Omet toute section vide. {FORMAT}"
    )


def make_letter(d):
    return ask(
        f"Rédige en {_lang(d.get('lang'))} une lettre de motivation naturelle, ton "
        f"{d.get('tone')}, longueur {d.get('length')}, personnalisée à l'annonce (évite "
        "les formules génériques). Format lettre classique, sans sections '##'. "
        f"Données (JSON) :\n{json.dumps(d, ensure_ascii=False)}"
    )


def improve(text):
    return ask(
        "Améliore la formulation de ce texte de CV (verbes d'action, clarté) sans "
        "ajouter aucun fait, chiffre ou compétence absent. Garde la même structure. "
        f"Texte brut uniquement :\n{text}"
    )


def analyze(cv):
    return ask(
        "Analyse ce CV (structure, titre, profil, expérience, compétences, formation, "
        "lisibilité, cohérence, répétitions, informations manquantes, mots-clés, "
        "formulations faibles, erreurs). Réponds en français avec exactement trois "
        "sections en markdown : ### Points forts, ### À améliorer, ### Suggestions.\n"
        f"CV :\n{cv}"
    )


def improve_cv(cv, analysis=""):
    return ask(
        "Réécris ce CV en version améliorée, en corrigeant les faiblesses sans rien "
        f"inventer, dans la même langue. {FORMAT}\n"
        f"Pistes d'analyse (facultatif) :\n{analysis}\nCV :\n{cv}"
    )


def ats(cv, offer=""):
    ctx = f"Offre :\n{offer}\n" if offer else ""
    return ask(
        "Évalue de façon indicative la compatibilité ATS de ce CV. Réponds avec une "
        "ligne par catégorie, au format exact : Catégorie | note de 0 à 100 | explication "
        "courte. Catégories : Titre du poste, Mots-clés, Expérience, Compétences, "
        "Structure, Lisibilité. Ensuite 2 à 3 conseils en puces. Réponds en français.\n"
        f"{ctx}CV :\n{cv}"
    )


def match(cv, offer):
    return ask(
        "Compare ce CV à l'offre. Réponds en français, en markdown : première ligne "
        "'Correspondance : NN %' (estimation indicative), puis ### Mots-clés trouvés, "
        "### Mots-clés absents, ### Compétences correspondantes, ### Compétences à "
        "vérifier (que le candidat devra confirmer), ### Expérience pertinente, "
        f"### Éléments à reformuler.\nOFFRE :\n{offer}\n\nCV :\n{cv}"
    )


def adapt(cv, offer):
    return ask(
        "Adapte ce CV à l'offre : reformule et réordonne, utilise les mots-clés de "
        "l'offre uniquement pour des compétences DÉJÀ présentes dans le CV. N'ajoute "
        f"aucune compétence absente. Même langue. {FORMAT}\nOFFRE :\n{offer}\n\nCV :\n{cv}"
    )


def translate(text, lang):
    return ask(
        f"Traduis en {_lang(lang)} en conservant strictement le sens, les informations "
        "et la structure ('##', puces). N'ajoute rien.\n" + text
    )


def extract(text):
    return ask(
        "Extrais du texte libre les faits fournis, sous forme de liste '- Clé : valeur' "
        "(métier, expérience, compétences, permis, disponibilité, localisation, autres "
        "informations utiles). N'invente rien ; ignore ce qui n'est pas dit.\n" + text
    )


def from_facts(facts, kind, lang, country):
    if kind == "CV":
        return ask(
            f"Rédige en {_lang(lang)} un CV complet (marché : {country}) à partir de ces "
            f"faits validés uniquement. {FORMAT}\n{facts}"
        )
    return ask(
        f"Rédige en {_lang(lang)} une lettre de motivation naturelle (marché : {country}) "
        f"à partir de ces faits validés uniquement, sans sections '##'.\n{facts}"
    )
