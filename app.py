"""PAVEL IA CV PRO — application Streamlit (mobile-first, design premium)."""
import datetime
import re

import streamlit as st

import ai
import exporters
from config import COUNTRIES, CV_TYPES, LANGS, LEVELS, PAYPAL_URL, TEMPLATES, has

st.set_page_config(page_title="Pavel IA CV Pro", page_icon="📄", layout="centered",
                   initial_sidebar_state="collapsed")

st.markdown("""<style>
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes flow{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(245,158,11,.55)}50%{box-shadow:0 0 0 12px rgba(245,158,11,0)}}
.stApp{background:radial-gradient(1100px 520px at 50% -10%,#e0e7ff 0%,#f8fafc 55%,#fff 100%)}
.block-container{max-width:760px;padding-top:1.2rem;animation:fadeUp .5s ease both}
.hero{background:linear-gradient(120deg,#0f172a,#1e3a8a,#7c3aed,#2563eb);background-size:300% 300%;
 animation:flow 12s ease infinite;color:#fff;padding:2rem 1.4rem;border-radius:22px;margin-bottom:1.2rem;
 text-align:center;box-shadow:0 14px 34px rgba(30,58,138,.28)}
.hero h1{margin:0;font-size:2.5rem;color:#fff;font-weight:800;letter-spacing:-.5px}
.hero p{margin:.4rem 0;opacity:.92;font-size:1.05rem}
.hero .badge{display:inline-block;margin-top:.6rem;padding:.3rem .9rem;border-radius:999px;
 background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.3);font-weight:600;font-size:.9rem}
.stButton>button,.stDownloadButton>button{width:100%;min-height:3.3rem;border:none;border-radius:16px;
 background:linear-gradient(135deg,#1e3a8a,#3b82f6);color:#fff;font-weight:700;font-size:1rem;
 box-shadow:0 6px 16px rgba(37,99,235,.22);transition:transform .2s ease,box-shadow .2s ease,filter .2s ease}
.stButton>button p,.stDownloadButton>button p{color:#fff!important}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-2px);filter:brightness(1.08);
 box-shadow:0 10px 24px rgba(59,130,246,.38);color:#fff}
.stButton>button:active{transform:scale(.98)}
.st-key-home_cv button{background:linear-gradient(135deg,#2563eb,#1e40af)}
.st-key-home_letter button{background:linear-gradient(135deg,#8b5cf6,#5b21b6)}
.st-key-home_analyze button{background:linear-gradient(135deg,#06b6d4,#155e75)}
.st-key-home_adapt button{background:linear-gradient(135deg,#ec4899,#9d174d)}
.st-key-home_translate button{background:linear-gradient(135deg,#10b981,#065f46)}
.st-key-home_express button{background:linear-gradient(135deg,#f59e0b,#b45309)}
.st-key-home_docs button{background:linear-gradient(135deg,#64748b,#1e293b)}
[class*="st-key-home_"] button{min-height:3.7rem;font-size:1.05rem}
[class*="st-key-back_"] button{background:#fff;border:1px solid #cbd5e1;box-shadow:none;min-height:2.6rem}
[class*="st-key-back_"] button p{color:#1e293b!important}
[data-testid="stLinkButton"] a,[class*="st-key-paypal_btn"] button{display:flex;align-items:center;justify-content:center;
 min-height:3.4rem;border-radius:16px;font-weight:800;text-decoration:none;color:#3b2300!important;
 background:linear-gradient(135deg,#fde68a,#f59e0b);animation:pulse 2.4s infinite;border:none}
[class*="st-key-paypal_btn"] button p{color:#3b2300!important}
.support{background:linear-gradient(135deg,#fffbeb,#fef3c7);border:1px solid #fcd34d;border-radius:18px;
 padding:1rem 1.1rem;margin:.4rem 0 .7rem;color:#78350f;text-align:center}
[data-testid="stMetric"]{background:rgba(255,255,255,.8);backdrop-filter:blur(8px);border:1px solid #e2e8f0;
 border-radius:18px;padding:.8rem 1rem;box-shadow:0 4px 14px rgba(15,23,42,.06)}
.stTextInput input,.stTextArea textarea,.stSelectbox [data-baseweb="select"]>div{border-radius:12px!important;
 border:1px solid #cbd5e1!important;background:#fff!important}
.stTextInput input:focus,.stTextArea textarea:focus{border-color:#3b82f6!important;box-shadow:0 0 0 3px rgba(59,130,246,.2)!important}
.stProgress>div>div>div>div{background-image:linear-gradient(to right,#1e3a8a,#7c3aed);border-radius:10px}
[data-testid="stExpander"]{border-radius:16px;border:1px solid #e2e8f0;background:rgba(255,255,255,.75)}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>""", unsafe_allow_html=True)

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


def fetch_skills():
    sync()
    try:
        ss["sugg_skills"] = ai.suggest_skills(ss.cv.get("poste", ""), ss.cv.get("sector", ""))
    except ai.AIError as e:
        st.toast(str(e))


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
    st.toast("Document enregistré dans Mes documents !", icon="🎉")


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


def support_card():
    url = ""
    try:
        url = str(st.secrets.get("PAYPAL_URL", "") or "").strip()
    except Exception:
        pass
    url = url or PAYPAL_URL.strip()
    st.markdown('<div class="support"><b>💛 Pavel IA est gratuit</b><br>Il vous a été utile ? '
                'Un petit soutien aide à le faire grandir.</div>', unsafe_allow_html=True)
    if url.startswith("https://"):
        st.link_button("💛 SOUTENIR PAVEL IA VIA PAYPAL", url, use_container_width=True)
    else:
        st.button("💛 SOUTENIR VIA PAYPAL", key="paypal_btn",
                  on_click=lambda: st.toast("Le lien PayPal arrive bientôt. Merci ! 🙏"))


# ---------------------------------------------------------------- pages
def home():
    st.markdown('<div class="hero"><h1>PAVEL IA</h1><p>Votre carrière commence par un bon CV.</p>'
                '<span class="badge">Créez. Améliorez. Adaptez. Postulez.</span></div>',
                unsafe_allow_html=True)
    n_cv = sum(d["kind"].startswith("CV") for d in ss.docs)
    n_l = sum(d["kind"] == "Lettre" for d in ss.docs)
    c1, c2 = st.columns(2)
    c1.metric("📄 CV créés", n_cv)
    c2.metric("✉️ Lettres prêtes", n_l)
    st.write("")
    for label, p in [("📄 CRÉER MON CV", "cv"), ("✉️ MA LETTRE DE MOTIVATION", "letter"),
                     ("🤖 ANALYSER MON CV", "analyze"),
                     ("🎯 ADAPTER MON CV À UNE OFFRE", "adapt"), ("🌍 TRADUIRE MON CV", "translate"),
                     ("🚀 CV EXPRESS", "express"), ("📁 MES DOCUMENTS", "docs")]:
        st.button(label, on_click=go, args=(p,), key="home_" + p)
    with st.expander("🔒 Confidentialité"):
        st.write("Vos informations sont utilisées pour générer et personnaliser vos documents. "
                 "Le contenu est envoyé au service IA (Gemini) pour la génération. Vos documents "
                 "ne sont conservés que pendant votre session.")


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
                st.balloons()
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
        st.markdown("### 📋 ANALYSE PAVEL IA")
        st.markdown(ss["an_res"])
        if st.button("✨ AMÉLIORER MON CV", key="imp_btn"):
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
                st.balloons()
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
                st.balloons()
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
            if out:ss["ex_facts"] = out
    if ss.get("ex_facts"):
        facts = st.text_area("Informations extraites (corrigez avant de générer)", height=220,
                             key="ex_facts")
        if st.button("✨ GÉNÉRER MON CV", key="ex_cv_btn"):
            out = run_ai(ai.from_facts, facts, "CV", lang, country)
            if out:
                ss["ex_cv"] = out
                st.balloons()
        if st.button("✉️ GÉNÉRER MA LETTRE", key="ex_l_btn"):
            out = run_ai(ai.from_facts, facts, "Lettre", lang, country)
            if out:
                ss["ex_letter"] = out
                st.balloons()
    result_block("ex_cv", "CV")
    result_block("ex_letter", "Lettre")


def reuse(i):
    ss["cv_out"] = ss.docs[i]["text"]
    ss.page = "cv"
    ss.step = 4


def page_docs():
    top("Mes documents")
    st.caption("📂 Conservés pendant votre session uniquement : téléchargez ce que vous voulez garder.")
    if not ss.docs:
        st.info("Aucun document enregistré pour l'instant.")
    for i in reversed(range(len(ss.docs))):
        d = ss.docs[i]
        with st.expander(f"{d['kind']} — {d['poste'] or 'sans titre'} — {d['date']}"):
            st.write(f"Modèle : {d['tpl']}")
            downloads(d["text"], d["tpl"], f"{d['kind']}_{i}".replace(" ", "_"), f"doc{i}")
            if d["kind"].startswith("CV"):
                st.button("♻️ Réutiliser", on_click=reuse, args=(i,), key=f"reuse{i}")


PAGES = {"home": home, "cv": page_cv, "letter": page_letter, "analyze": page_analyze,
         "adapt": page_adapt, "translate": page_translate, "express": page_express,
         "docs": page_docs}
PAGES.get(ss.page, home)()
st.divider()
support_card()
  
