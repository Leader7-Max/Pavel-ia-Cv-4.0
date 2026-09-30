"""PAVEL IA CV PRO — application Streamlit (mobile-first) ultra-moderne."""
import datetime
import re

import streamlit as st

import ai
import exporters
from config import COUNTRIES, CV_TYPES, LANGS, LEVELS, TEMPLATES, has

st.set_page_config(page_title="Pavel IA CV Pro", page_icon="📄", layout="centered",
                   initial_sidebar_state="collapsed")

# --- DESIGN CSS ULTRA-MODERNE & EFFETS VISUELS ---
st.markdown("""<style>
    /* Style global des boutons avec dégradés et ombres fluides */
    .stButton>button, .stDownloadButton>button {
        width: 100%;
        min-height: 3.2rem;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border-radius: 14px;
        border: none;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
        color: white;
    }
    /* Section Hero ultra-design */
    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #2563eb 100%);
        color: #fff;
        padding: 1.8rem;
        border-radius: 20px;
        margin-bottom: 1.2rem;
        text-align: center;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.15);
    }
    .hero h1 { margin: 0; font-size: 2.2rem; color: #fff; font-weight: 800; letter-spacing: -0.5px; }
    .hero p { margin: 0.4rem 0; opacity: 0.9; font-size: 1.05rem; }
    
    /* Arrondis modernes pour les champs de texte */
    .stTextInput>div>div>input, .stTextArea textarea, .stSelectbox>div>div>div {
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
    }
    /* Barre de progression élégante */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #1e3a8a, #3b82f6);
        border-radius: 10px;
    }
</style>""", unsafe_allow_html=True)

ss = st.session_state
ss.setdefault("page", "home")
ss.setdefault("step", 1)
ss.setdefault("cv", {})
ss.setdefault("docs", [])

CV_KEYS = ["prenom", "nom", "tel", "email", "ville", "pays", "linkedin", "cvtype", "sector",
           "poste", "level", "target_country", "target_city", "lang", "experiences",
           "formation", "skills", "languages", "extras"]


def sync():
    for k in CV_KEYS:
        if "w_" + k in ss:
            ss.cv[k] = ss["w_" + k]


def go(p):
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


def top(title):
    st.button("← Accueil", on_click=go, args=("home",), key="back_" + ss.page)
    st.subheader(title)
    if not has(ss.page):
        st.info("Cette fonctionnalité fait partie de l'offre Premium (bientôt disponible).")
        st.stop()


def field(label, key, area=False, ph=""):
    fn = st.text_area if area else st.text_input
    ss.cv[key] = fn(label, value=ss.cv.get(key, ""), placeholder=ph, key="w_" + key)


def pick(label, key, options):
    cur = ss.cv.get(key, options[0])
    idx = options.index(cur) if cur in options else 0
    ss.cv[key] = st.selectbox(label, options, index=idx, key="w_" + key)


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
    st.toast("💾 Document enregistré avec succès dans Mes documents !", icon="🎉")


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
    st.caption("Estimation indicative. Certains éléments graphiques complexes peuvent altérer la lecture ATS.")
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
    st.markdown('<div class="hero"><h1>PAVEL IA</h1><p>Votre carrière commence par un bon CV.</p><b>Créez. Améliorez. Adaptez. Postulez.</b></div>', unsafe_allow_html=True)
    n_cv = sum(d["kind"].startswith("CV") for d in ss.docs)
    n_l = sum(d["kind"] == "Lettre" for d in ss.docs)
    
    # Dashboard métriques moderne
    c1, c2 = st.columns(2)
    c1.metric("📄 CV créés", n_cv)
    c2.metric("✉️ Lettres prêtes", n_l)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    for label, p in [("📄 CRÉER MON CV", "cv"), ("✉️ MA LETTRE DE MOTIVATION", "letter"),
                     ("🤖 ANALYSER MON CV", "analyze"),
                     ("🎯 ADAPTER MON CV À UNE OFFRE", "adapt"), ("🌍 TRADUIRE MON CV", "translate"),
                     ("🚀 CV EXPRESS", "express"), ("📁 MES DOCUMENTS", "docs")]:
        st.button(label, on_click=go, args=(p,), key="home_" + p)
        
    with st.expander("🔒 Politique de Confidentialité & Sécurité"):
        st.write("Vos informations sont traitées de manière sécurisée uniquement pour générer vos documents professionnels. Aucune donnée personnelle n'est stockée de manière permanente après votre session.")


def page_cv():
    top("Créer mon CV")
    step = ss.step
    st.progress(step / 4)
    st.caption(f"Étape {step} sur 4")
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
    elif step == 3:
        field("Expériences (une par bloc : poste, entreprise, ville, période, missions, résultats)", "experiences", True)
        field("Formation (diplôme, établissement, ville, période)", "formation", True)
    else:
        field("Compétences (techniques, professionnelles, logiciels, outils)", "skills", True)
        field("Langues et niveaux", "languages", True)
        field("Compléments (certifications, permis, disponibilité, mobilité, intérêts)",
              "extras", True)
    if step == 3:
        def _improve():
            try:
                ss["w_experiences"] = ai.improve(ss.get("w_experiences", ""))
                st.toast("✨ Formulations optimisées !", icon="🚀")
            except ai.AIError as e:
                st.toast(str(e))
        st.button("✨ Améliorer cette formulation par l'IA", on_click=_improve,
                  key="impr_exp")
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
                st.balloons()  # Effet visuel Waouh de réussite
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
                st.balloons()
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
        st.markdown("### 📋 Bilan Pavel IA")
        st.markdown(ss["an_res"])
        if st.button("✨ GÉNÉRER LE CV CORRIGÉ", key="imp_btn"):
            out = run_ai(ai.improve_cv, cv, ss["an_res"])
            if out:
                ss["imp_out"] = out
                st.balloons()
    result_block("imp_out", "CV amélioré")
    ats_button("an", cv)


def page_adapt():
    top("Adapter mon CV à une offre")
    cv = import_cv("ad")
    offer = st.text_area("Collez l'annonce", height=180, key="ad_offer")
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
            st.caption(f"Taux de correspondance : {n} % — estimation indicative.")
        st.markdown(ss["ad_res"])
        if st.button("✨ GÉNÉRER LE CV ADAPTÉ", key="ad_gen"):
            out = run_ai(ai.adapt, cv, offer)
            if out:
                ss["ad_out"] = out
                st.balloons()
    result_block("ad_out", "CV adapté")
    ats_button("ad", cv, offer)


def page_translate():
    top("Traduire mon CV")
    txt = import_cv("tr")
    lang = st.selectbox("Traduire vers", list(LANGS), key="tr_lang")
    if st.button("🌍 TRADUIRE MAINTENANT", key="tr_btn"):
        if len(txt.strip()) < 20:
            st.warning("Importez ou collez d'abord le texte.")
        else:
            out = run_ai(ai.translate, txt, lang)
            if out:
                ss["tr_out"] = out
                st.balloons()
    result_block("tr_out", "CV traduit")


def page_express():
    top("CV Express")
    st.caption("Décrivez votre profil librement. L'IA extrait les faits clés pour rédiger vos documents instantanément.")
    free = st.text_area("Votre texte libre", height=160, key="ex_text",
                        placeholder="Ex: Je cherche un emploi de développeur web à Lyon, 3 ans d'expérience...")
    lang = st.selectbox("Langue", list(LANGS), key="ex_lang")
    country = st.selectbox("Pays ciblé", COUNTRIES, key="ex_country")
    if st.button("🔎 EXTRAIRE LES INFORMATIONS", key="ex_extract"):
        if len(free.strip()) < 20:
            st.warning("Écrivez quelques phrases de description.")
        else:
            out = run_ai(ai.extract, free)
            if out:
                ss["ex_facts"] = out
    if ss.get("ex_facts"):
        facts = st.text_area("Informations extraites (ajustez si besoin)", height=220,
                             key="ex_facts")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✨ GÉNÉRER LE CV", key="ex_cv_btn"):
                out = run_ai(ai.from_facts, facts, "CV", lang, country)
                if out:
                    ss["ex_cv"] = out
                    st.balloons()
        with col2:
            if st.button("✉️ GÉNÉRER LA LETTRE", key="ex_l_btn"):
                out = run_ai(ai.from_facts, facts, "Lettre", lang, country)
                if out:
                    ss["ex_letter"] = out
                    st.balloons()
    result_block("ex_cv", "CV")
    result_block("ex_letter", "Lettre")


def reuse(i):
    d = ss.docs[i]
    ss["cv_out"] = d["text"]
    ss.page = "cv"
    ss.step = 4


def page_docs():
    top("Mes documents")
    st.caption("📂 Conservés pendant votre session active : pensez à télécharger vos fichiers.")
    if not ss.docs:
        st.info("Aucun document enregistré pour l'instant.")
    for i in reversed(range(len(ss.docs))):
        d = ss.docs[i]
        with st.expander(f"{d['kind']} — {d['poste'] or 'sans titre'} — {d['date']}"):
            st.write(f"Modèle sélectionné : {d['tpl']}")
            downloads(d["text"], d["tpl"], f"{d['kind']}_{i}".replace(" ", "_"), f"doc{i}")
            if d["kind"].startswith("CV"):
                st.button("♻️ Réutiliser ce contenu", on_click=reuse, args=(i,), key=f"reuse{i}")


PAGES = {"home": home, "cv": page_cv, "letter": page_letter, "analyze": page_analyze,
         "adapt": page_adapt, "translate": page_translate, "express": page_express,
         "docs": page_docs}
PAGES.get(ss.page, home)()
