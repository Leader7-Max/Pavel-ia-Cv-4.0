"""Appels Gemini (REST) et extraction de texte PDF."""
import io
import json
import re
import unicodedata

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
    "Format de sortie : texte brut. Ligne 1 = PRÉNOM NOM ; ligne 2 = titre du poste ; ligne 3 = "
    "coordonnées complètes (téléphone | e-mail | adresse | liens) séparées par « | » ; puis des "
    "sections '## Titre' avec des puces '- '. Pas de gras, pas de tableau. N'omets AUCUNE coordonnée "
    "fournie (téléphone, e-mail, adresse, liens)."
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


def build_header(d):
    """En-tête du CV (nom, titre, coordonnées) construit par le code : jamais oublié par l'IA."""
    g = lambda k: str(d.get(k) or "").strip()
    name = " ".join(x for x in (g("prenom"), g("nom").upper()) if x)
    place = ", ".join(x for x in (g("ville"), g("pays")) if x)
    loc = ", ".join(x for x in (g("address"), place) if x)
    contacts = [c for c in (g("tel"), g("email"), loc, g("linkedin"), g("website")) if c]
    return "\n".join(x for x in (name, g("poste"), " | ".join(contacts)) if x)


def make_cv(d):
    body_data = {k: v for k, v in d.items() if k not in ("tel", "email", "address", "website", "linkedin")}
    body = ask(
        f"Rédige les SECTIONS d'un CV complet en {_lang(d.get('lang'))}, style « {d.get('cvtype', '')} », "
        f"pour le marché : {d.get('target_country', '')}. Adapte vocabulaire et structure sans prétendre "
        "qu'une convention est obligatoire. Données (JSON) :\n"
        f"{json.dumps(body_data, ensure_ascii=False)}\n"
        "N'écris PAS l'en-tête (nom, titre, coordonnées) : il est ajouté automatiquement. Commence "
        "directement par « ## Profil professionnel » (3 à 4 lignes basées uniquement sur ces faits), puis "
        "expériences, formation, compétences, langues, informations complémentaires. Pour chaque "
        "expérience : une ligne « Poste — Entreprise, Ville (période) » puis des puces '- '. Omet toute "
        "section vide. Format : texte brut, sections '## Titre', puces '- ', sans gras ni tableau."
    )
    i = body.find("## ")
    body = body[i:] if i >= 0 else body
    return build_header(d) + "\n" + body


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
        "Tu es un recruteur senior et coach carrière. Analyse ce CV avec un ton professionnel, direct "
        "et encourageant. Chaque point = UNE phrase concrète qui cite un élément précis du CV. Ne "
        "juge que ce qui est écrit : n'invente rien. Les suggestions proposent des reformulations "
        "utilisant uniquement les faits présents. Réponds en français, EXACTEMENT dans ce format :\n"
        "NOTE: <entier 0-100>\nVERDICT: <une phrase d'appréciation globale>\n"
        "CRITÈRES:\nStructure | <0-100> | <explication courte>\nProfil | <0-100> | <...>\n"
        "Expériences | <0-100> | <...>\nCompétences | <0-100> | <...>\nFormation | <0-100> | <...>\n"
        "Lisibilité | <0-100> | <...>\nPOINTS FORTS:\n- <3 à 4 points>\nÀ AMÉLIORER:\n- <3 à 5 points>\n"
        "SUGGESTIONS:\n- <3 à 5 actions concrètes, avec exemple de reformulation>\n"
        "INFORMATIONS MANQUANTES:\n- <coordonnées, sections ou données absentes ; écris « Aucune » si tout est là>\n"
        f"CV :\n{cv}"
    )


def improve_cv(cv, analysis=""):
    return ask(
        "Réécris ce CV en version améliorée, en corrigeant les faiblesses sans rien inventer, dans la "
        "même langue. Conserve EXACTEMENT le nom, le titre et toutes les coordonnées d'origine "
        f"(téléphone, e-mail, adresse, liens). {FORMAT}\n"
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
        "Adapte ce CV à l'offre : reformule et réordonne, utilise les mots-clés de l'offre uniquement "
        "pour des compétences DÉJÀ présentes dans le CV. N'ajoute aucune compétence absente. Conserve "
        "EXACTEMENT le nom, le titre et toutes les coordonnées d'origine. Même langue. "
        f"{FORMAT}\nOFFRE :\n{offer}\n\nCV :\n{cv}"
    )


def translate(text, lang):
    return ask(
        f"Traduis en {_lang(lang)} en conservant strictement le sens, les informations et la structure "
        "('##', puces). Ne traduis pas les noms propres, numéros de téléphone, e-mails, adresses et "
        "liens : recopie-les à l'identique. N'ajoute rien.\n" + text
    )


def extract(text):
    return ask(
        "Extrais du texte libre les faits fournis, sous forme de liste '- Clé : valeur' (nom, "
        "téléphone, e-mail, adresse, métier, expérience, compétences, permis, disponibilité, "
        "localisation, autres informations utiles). N'invente rien ; ignore ce qui n'est pas dit.\n" + text
    )


def from_facts(facts, kind, lang, country):
    if kind == "CV":
        return ask(
            f"Rédige en {_lang(lang)} un CV complet (marché : {country}) à partir de ces faits validés "
            "uniquement. Reprends toutes les coordonnées présentes dans les faits (téléphone, e-mail, "
            f"adresse, liens). {FORMAT}\n{facts}"
        )
    return ask(
        f"Rédige en {_lang(lang)} une lettre de motivation naturelle (marché : {country}) à partir de "
        f"ces faits validés uniquement, sans sections '##'.\n{facts}"
    )


# --- SUGGESTIONS INTELLIGENTES (sans inventer de faits) ---

def suggest_summary(poste, sector, level, experiences=""):
    return ask(
        "Rédige un profil professionnel de CV (3 à 4 lignes, texte brut, sans titre) en te "
        "basant UNIQUEMENT sur ces éléments fournis. N'invente ni années d'expérience, ni "
        "employeurs, ni compétences, ni chiffres.\n"
        f"Poste visé : {poste}\nSecteur : {sector}\nNiveau : {level}\n"
        f"Expériences fournies :\n{experiences}"
    )


def suggest_bullets(poste, experience_summary):
    return ask(
        "Reformule ces notes d'expérience en puces '- ' percutantes (verbes d'action) sans "
        "ajouter aucun fait, chiffre, résultat ou outil absent du texte. Conserve les blocs "
        f"(poste, entreprise, ville, période). Texte brut uniquement.\nPoste visé : {poste}\n"
        f"Notes :\n{experience_summary}"
    )


def suggest_skills(poste, sector):
    return ask(
        "Liste 10 à 12 compétences généralement attendues pour ce poste, en puces courtes "
        "'- '. Ce sont de simples SUGGESTIONS que le candidat devra vérifier.\n"
        f"Poste : {poste}\nSecteur : {sector}"
    )


# --- CONTACTS : garantie que les coordonnées ne sont jamais perdues ---
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?:\+|00)?\d[\d .()/-]{7,}\d")


def _is_contact_line(line):
    return "@" in line or " | " in line or sum(c.isdigit() for c in line) >= 6


def _header_lines(text):
    out = []
    for line in text.replace("\r", "").split("\n"):
        if line.strip().startswith("## "):
            break
        out.append(line)
    return out[:8]


def missing_contact(text):
    """Liste des coordonnées absentes de l'en-tête d'un CV ('e-mail', 'téléphone')."""
    head = "\n".join(_header_lines(text))
    miss = []
    if not _EMAIL.search(head):
        miss.append("e-mail")
    if not any(sum(c.isdigit() for c in m.group()) >= 9 for m in _PHONE.finditer(head)):
        miss.append("téléphone")
    return miss


def inject_contact(text, tel="", email="", address="", extra=""):
    """Réécrit l'en-tête du CV en y ajoutant les coordonnées fournies (sans doublon)."""
    lines = text.replace("\r", "").split("\n")
    cut = next((i for i, l in enumerate(lines) if l.strip().startswith("## ")), len(lines))
    head = [l.strip() for l in lines[:cut] if l.strip()]
    name = head[0] if head else ""
    others = head[1:]
    title = [l for l in others if not _is_contact_line(l)][:1]
    existing = []
    for l in others:
        if _is_contact_line(l):
            existing += [x.strip() for x in l.split("|") if x.strip()]
    new = [v.strip() for v in (tel, email, address, extra) if v and v.strip()]
    contacts = new + [c for c in existing if c not in new]
    new_head = [name] + title + ([" | ".join(contacts)] if contacts else [])
    return "\n".join([l for l in new_head if l] + lines[cut:])


# --- DÉTECTION DU TYPE DE DOCUMENT ---
KIND_LABELS = {"CV": "un CV", "LETTRE": "une lettre de motivation", "OFFRE": "une offre d'emploi",
               "AUTRE": "un autre type de document"}
_CV_WORDS = ("expérience", "experience", "formation", "compétence", "competence", "education", "skills",
             "profil", "profile", "langues", "languages", "diplôme", "parcours", "curriculum", "work history",
             "employment", "berufserfahrung", "ausbildung", "kenntnisse", "experiencia", "formación",
             "habilidades", "esperienza", "istruzione", "competenze", "centres d'intérêt", "certifications")
_LETTER_WORDS = ("madame, monsieur", "je me permets", "veuillez agréer", "cordialement", "je vous prie",
                 "dear sir", "dear hiring", "yours sincerely", "yours faithfully", "sehr geehrte",
                 "mit freundlichen", "estimado", "atentamente", "gentile", "distinti saluti", "objet :")
_OFFER_WORDS = ("nous recherchons", "nous offrons", "vous serez chargé", "vous serez en charge",
                "profil recherché", "type de contrat", "rémunération", "postuler", "avantages",
                "we are looking for", "job description", "responsibilities", "requirements",
                "what you will do", "about the role", "wir suchen", "stellenbeschreibung", "buscamos",
                "cerchiamo")
_DATE_RANGE = re.compile(r"(19|20)\d{2}\s*[-–—/àto]+\s*((19|20)\d{2}|présent|present|aujourd|actuel|en cours|heute|hoy|oggi)")


def _doc_scores(text):
    t = text[:8000].lower()
    cv = min(sum(w in t for w in _CV_WORDS), 6)
    cv += 1 if _EMAIL.search(t) else 0
    cv += 1 if any(sum(c.isdigit() for c in m.group()) >= 9 for m in _PHONE.finditer(t)) else 0
    cv += 2 if _DATE_RANGE.search(t) else 0
    return cv, sum(w in t for w in _LETTER_WORDS), sum(w in t for w in _OFFER_WORDS)


def detect_type(text):
    """Retourne (type, explication) avec type dans CV, LETTRE, OFFRE, AUTRE."""
    if len(text.strip()) < 150:
        return "AUTRE", "le texte est trop court pour être un CV complet."
    cv, letter, offer = _doc_scores(text)
    if cv >= 6 and letter < 2 and offer < 3:
        return "CV", "structure, coordonnées et périodes typiques d'un CV détectées."
    if letter >= 2 and cv < 6:
        return "LETTRE", "formules de politesse et ton épistolaire typiques d'une lettre de motivation."
    if offer >= 3 and cv < 6:
        return "OFFRE", "vocabulaire d'annonce (missions, profil recherché, contrat…)."
    if cv <= 2 and letter < 2 and offer < 3:
        return "AUTRE", "ni sections de CV (expérience, formation, compétences) ni coordonnées reconnues."
    try:
        raw = ask("Quel est le type de ce document ? Réponds uniquement par : TYPE | raison courte en "
                  "français. TYPE est exactement l'un de : CV, LETTRE, OFFRE, AUTRE.\n" + text[:5000])
        kind, _, why = raw.partition("|")
        kind = _norm(kind).upper().strip(" .*")
        if kind in KIND_LABELS:
            return kind, why.strip() or "analyse du contenu."
    except AIError:
        pass
    return ("CV", "probablement un CV (vérification IA indisponible).") if cv >= 4 else \
           ("AUTRE", "probablement pas un CV (vérification IA indisponible).")


def _norm(s):
    return unicodedata.normalize("NFD", str(s)).encode("ascii", "ignore").decode().lower()


# --- ANALYSE : lecture structurée de la réponse ---
def parse_analysis(raw):
    res = {"ok": False, "score": None, "verdict": "", "criteria": [], "strengths": [], "improve": [],
           "suggest": [], "missing": []}
    sec = None
    for line in str(raw).replace("**", "").splitlines():
        l = line.strip().lstrip("#").strip()
        if not l:
            continue
        n = _norm(l).rstrip(":").strip()
        m = re.match(r"^note(?: globale)?\s*:?\s*(\d{1,3})", n)
        if m:
            res["score"] = min(100, int(m.group(1)))
            continue
        if n.startswith("verdict"):
            res["verdict"] = l.split(":", 1)[1].strip() if ":" in l else ""
            continue
        key = None
        if n.startswith("criteres"):
            key = "criteria"
        elif n.startswith("points forts"):
            key = "strengths"
        elif n.startswith("a ameliorer") or n.startswith("points a ameliorer"):
            key = "improve"
        elif n.startswith("suggestions") or n.startswith("recommandations"):
            key = "suggest"
        elif n.startswith("informations manquantes"):
            key = "missing"
        if key and not (l.startswith("-") or "|" in l):
            sec = key
            continue
        if sec == "criteria":
            mm = re.match(r"^[-*\s]*(.+?)\s*\|\s*(\d{1,3})\s*\|\s*(.+)$", l)
            if mm:
                res["criteria"].append((mm.group(1).strip(), min(100, int(mm.group(2))), mm.group(3).strip()))
        elif sec:
            item = re.sub(r"^[-*•]\s*", "", l).strip()
            if item:
                res[sec].append(item)
    res["ok"] = res["score"] is not None and bool(res["strengths"] or res["improve"])
    return res


# --- COACH D'ENTRETIEN ---
def interview_questions(poste, company, kind, lang, cv, offer, n):
    return ask(
        f"Tu es un recruteur. Prépare exactement {n} questions d'entretien en {_lang(lang)} pour le poste "
        f"« {poste} »{' chez ' + company if company else ''}. Type d'entretien : {kind}. Personnalise-les "
        "avec le CV et l'offre fournis si présents. Réponds uniquement par une liste numérotée "
        f"(1. … 2. …), une question par ligne.\nOFFRE :\n{offer}\n\nCV :\n{cv}"
    )


def parse_questions(raw, n):
    qs = []
    for l in str(raw).splitlines():
        m = re.match(r"^\s*(?:\d+[.)]|[-*•])\s*(.+)$", l)
        if m and len(m.group(1).strip()) > 8:
            qs.append(m.group(1).replace("**", "").strip())
    return qs[:n]


def interview_feedback(question, answer, poste, kind, lang, cv):
    return ask(
        f"Tu es un coach d'entretien bienveillant mais exigeant. Poste visé : « {poste} ». Type : {kind}. "
        f"Évalue en {_lang(lang)} la réponse du candidat. Format EXACT :\nNOTE: <0-10>/10\n"
        "POINTS FORTS:\n- ...\nÀ AMÉLIORER:\n- ...\nRÉPONSE MODÈLE:\n<réponse structurée (méthode STAR si "
        "pertinent) construite UNIQUEMENT à partir de la réponse du candidat et du CV ; si un fait manque, "
        "écris [à compléter] au lieu de l'inventer>\n"
        f"QUESTION : {question}\nRÉPONSE DU CANDIDAT : {answer}\nCV :\n{cv}"
    )


def parse_note(raw):
    m = re.search(r"NOTE\s*:?\s*(\d{1,2})\s*/\s*10", str(raw), re.I)
    return min(10, int(m.group(1))) if m else None


def interview_summary(rows, poste, lang):
    detail = "\n\n".join(f"Q{i + 1}: {q}\nRéponse: {a}\nNote: {n}/10" for i, (q, a, n) in enumerate(rows))
    return ask(
        f"Rédige en {_lang(lang)} le bilan d'un entretien blanc pour le poste « {poste} » : appréciation "
        "globale en 2 phrases, 3 forces, 3 axes de progrès prioritaires, 3 conseils pratiques pour le "
        f"jour J. Reste factuel, sans rien inventer.\n{detail}"
    )


# --- LINKEDIN ---
def linkedin_profile(cv, goal, lang, tone):
    return ask(
        f"À partir de ce CV, rédige en {_lang(lang)} un profil LinkedIn optimisé, ton {tone}. Objectif "
        f"professionnel : {goal or 'non précisé'}. N'invente AUCUN fait, chiffre ou compétence ; mets "
        "[à compléter] si une information manque. Réponds avec ces sections exactes, au format "
        "'## Titre' : ## Titres du profil (3 propositions de 120 caractères max) ; ## À propos (résumé "
        "de 1 500 caractères max, à la première personne) ; ## Expériences (une rubrique prête à coller "
        "par expérience, avec puces) ; ## Compétences à ajouter (liste de 10 à 15 compétences issues du "
        "CV) ; ## Message d'accroche (3 lignes pour contacter un recruteur) ; ## Conseils (5 conseils "
        f"concrets de visibilité).\nCV :\n{cv}"
    )


def split_sections(raw):
    out, cur = [], None
    for line in str(raw).splitlines():
        if line.startswith("## "):
            cur = [line[3:].strip(), []]
            out.append(cur)
        elif cur is not None:
            cur[1].append(line)
    return [(t, "\n".join(b).strip()) for t, b in out]


def followup_mail(company, poste, days, lang):
    return ask(
        f"Rédige en {_lang(lang)} un court mail de relance poli et professionnel (5 lignes maximum, avec "
        f"objet) pour une candidature au poste « {poste} » chez {company}, envoyée il y a {days} jours. "
        "N'invente aucun fait."
    )
    
