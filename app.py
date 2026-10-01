"""PAVEL IA CV PRO — application Streamlit (mobile-first, design premium)."""
import datetime
import importlib
import re

import streamlit as st

import ai
import exporters
from config import COUNTRIES, CV_TYPES, LANGS, LEVELS, TEMPLATES, has

MISSING = []


class _Safe:
    """Charge un module optionnel. S'il manque ou est obsolète, l'app continue (fonction désactivée)
    et le problème est signalé en bas de page."""

    def __init__(self, name):
        self._name = name
        try:
            self._mod = importlib.import_module(name)
        except Exception as e:
            self._mod = None
            MISSING.append(f"{name}.py introuvable ou en erreur ({type(e).__name__})")

    def __getattr__(self, attr):
        f = getattr(self._mod, attr, None) if self._mod else None
        if f is None:
            note = f"{self._name}.py à mettre à jour ({attr} absent)"
            if self._mod and note not in MISSING:
                MISSING.append(note)
            return lambda *a, **k: False
        return f


social = _Safe("social")
ui = _Safe("ui")
vault = _Safe("vault")

st.set_page_config(page_title="Pavel IA CV Pro", page_icon="📄", layout="centered",
                   initial_sidebar_state="collapsed")

ui.inject_css()

ss = st.session_state
ss.setdefault("page", "home")
ss.setdefault("step", 1)
ss.setdefault("cv", {})
ss.setdefault("docs", [])

CV_KEYS = ["prenom", "nom", "tel", "email", "ville", "pays", "linkedin", "cvtype", "sector",
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


def pick(label, key, options):
    kw = {}
    if "w_" + key not in ss:
        cur = ss.cv.get(key, options[0])
        kw["index"] = options.index(cur) if cur in options else 0
    ss.cv[key] = st.selectbox(label, options, key="w_" + key, **kw)


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


def result_block(k, kind, poste=""):
    if not ss.get(k):
        return
    st.text_area("Résultat (modifiable)", key=k, height=380)
    with st.expander("📋 Copier le texte"):
        st.code(ss[k], language="markdown")
    tpl = st.selectbox("Modèle de mise en page", list(TEMPLATES), key="tpl_" + k,
                       format_func=lambda t: f"{t} — {TEMPLATES[t]}")
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
    ui.section("Que souhaitez-vous faire ?")
    items = [("📄 CRÉER MON CV", "cv"), ("✉️ LETTRE DE MOTIVATION", "letter"),
             ("🤖 ANALYSER MON CV", "analyze"), ("🎯 ADAPTER À UNE OFFRE", "adapt"),
             ("🌍 TRADUIRE MON CV", "translate"), ("🚀 CV EXPRESS", "express"),
             ("📁 MES DOCUMENTS", "docs")]
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
        for lab, key in [("Prénom", "prenom"), ("Nom", "nom"), ("Téléphone", "tel"),
                         ("Email", "email"), ("Ville", "ville"), ("Pays", "pays"),
                         ("LinkedIn (facultatif)", "linkedin")]:
            field(lab, key)
    elif step == 2:
        pick("Type de CV", "cvtype", CV_TYPES)
        field("Secteur (personnalisable)", "sector")
        field("Poste recherché", "poste")
        pick("Niveau d'expérience", "level", LEVELS)
        pick("Pays ciblé", "target_country", COUNTRIES)
        field("Ville ciblée", "target_city")
        pick("Langue du CV", "lang", list(LANGS))
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
        if not (ss.cv.get("nom") or ss.cv.get("prenom")):
            st.warning("Renseignez au moins votre nom à l'étape 1.")
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
    if st.button("🤖 LANCER L'ANALYSE", key="an_btn"):
        if len(cv.strip()) < 50:
            st.warning("Importez ou collez d'abord votre CV.")
        else:
            ss["an_res"] = run_ai(ai.analyze, cv) or ss.get("an_res", "")
    if ss.get("an_res"):
        st.markdown("### 📋 ANALYSE PAVEL IA")
        st.markdown(ss["an_res"])
        if st.button("✨ AMÉLIORER MON CV", key="imp_btn"):
            out = run_ai(ai.improve_cv, cv, ss["an_res"])
            if out:
                ss["imp_out"] = out
                celebrate()
    result_block("imp_out", "CV amélioré")
    ats_button("an", cv)


def page_adapt():
    top("Adapter mon CV à une offre")
    cv = import_cv("ad")
    offer = st.text_area("Collez l'annonce", height=180, key="ad_offer")
    text_counter(offer, min_chars=30)
    ready = len(cv.strip()) >= 50 and len(offer.strip()) >= 30
    if st.button("🔎 COMPARER CV ↔ OFFRE", key="ad_cmp"):
        if not ready:
            st.warning("Ajoutez votre CV et l'annonce de l'offre.")
        else:
            ss["ad_res"] = run_ai(ai.match, cv, offer) or ss.get("ad_res", "")
    if ss.get("ad_res"):
        m = re.search(r"(\d{1,3})\s*%", ss["ad_res"])
        if m:
            n = min(int(m.group(1)), 100)
            st.progress(n / 100)
            st.caption(f"Correspondance : {n} % — estimation indicative, pas une garantie "
                       "d'embauche ni de réussite ATS.")
        st.markdown(ss["ad_res"])
        if st.button("✨ GÉNÉRER LE CV ADAPTÉ", key="ad_gen"):
            out = run_ai(ai.adapt, cv, offer)
            if out:
                ss["ad_out"] = out
                celebrate()
    result_block("ad_out", "CV adapté")
    ats_button("ad", cv, offer)


def page_translate():
    top("Traduire mon CV")
    txt = import_cv("tr")
    lang = st.selectbox("Traduire vers", list(LANGS), key="tr_lang")
    if st.button("🌍 TRADUIRE", key="tr_btn"):
        if len(txt.strip()) < 20:
            st.warning("Importez ou collez d'abord le texte.")
        else:
            out = run_ai(ai.translate, txt, lang)
            if out:
                ss["tr_out"] = out
                celebrate()
    result_block("tr_out", "CV traduit")


def page_express():
    top("CV Express")
    st.caption("Décrivez votre situation librement. L'IA extrait les faits, vous les corrigez, "
               "puis elle génère vos documents sans rien inventer.")
    free = st.text_area("Votre texte libre", height=160, key="ex_text",
                        placeholder="Je cherche un emploi de préparateur de commande à Lyon...")
    text_counter(free, min_chars=20)
    lang = st.selectbox("Langue", list(LANGS), key="ex_lang")
    country = st.selectbox("Pays ciblé", COUNTRIES, key="ex_country")
    if st.button("🔎 EXTRAIRE LES INFORMATIONS", key="ex_extract"):
        if len(free.strip()) < 20:
            st.warning("Écrivez quelques phrases sur vous.")
        else:
            out = run_ai(ai.extract, free)
            if out:
                ss["ex_facts"] = out
    if ss.get("ex_facts"):
        facts = st.text_area("Informations extraites (corrigez avant de générer)", height=220,
                             key="ex_facts")
        if st.button("✨ GÉNÉRER MON CV", key="ex_cv_btn"):
            out = run_ai(ai.from_facts, facts, "CV", lang, country)
            if out:
                ss["ex_cv"] = out
                celebrate()
        if st.button("✉️ GÉNÉRER MA LETTRE", key="ex_l_btn"):
            out = run_ai(ai.from_facts, facts, "Lettre", lang, country)
            if out:
                ss["ex_letter"] = out
                celebrate()
    result_block("ex_cv", "CV")
    result_block("ex_letter", "Lettre")


def reuse(i):
    ss["cv_out"] = ss.docs[i]["text"]
    ss.page = "cv"
    ss.step = 4


def page_docs():
    top("Mes documents")
    st.caption("📂 Cette liste disparaît quand vous actualisez la page. Pour retrouver vos documents à tout moment, activez le coffre personnel en bas de cette page.")
    if not ss.docs:
        st.info("Aucun document enregistré pour l'instant.")
    for i in reversed(range(len(ss.docs))):
        d = ss.docs[i]
        with st.expander(f"{d['kind']} — {d['poste'] or 'sans titre'} — {d['date']}"):
            st.write(f"Modèle : {d['tpl']}")
            downloads(d["text"], d["tpl"], f"{d['kind']}_{i}".replace(" ", "_"), f"doc{i}")
            if d["kind"].startswith("CV"):
                st.button("♻️ Réutiliser", on_click=reuse, args=(i,), key=f"reuse{i}")
    st.divider()
    vault.panel(downloads)


PAGES = {"home": home, "cv": page_cv, "letter": page_letter, "analyze": page_analyze,
         "adapt": page_adapt, "translate": page_translate, "express": page_express,
         "docs": page_docs}
PAGES.get(ss.page, home)()
st.divider()
social.footer(ss.page != "home")
if MISSING:
    st.warning("⚠️ Fichiers à vérifier dans GitHub : " + " · ".join(MISSING))
        
