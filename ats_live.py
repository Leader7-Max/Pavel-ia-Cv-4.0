"""Analyse ATS en direct : score, mots-clés trouvés/manquants et contrôles (sans appel IA, instantanée)."""
import re
import unicodedata

import streamlit as st

_STOP = """le la les un une des du de d l et ou à a au aux en dans par pour sur avec sans sous chez est sont
être avoir vous nous ils elles votre vos notre nos leur leurs ce cet cette ces qui que quoi dont où se sa son
ses ne pas plus très aussi comme mais donc or ni car si the an and of to in on for with without at by from is
are be have you we your our their this that these those who which what as it its not more very also but
poste entreprise offre profil missions mission recherchons recherche rejoindre équipe candidat candidats
cdi cdd temps plein partiel salaire expérience experience minimum idéalement serez serons h f hf""".split()
_SECTIONS = {
    "Profil": ("profil", "profile", "résumé", "resume", "summary", "objectif", "perfil", "profilo"),
    "Expérience": ("expérience", "experience", "parcours", "berufserfahrung", "experiencia", "esperienza"),
    "Formation": ("formation", "education", "diplôme", "ausbildung", "formación", "istruzione"),
    "Compétences": ("compétence", "competence", "skills", "kenntnisse", "habilidades", "competenze"),
    "Langues": ("langue", "language", "sprachen", "idiomas", "lingue"),
}
_DATES = re.compile(r"(19|20)\d{2}\s*[-–—/àto]+\s*((19|20)\d{2}|présent|present|aujourd|actuel|en cours|heute|hoy|oggi)",
                    re.I)
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?:\+|00)?\d[\d .()/-]{7,}\d")


def norm(word):
    w = unicodedata.normalize("NFD", str(word).lower()).encode("ascii", "ignore").decode()
    return w[:-1] if len(w) > 4 and w[-1] in "sx" else w


_STOPN = {norm(w) for w in _STOP}


def tokens(text):
    return [t.strip(".-") for t in re.findall(r"[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9+#.\-]+", text)]


def keywords(offer, n=20):
    """Mots-clés les plus significatifs d'une offre (fréquence, puis longueur)."""
    counts, shown = {}, {}
    for t in tokens(offer):
        k = norm(t)
        if len(k) < 3 or k.isdigit() or k in _STOPN:
            continue
        counts[k] = counts.get(k, 0) + 1
        shown.setdefault(k, t)
    return [shown[k] for k in sorted(counts, key=lambda k: (-counts[k], -len(k), k))[:n]]


def verdict(score):
    if score < 50:
        return "À renforcer : plusieurs éléments peuvent gêner la lecture par les ATS."
    if score < 75:
        return "Correct : quelques ajustements amélioreront nettement vos chances."
    return "Solide : votre CV est bien structuré et lisible par les ATS."


def analyze(cv, offer=""):
    low = cv.lower()
    cv_words = {norm(t) for t in tokens(cv)}
    cv_flat = unicodedata.normalize("NFD", low).encode("ascii", "ignore").decode()
    checks = []
    present = {}
    for name, words in _SECTIONS.items():
        present[name] = any(w in low for w in words)
        checks.append((f"Section « {name} »", present[name],
                       "présente" if present[name] else "à ajouter avec un titre explicite"))
    email = bool(_EMAIL.search(cv))
    phone = any(sum(c.isdigit() for c in m.group()) >= 9 for m in _PHONE.finditer(cv))
    checks.append(("E-mail", email, "présent" if email else "ajoutez une adresse e-mail dans l'en-tête"))
    checks.append(("Téléphone", phone, "présent" if phone else "ajoutez un numéro dans l'en-tête"))
    struct = round(100 * (sum(present.values()) + email + phone) / (len(present) + 2))
    words = len(cv.split())
    bullets = len(re.findall(r"^\s*[-•*]", cv, re.M))
    dates = bool(_DATES.search(cv))
    weird = len(re.findall(r"[│┃■□◆◇★☆✓✔►▶➤]", cv))
    lines = [l for l in cv.splitlines() if l.strip()]
    avg_len = sum(len(l) for l in lines) / max(len(lines), 1)
    read = 100
    for bad, pts, label, tip in (
            (words < 150, 30, "Longueur", "CV très court : développez expériences et compétences"),
            (words > 1000, 20, "Longueur", "CV très long : visez 1 à 2 pages"),
            (bullets == 0, 20, "Puces", "utilisez des puces pour lister missions et réalisations"),
            (not dates, 15, "Dates", "indiquez des périodes (ex. 2021 - 2024) pour chaque expérience"),
            (weird > 5, 15, "Symboles", "évitez les symboles décoratifs que certains ATS lisent mal"),
            (avg_len > 160, 10, "Lignes", "lignes trop longues : aérez et coupez en puces")):
        if bad:
            read -= pts
            checks.append((label, False, tip))
    for ok_label, ok in (("Puces", bullets > 0), ("Dates", dates)):
        if ok:
            checks.append((ok_label, True, "bien utilisées" if ok_label == "Puces" else "périodes détectées"))
    read = max(read, 0)
    found, missing, kw_score = [], [], None
    if offer.strip():
        kws = keywords(offer)
        for k in kws:
            nk = norm(k)
            (found if nk in cv_words or (len(nk) >= 5 and nk in cv_flat) else missing).append(k)
        kw_score = round(100 * len(found) / len(kws)) if kws else 0
        total = round(0.5 * kw_score + 0.3 * struct + 0.2 * read)
    else:
        total = round(0.6 * struct + 0.4 * read)
    parts = {"Structure": struct, "Lisibilité": read}
    if kw_score is not None:
        parts = {"Mots-clés": kw_score, **parts}
    return {"score": total, "parts": parts, "found": found, "missing": missing, "checks": checks}


def page(h):
    """Page Streamlit (h = outils partagés fournis par app.py)."""
    h.top("Score ATS en direct")
    st.caption("L'analyse se met à jour instantanément pendant que vous modifiez le texte. "
               "Estimation indicative : ce n'est pas une garantie de réussite ATS.")
    cv = h.import_cv("atsl")
    offer = st.text_area("Offre d'emploi (recommandé : calcule les mots-clés manquants)", height=150,
                         key="atsl_offer")
    if len(cv.strip()) < 50:
        st.info("Importez ou collez votre CV pour lancer l'analyse.")
        return
    if not h.cv_gate(cv, "atsl"):
        return
    r = analyze(cv, offer)
    h.ui.score(r["score"], verdict(r["score"]), "Compatibilité ATS indicative, calculée localement.")
    for label, n in r["parts"].items():
        st.write(f"**{label}** — {n}/100")
        st.progress(n / 100)
    if offer.strip():
        if r["found"]:
            st.success("**✅ Mots-clés trouvés dans votre CV**\n\n" + " · ".join(r["found"]))
        if r["missing"]:
            st.warning("**⚠️ Mots-clés de l'offre absents de votre CV**\n\n" + " · ".join(r["missing"]) +
                       "\n\nN'ajoutez que ceux qui correspondent à vos compétences réelles.")
    else:
        st.info("Collez l'offre d'emploi pour voir les mots-clés trouvés et manquants.")
    st.markdown("#### 🔎 Contrôles")
    st.markdown("\n".join(f"- {'✅' if ok else '⚠️'} **{label}** : {tip}" for label, ok, tip in r["checks"]))
    h.ats_button("atsl", cv, offer)
  
