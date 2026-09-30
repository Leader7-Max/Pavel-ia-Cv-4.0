"""Appels Gemini (REST) et extraction de texte PDF."""
import io
import json

import requests
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


FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"]


def _models():
    raw = str(_secret("GEMINI_MODEL", "") or "").strip().strip("\"'").strip()
    if raw.startswith("models/"):
        raw = raw[len("models/"):]
    out = [raw] if raw else []
    return out + [m for m in FALLBACK_MODELS if m not in out]


def ask(prompt):
    key = str(_secret("GEMINI_API_KEY") or "").strip().strip("\"'").strip()
    if not key:
        raise AIError("Clé GEMINI_API_KEY absente : ajoutez-la dans Streamlit Secrets.")
    body = {
        "systemInstruction": {"parts": [{"text": RULES}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4},
    }
    r = None
    for model in _models():
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        try:
            r = requests.post(url, json=body, headers={"x-goog-api-key": key}, timeout=60)
        except requests.Timeout:
            raise AIError("Le service IA met trop de temps à répondre. Réessayez.")
        except requests.RequestException:
            raise AIError("Connexion au service IA impossible. Vérifiez votre réseau.")
        if r.status_code != 404:
            break
    if r.status_code == 404:
        raise AIError("Aucun modèle Gemini disponible (404). Vérifiez ou supprimez le secret "
                      "GEMINI_MODEL, ou utilisez un nom valide comme gemini-flash-latest.")
    if r.status_code == 429:
        raise AIError("Quota IA atteint. Réessayez dans quelques minutes.")
    if r.status_code in (400, 401, 403):
        raise AIError("Clé API refusée ou requête invalide. Vérifiez GEMINI_API_KEY.")
    if r.status_code != 200:
        raise AIError(f"Erreur du service IA ({r.status_code}). Réessayez.")
    try:
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, ValueError, TypeError):
        raise AIError("Réponse vide ou bloquée par l'IA. Reformulez votre demande.")
    if not text:
        raise AIError("Réponse vide de l'IA. Réessayez.")
    return text


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
    
