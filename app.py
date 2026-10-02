"""PAVEL IA CV PRO — application Streamlit (mobile-first, design premium)."""
import datetime
import importlib
import re
import types

import streamlit as st

try:
    import ai
    import exporters
    from config import COUNTRIES, CV_TYPES, LANGS, LEVELS, TEMPLATES, has
except Exception as _err:  # fichier essentiel absent ou obsolète
    st.error(f"🛠️ Fichier essentiel manquant ou incorrect : {type(_err).__name__} : {_err}. "
             "Vérifiez que ai.py, config.py et exporters.py (et requirements.txt) sont bien dans GitHub, "
             "à jour, puis faites Reboot.")
    st.stop()

MISSING = []
PROBLEMS = []
REQUIRED = {
    "ui": ["inject_css", "hero", "badges", "stats", "section", "steps", "mini_logo"],
    "social": ["social_bar", "footer"],
    "vault": ["save", "panel", "tracker_load", "tracker_save"],
    "ats_live": ["page"],
    "interview_coach": ["page"],
    "linkedin_gen": ["page"],
    "tracker": ["page"],
}


class _Safe:
    """Charge un module optionnel. S'il manque ou est incorrect, l'app continue (fonction désactivée)
    et le problème est expliqué en haut de page."""

    def __init__(self, name):
        self._name = name
        self._mod = None
        try:
            self._mod = importlib.import_module(name)
        except ModuleNotFoundError as e:
            PROBLEMS.append(f"**{name}.py** est absent du dépôt GitHub ({e}).")
        except SyntaxError as e:
            PROBLEMS.append(f"**{name}.py** : erreur de syntaxe ligne {e.lineno} ({e.msg}). "
                            "Le fichier est mal collé ou incomplet.")
        except Exception as e:
            PROBLEMS.append(f"**{name}.py** : {type(e).__name__} : {e}")
        if self._mod is not None:
            absent = [a for a in REQUIRED.get(name, []) if not hasattr(self._mod, a)]
            if absent:
                first = (self._mod.__doc__ or "").strip().splitlines()[:1]
                PROBLEMS.append(f"**{name}.py** n'est pas la bonne version : il manque {', '.join(absent)}. "
                                f"Le fichier commence par « {first[0] if first else 'rien'} ». "
                                "Remplacez-le par celui de l'archive.")

    def __getattr__(self, attr):
        f = getattr(self._mod, attr, None) if self._mod is not None else None
        if f is None:
            return lambda *a, **k: False
        return f


social = _Safe("social")
ui = _Safe("ui")
vault = _Safe("vault")
ats_live = _Safe("ats_live")
interview_coach = _Safe("interview_coach")
linkedin_gen = _Safe("linkedin_gen")
tracker = _Safe("tracker")

st.set_page_config(page_title="Pavel IA CV Pro", page_icon="📄", layout="centered",
                   initial_sidebar_state="collapsed")

if PROBLEMS:
    st.error("🛠️ Le design est désactivé : corrigez ces fichiers dans GitHub puis faites Reboot.\n\n"
             + "\n\n".join("- " + p for p in PROBLEMS))

ui.inject_css()

ss = st.session_state
ss.setdefault("page", "home")
ss.setdefault("step", 1)
ss.setdefault("cv", {})
ss.setdefault("docs", [])

CV_KEYS = ["prenom", "nom", "tel", "email", "ville", "pays", "linkedin", "address", "website", "template", "cvtype", "sector",
           "poste", "level", "target_country", "target_city", "lang", "profile", "experiences",
           "formation", "skills", "languages", "extras"]
STEPS = ["Identité", "Poste visé", "Parcours", "Compétences"]


def sync():
    for k in CV_KEYS:
        if "w_" + k in ss:
            ss.cv[k] = ss["w_" + k]


def go(p):
    sync()
    ss.page = p


def setstep(n):
    sync()
    ss.step = n


def run_ai(fn, *args):
    try:
        with st.spinner("✨ Pavel IA analyse et rédige..."):
            return fn(*args)
    except ai.AIError as e:
        st.error(str(e))
    except Exception:
        st.error("Une erreur inattendue est survenue. Réessayez dans un instant.")
    return None


def celebrate(big=False):
    st.toast("Document prêt : relisez-le, puis téléchargez-le.", icon="✨")
    if big:
        st.balloons()


def text_counter(text, min_chars=0):
    chars = len(text)
    words = len(text.split()) if text.strip() else 0
    if min_chars and chars < min_chars:
        st.caption(f"✏️ {chars} caractères ({words} mots) — encore {min_chars - chars} recommandés")
    elif min_chars:
        st.caption(f"✅ {chars} caractères ({words} mots) — longueur suffisante")
    else:
        st.caption(f"📊 {chars} caractères ({words} mots)")


def top(title):
    st.button("← Accueil", on_click=go, args=("home",), key="back_" + ss.page)
    ui.mini_logo()
    st.subheader(title)
    if not has(ss.page):
        st.info("Cette fonctionnalité fait partie de l'offre Premium (bientôt disponible).")
        st.stop()


def field(label, key, area=False, ph=""):
    fn = st.text_area if area else st.text_input
    kw = {} if "w_" + key in ss else {"value": ss.cv.get(key, "")}
    ss.cv[key] = fn(label, placeholder=ph, key="w_" + key, **kw)


def pick(label, key, options, fmt=None):
    kw = {}
    if "w_" + key not in ss:
        cur = ss.cv.get(key, options[0])
        kw["index"] = options.index(cur) if cur in options else 0
    ss.cv[key] = st.selectbox(label, options, key="w_" + key, format_func=fmt or str, **kw)


# Callbacks des assistants IA (ils modifient les champs AVANT leur affichage)
def fill_profile():
    sync()
    c = ss.cv
    try:
        ss["w_profile"] = ai.suggest_summary(c.get("poste", ""), c.get("sector", ""),
                                             c.get("level", ""), c.get("experiences", ""))
        st.toast("✨ Profil rédigé — relisez-le et modifiez-le.", icon="🎯")
    except ai.AIError as e:
        st.toast(str(e))
    except Exception:
        st.toast("Fonction indisponible : mettez à jour ai.py.")


def improve_field(key, mode):
    txt = ss.get("w_" + key, "")
    if not txt.strip():
        st.toast("Écrivez d'abord quelques notes dans le champ.")
        return
    try:
        ss["w_" + key] = (ai.suggest_bullets(ss.cv.get("poste", ""), txt) if mode == "bullets"
                          else ai.improve(txt))
        st.toast("✨ Texte reformulé — vérifiez qu'il reste exact.", icon="🚀")
    except ai.AIError as e:
        st.toast(str(e))
    except Exception:
        st.toast("Fonction indisponible : mettez à jour ai.py.")


def fetch_skills():
    sync()
    try:
        ss["sugg_skills"] = ai.suggest_skills(ss.cv.get("poste", ""), ss.cv.get("sector", ""))
    except ai.AIError as e:
        st.toast(str(e))
    except Exception:
        st.toast("Fonction indisponible : mettez à jour ai.py.")


def import_cv(k):
    f = st.file_uploader("Importer votre CV (PDF, 5 Mo max)", type=["pdf"], key="up_" + k)
    if f is not None and ss.get("last_" + k) != (f.name, f.size):
        txt = run_ai(ai.pdf_text, f.getvalue())
        ss["last_" + k] = (f.name, f.size)
        if txt:
            ss["imp_" + k] = txt
    return st.text_area("Texte du CV (importé, modifiable, ou collez-le ici)", height=200,
                        key="imp_" + k)


def save_doc(kind, text, tpl, poste):
    ss.docs.append({"kind": kind, "text": text, "tpl": tpl, "poste": poste,
                    "date": datetime.date.today().strftime("%d/%m/%Y")})
    in_vault = vault.save(kind, poste, tpl, ss.docs[-1]["date"], text)
    st.toast("Enregistré dans votre coffre sécurisé !" if in_vault else
             "Enregistré pour cette session. Activez le coffre (Mes documents) pour le garder.",
             icon="🎉")


def downloads(txt, tpl, base, k):
    try:
        st.download_button("⬇️ Télécharger en PDF", exporters.to_pdf(txt, tpl), base + ".pdf",
                           "application/pdf", key="pdf_" + k)
        st.download_button(
            "⬇️ Télécharger en Word (.docx)", exporters.to_docx(txt, tpl), base + ".docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="docx_" + k)
    except Exception:
        st.error("Export PDF/Word impossible avec ce texte. Vérifiez-le puis réessayez.")
    st.download_button("⬇️ Télécharger en TXT", exporters.to_txt(txt), base + ".txt",
                       "text/plain", key="txt_" + k)


def apply_contact(k):
    ss[k] = ai.inject_contact(ss[k], ss.get("cc_tel_" + k, ""), ss.get("cc_mail_" + k, ""),
                              ss.get("cc_addr_" + k, ""))
    st.toast("Coordonnées ajoutées au CV.", icon="✅")


def contact_check(k):
    """Alerte (et correction en un clic) si l'en-tête du CV n'a ni téléphone ni e-mail."""
    text = ss.get(k, "")
    if "## " not in text or not hasattr(ai, "missing_contact"):
        return
    miss = ai.missing_contact(text)
    if not miss:
        return
    st.warning("⚠️ Coordonnées manquantes dans l'en-tête : " + " et ".join(miss) + ".")
    with st.expander("➕ Ajouter mes coordonnées", expanded=True):
        c = ss.cv
        st.text_input("Téléphone", value=c.get("tel", ""), key="cc_tel_" + k)
        st.text_input("E-mail", value=c.get("email", ""), key="cc_mail_" + k)
        st.text_input("Adresse ou ville", key="cc_addr_" + k,
                      value=", ".join(x for x in (c.get("address", ""), c.get("ville", "")) if x))
        st.button("✅ Insérer dans mon CV", on_click=apply_contact, args=(k,), key="cc_btn_" + k)


def cv_gate(cv, key):
    """Vérifie que le texte est bien un CV (CV, lettre, offre ou autre). True si l'on peut continuer."""
    if len(cv.strip()) < 50:
        return True
    sig = hash(cv)
    cache = ss.get("kind_" + key)
    if not cache or cache[0] != sig:
        res = run_ai(ai.detect_type, cv)
        if not res:
            return True
        cache = (sig, res[0], res[1])
        ss["kind_" + key] = cache
    _, kind, why = cache
    if kind == "CV":
        st.caption("✅ Document reconnu : c'est bien un CV.")
        return True
    label = ai.KIND_LABELS.get(kind, "un autre type de document")
    st.warning(f"📄 Ce document ressemble à **{label}**, pas à un CV : {why}")
    st.info({"LETTRE": "Pour une lettre, utilisez « Lettre de motivation » (ou « Traduire mon CV » pour la traduire).",
             "OFFRE": "Collez cette offre dans le champ « annonce » et importez votre vrai CV ici."}.get(
        kind, "Importez votre CV au format PDF, ou collez son texte, pour obtenir une analyse pertinente."))
    return st.checkbox("Continuer quand même avec ce document", key="force_" + key)


def show_analysis(raw):
    """Affiche l'analyse : score en anneau, critères, puis encadrés colorés. Texte brut si format inattendu."""
    parse = getattr(ai, "parse_analysis", None)
    a = parse(raw) if parse else {"ok": False}
    if not a.get("ok"):
        st.markdown(raw)
        return
    ui.score(a["score"], a["verdict"] or "Voici votre bilan.")
    if a["criteria"]:
        st.markdown("#### 📊 Détail par critère")
        for label, n, why in a["criteria"]:
            st.write(f"**{label}** : {n}/100")
            st.progress(n / 100)
            st.caption(why)
    bullets = lambda items: "\n".join("- " + x for x in items)
    if a["strengths"]:
        st.success("**✅ Points forts**\n\n" + bullets(a["strengths"]))
    if a["improve"]:
        st.warning("**⚠️ À améliorer**\n\n" + bullets(a["improve"]))
    if a["suggest"]:
        st.info("**💡 Suggestions concrètes**\n\n" + bullets(a["suggest"]))
    miss = [m for m in a["missing"] if m.lower().strip(" .") not in ("aucune", "aucun", "rien")]
    if miss:
        st.error("**📌 Informations manquantes**\n\n" + bullets(miss))


def result_block(k, kind, poste=""):
    if not ss.get(k):
        return
    st.text_area("Résultat (modifiable)", key=k, height=380)
    is_cv = kind.startswith("CV")
    if is_cv:
        contact_check(k)
    with st.expander("📋 Copier le texte"):
        st.code(ss[k], language="markdown")
    keys = list(TEMPLATES)
    default = ss.cv.get("template") if is_cv and ss.cv.get("template") in keys else keys[0]
    if is_cv:
        ui.template_gallery(ss.get("tpl_" + k, default))
    tpl = st.selectbox("Maquette de mise en page", keys, index=keys.index(default), key="tpl_" + k,
                       format_func=lambda t: f"{t} : {TEMPLATES[t]}")
    st.caption("💡 Relisez toujours le document avant de postuler : l'IA structure, vous validez.")
    downloads(ss[k], tpl, f"{kind}_{datetime.date.today().isoformat()}".replace(" ", "_"), k)
    st.button("💾 Enregistrer dans Mes documents", on_click=save_doc,
              args=(kind, ss[k], tpl, poste), key="save_" + k)


def show_ats(k):
    res = ss.get(k)
    if not res:
        return
    st.markdown("#### 📊 Compatibilité ATS indicative")
    st.caption("Estimation indicative, pas une garantie. Certains éléments graphiques "
               "complexes peuvent être moins bien interprétés par certains systèmes ATS.")
    rest = []
    for l in res.splitlines():
        m = re.match(r"^\s*(.+?)\s*\|\s*(\d{1,3})\s*\|\s*(.+)$", l)
        if m:
            n = min(int(m.group(2)), 100)
            st.write(f"**{m.group(1)}** — {n}/100")
            st.progress(n / 100)
            st.caption(m.group(3))
        elif l.strip():
            rest.append(l)
    if rest:
        st.markdown("\n\n".join(rest))


def ats_button(k, cv, offer=""):
    if st.button("📄 ANALYSE ATS", key="ats_btn_" + k):
        if not cv.strip():
            st.warning("Ajoutez d'abord le texte de votre CV.")
        else:
            ss["ats_" + k] = run_ai(ai.ats, cv, offer) or ss.get("ats_" + k, "")
    show_ats("ats_" + k)


# ---------------------------------------------------------------- pages
def home():
    ui.hero()
    ui.badges()
    n_cv = sum(d["kind"].startswith("CV") for d in ss.docs)
    n_l = sum(d["kind"] == "Lettre" for d in ss.docs)
    ui.stats(n_cv, n_l)
    social.social_bar()
    groups = [
        ("Créer", [("📄 CRÉER MON CV", "cv"), ("✉️ LETTRE DE MOTIVATION", "letter"), ("🚀 CV EXPRESS", "express")]),
        ("Optimiser", [("🤖 ANALYSER MON CV", "analyze"), ("🎯 ADAPTER À UNE OFFRE", "adapt"),
                       ("📊 SCORE ATS EN DIRECT", "ats"), ("🌍 TRADUIRE MON CV", "translate")]),
        ("Réussir", [("🎤 SIMULATION D'ENTRETIEN", "interview"), ("💼 PROFIL LINKEDIN", "linkedin"),
                     ("📌 SUIVI DES CANDIDATURES", "tracker")]),
        ("Mes documents", [("📁 MES DOCUMENTS", "docs")]),
    ]
    for title, items in groups:
        ui.section(title)
        for label, p in items:
            st.button(label, on_click=go, args=(p,), key="home_" + p)
    ui.steps()
    with st.expander("🔒 Confidentialité"):
        st.write("Vos informations sont utilisées pour générer et personnaliser vos documents. "
                 "Le contenu est envoyé au service IA (Gemini) pour la génération. Vos documents "
                 "ne sont conservés que pendant votre session, sauf si vous activez le coffre "
                 "personnel (sauvegarde chiffrée avec votre code).")


def page_cv():
    top("Créer mon CV")
    step = ss.step
    st.progress(step / 4)
    st.caption(f"Étape {step} sur 4 — {STEPS[step - 1]}")
    if step == 1:
        st.caption("Les champs * apparaîtront obligatoirement dans l'en-tête de votre CV.")
        for lab, key in [("Prénom *", "prenom"), ("Nom *", "nom"), ("Téléphone *", "tel"),
                         ("E-mail *", "email"), ("Adresse (rue, code postal)", "address"),
                         ("Ville *", "ville"), ("Pays", "pays"), ("LinkedIn (facultatif)", "linkedin"),
                         ("Site web (facultatif)", "website")]:
            field(lab, key)
    elif step == 2:
        pick("Type de CV", "cvtype", CV_TYPES)
        field("Secteur (personnalisable)", "sector")
        field("Poste recherché", "poste")
        pick("Niveau d'expérience", "level", LEVELS)
        pick("Pays ciblé", "target_country", COUNTRIES)
        field("Ville ciblée", "target_city")
        pick("Langue du CV", "lang", list(LANGS))
        pick("Maquette du CV", "template", list(TEMPLATES), lambda t: f"{t} : {TEMPLATES[t]}")
        ui.template_gallery(ss.cv.get("template", ""))
        field("Profil professionnel (modifiable, facultatif)", "profile", True)
        st.button("✨ Rédiger mon profil professionnel (IA)", on_click=fill_profile,
                  key="ai_sugg_summary")
    elif step == 3:
        field("Expériences (une par bloc : poste, entreprise, ville, période, missions, "
              "résultats)", "experiences", True)
        st.button("💡 Suggérer des missions percutantes (IA)", on_click=improve_field,
                  args=("experiences", "bullets"), key="ai_sugg_bullets")
        st.button("✨ Améliorer cette formulation (IA)", on_click=improve_field,
                  args=("experiences", "improve"), key="impr_exp")
        field("Formation (diplôme, établissement, ville, période)", "formation", True)
    else:
        field("Compétences (techniques, professionnelles, logiciels, outils)", "skills", True)
        st.button("💡 Voir des suggestions de compétences (IA)", on_click=fetch_skills,
                  key="ai_sugg_skills")
        if ss.get("sugg_skills"):
            st.info("Suggestions à vérifier : recopiez uniquement ce que vous maîtrisez vraiment.")
            st.markdown(ss["sugg_skills"])
        field("Langues et niveaux", "languages", True)
        field("Compléments (certifications, permis, disponibilité, mobilité, intérêts)",
              "extras", True)
    c1, c2 = st.columns(2)
    if step > 1:
        c1.button("← Précédent", on_click=setstep, args=(step - 1,), key="prev")
    if step < 4:
        c2.button("Suivant →", on_click=setstep, args=(step + 1,), key="next")
    if step == 4 and st.button("✨ GÉNÉRER MON CV", key="gen_cv"):
        sync()
        c = ss.cv
        miss = [lab for lab, ok in (("votre nom", c.get("nom") or c.get("prenom")),
                                    ("votre téléphone", c.get("tel")), ("votre e-mail", c.get("email")),
                                    ("votre ville ou adresse", c.get("ville") or c.get("address"))) if not ok]
        if miss:
            st.warning("Pour un CV complet, renseignez à l'étape 1 : " + ", ".join(miss) + ".")
        else:
            out = run_ai(ai.make_cv, dict(ss.cv))
            if out:
                ss["cv_out"] = out
                celebrate(True)
    result_block("cv_out", "CV", ss.cv.get("poste", ""))


def page_letter():
    top("Ma lettre de motivation")
    nom = st.text_input("Nom", key="lt_nom")
    poste = st.text_input("Poste recherché", key="lt_poste")
    ent = st.text_input("Entreprise", key="lt_ent")
    ville = st.text_input("Ville", key="lt_ville")
    annonce = st.text_area("Annonce complète", height=180, key="lt_annonce")
    exp = st.text_area("Votre expérience", key="lt_exp")
    comp = st.text_area("Vos compétences", key="lt_comp")
    dispo = st.text_input("Disponibilité", key="lt_dispo")
    tone = st.selectbox("Ton", ["Professionnel", "Chaleureux", "Dynamique", "Sobre"], key="lt_tone")
    length = st.selectbox("Longueur", ["Courte", "Moyenne", "Détaillée"], key="lt_len")
    lang = st.selectbox("Langue", list(LANGS), key="lt_lang")
    if st.button("✨ GÉNÉRER MA LETTRE", key="gen_letter"):
        if not (nom.strip() and poste.strip()):
            st.warning("Renseignez au moins votre nom et le poste.")
        else:
            d = {"nom": nom, "poste": poste, "entreprise": ent, "ville": ville,
                 "annonce": annonce, "experience": exp, "competences": comp,
                 "disponibilite": dispo, "tone": tone, "length": length, "lang": lang}
            out = run_ai(ai.make_letter, d)
            if out:
                ss["letter_out"] = out
                celebrate(True)
    result_block("letter_out", "Lettre", poste)


def page_analyze():
    top("Analyser mon CV")
    cv = import_cv("an")
    cv_ok = cv_gate(cv, "an")
    if st.button("🤖 LANCER L'ANALYSE", key="an_btn"):
        if len(cv.strip()) < 50:
            st.warning("Importez ou collez d'abord votre CV.")
        elif not cv_ok:
            st.warning("Cochez « Continuer
