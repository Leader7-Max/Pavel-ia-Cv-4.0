Parfait. Là j’ai ton vrai app.py, donc je peux améliorer le design sans supprimer tes fonctions ai.py, exporters.py, config.py, ni ton système de navigation.
Je vais conserver :
toutes les pages actuelles ;
CV en 4 étapes ;
lettres ;
analyse ATS ;
adaptation à une offre ;
traduction ;
CV Express ;
Mes documents ;
exports PDF / Word / TXT ;
session et sauvegarde des documents.
Je vais surtout remplacer la couche visuelle par un design Pavel IA CV Pro beaucoup plus premium, mobile-first, avec cartes, halos lumineux, boutons modernes, navigation visuelle, animations et meilleur affichage des résultats.
Voici le app.py complet à remplacer dans GitHub :
Écriture
"""PAVEL IA CV PRO — application Streamlit premium, moderne et mobile-first."""
import datetime import re
import streamlit as st
import ai import exporters from config import COUNTRIES, CV_TYPES, LANGS, LEVELS, TEMPLATES, has
============================================================
CONFIGURATION
============================================================
st.set_page_config( page_title="Pavel IA CV Pro", page_icon="✨", layout="centered", initial_sidebar_state="collapsed", )
============================================================
DESIGN SYSTEM
============================================================
st.markdown( """
�
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'); :root { --bg: #070914; --panel: #101528; --panel-2: #141a31; --primary: #7c5cff; --primary-2: #9b87ff; --cyan: #31d9ff; --green: #39df9b; --text: #f7f8ff; --muted: #9da6c2; --border: rgba(255,255,255,0.09); } html, body, [class*="css"] { font-family: "Inter", sans-serif; } .stApp { background: radial-gradient( circle at 8% 5%, rgba(124,92,255,0.20), transparent 28% ), radial-gradient( circle at 95% 15%, rgba(49,217,255,0.12), transparent 24% ), radial-gradient( circle at 50% 100%, rgba(124,92,255,0.10), transparent 32% ), var(--bg); color: var(--text); } #MainMenu { visibility: hidden; } footer { visibility: hidden; } header { background: transparent !important; } .block-container { max-width: 960px; padding-top: 1.2rem; padding-bottom: 3rem; } /* ============================================================ TOP BAR ============================================================ */ .topbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px; } .brand { display: flex; align-items: center; gap: 10px; font-weight: 800; letter-spacing: -0.5px; } .brand-icon { width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; border-radius: 12px; background: linear-gradient(135deg, #7c5cff, #31d9ff); box-shadow: 0 8px 25px rgba(124,92,255,0.25); font-size: 19px; } .brand-name { font-size: 16px; } .brand-pro { color: var(--cyan); } /* ============================================================ HERO ============================================================ */ .hero { position: relative; overflow: hidden; padding: 38px 24px 34px; border-radius: 28px; margin-bottom: 18px; text-align: center; background: linear-gradient( 135deg, rgba(124,92,255,0.24), rgba(49,217,255,0.07) ), rgba(15,20,39,0.82); border: 1px solid rgba(255,255,255,0.10); box-shadow: 0 25px 80px rgba(0,0,0,0.32), inset 0 1px 0 rgba(255,255,255,0.06); backdrop-filter: blur(18px); } .hero::before { content: ""; position: absolute; width: 280px; height: 280px; border-radius: 50%; background: rgba(124,92,255,0.19); filter: blur(80px); right: -110px; top: -130px; animation: glowMove 7s ease-in-out infinite alternate; } .hero::after { content: ""; position: absolute; width: 220px; height: 220px; border-radius: 50%; background: rgba(49,217,255,0.10); filter: blur(75px); left: -100px; bottom: -120px; animation: glowMove2 8s ease-in-out infinite alternate; } .hero-content { position: relative; z-index: 2; } .hero-badge { display: inline-flex; align-items: center; gap: 7px; padding: 8px 13px; border-radius: 999px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.09); color: #d9d5ff; font-size: 12px; font-weight: 700; margin-bottom: 16px; } .hero h1 { margin: 0; font-size: clamp(42px, 10vw, 70px); line-height: 0.96; letter-spacing: -3px; font-weight: 800; } .gradient-text { background: linear-gradient( 90deg, #ffffff, #9c89ff, #4ee8ff ); -webkit-background-clip: text; -webkit-text-fill-color: transparent; } .hero p { max-width: 650px; margin: 18px auto 0; color: var(--muted); line-height: 1.65; font-size: 15px; } .hero-line { width: 70px; height: 3px; border-radius: 20px; margin: 20px auto 0; background: linear-gradient(90deg, #7c5cff, #31d9ff); box-shadow: 0 0 20px rgba(49,217,255,0.30); } /* ============================================================ CARDS ============================================================ */ .glass-card { background: linear-gradient( 145deg, rgba(255,255,255,0.055), rgba(255,255,255,0.025) ); border: 1px solid var(--border); border-radius: 22px; padding: 22px; margin-bottom: 16px; box-shadow: 0 18px 50px rgba(0,0,0,0.20), inset 0 1px 0 rgba(255,255,255,0.035); backdrop-filter: blur(14px); } .section-title { font-size: 18px; font-weight: 800; margin-bottom: 5px; color: #ffffff; } .section-subtitle { color: var(--muted); font-size: 13px; line-height: 1.6; } /* ============================================================ HOME FEATURES ============================================================ */ .feature-card { min-height: 145px; padding: 19px; border-radius: 20px; background: rgba(255,255,255,0.035); border: 1px solid rgba(255,255,255,0.075); transition: transform 0.25s ease, border-color 0.25s ease; } .feature-card:hover { transform: translateY(-3px); border-color: rgba(124,92,255,0.28); } .feature-icon { font-size: 25px; margin-bottom: 9px; } .feature-title { font-size: 14px; font-weight: 750; margin-bottom: 6px; } .feature-text { color: var(--muted); font-size: 12px; line-height: 1.55; } /* ============================================================ METRICS ============================================================ */ .metric-card { text-align: center; padding: 17px; border-radius: 18px; background: rgba(255,255,255,0.035); border: 1px solid rgba(255,255,255,0.075); } .metric-number { font-size: 26px; font-weight: 800; background: linear-gradient(90deg, #ffffff, #8e7aff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; } .metric-label { color: var(--muted); font-size: 12px; margin-top: 3px; } /* ============================================================ STEPPER ============================================================ */ .stepper { display: flex; align-items: center; gap: 5px; margin: 15px 0 7px; } .step { flex: 1; height: 6px; border-radius: 20px; background: rgba(255,255,255,0.08); } .step.active { background: linear-gradient(90deg, #7c5cff, #31d9ff); box-shadow: 0 0 14px rgba(124,92,255,0.30); } .step-text { color: var(--muted); font-size: 12px; text-align: center; margin-bottom: 18px; } /* ============================================================ INPUTS ============================================================ */ div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] { background: rgba(255,255,255,0.035) !important; border-radius: 13px !important; } input, textarea { color: #ffffff !important; } label { color: #dce2f5 !important; font-weight: 600 !important; font-size: 13px !important; } [data-baseweb="select"] { border-color: rgba(255,255,255,0.08) !important; } /* ============================================================ BUTTONS ============================================================ */ .stButton > button, .stDownloadButton > button { width: 100%; min-height: 3.05rem; border-radius: 14px; border: 1px solid rgba(255,255,255,0.08); font-weight: 750; font-size: 0.92rem; color: #ffffff; background: linear-gradient( 135deg, rgba(124,92,255,0.96), rgba(91,67,219,0.96) ); box-shadow: 0 9px 25px rgba(124,92,255,0.18); transition: transform 0.20s ease, box-shadow 0.20s ease, filter 0.20s ease; } .stButton > button:hover, .stDownloadButton > button:hover { transform: translateY(-2px); filter: brightness(1.08); box-shadow: 0 14px 32px rgba(124,92,255,0.30); } .stButton > button:active, .stDownloadButton > button:active { transform: translateY(0); } /* ============================================================ RESULTATS ============================================================ */ .result-card { border-radius: 20px; padding: 19px; margin-top: 18px; background: linear-gradient( 135deg, rgba(57,223,155,0.08), rgba(49,217,255,0.035) ); border: 1px solid rgba(57,223,155,0.16); } .result-title { font-size: 16px; font-weight: 800; color: #eafff6; } /* ============================================================ INFO / PRIVACY ============================================================ */ .privacy { padding: 17px; border-radius: 17px; background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.06); color: var(--muted); font-size: 12px; line-height: 1.7; } /* ============================================================ FOOTER ============================================================ */ .footer { text-align: center; color: #6f7790; font-size: 11px; padding: 25px 0 5px; } /* ============================================================ ANIMATIONS ============================================================ */ @keyframes glowMove { from { transform: translate(0, 0); } to { transform: translate(-35px, 25px); } } @keyframes glowMove2 { from { transform: translate(0, 0); } to { transform: translate(30px, -20px); } } /* ============================================================ MOBILE ============================================================ */ @media (max-width: 640px) { .block-container { padding-left: 0.8rem; padding-right: 0.8rem; padding-top: 0.8rem; } .hero { padding: 32px 18px; border-radius: 23px; } .hero h1 { font-size: 48px; letter-spacing: -2.5px; } .hero p { font-size: 14px; } .glass-card { padding: 18px; border-radius: 19px; } .stButton > button, .stDownloadButton > button { min-height: 3.2rem; } } 
""", unsafe_allow_html=True, )
============================================================
SESSION STATE
============================================================
ss = st.session_state
ss.setdefault("page", "home") ss.setdefault("step", 1) ss.setdefault("cv", {}) ss.setdefault("docs", [])
CV_KEYS = [ "prenom", "nom", "tel", "email", "ville", "pays", "linkedin", "cvtype", "sector", "poste", "level", "target_country", "target_city", "lang", "experiences", "formation", "skills", "languages", "extras", ]
============================================================
UTILITAIRES
============================================================
def sync(): for key in CV_KEYS: widget_key = "w_" + key if widget_key in ss: ss.cv[key] = ss[widget_key]
def go(page): ss.page = page
def setstep(number): sync() ss.step = number
def run_ai(fn, *args): try: with st.spinner("✨ Pavel IA travaille..."): return fn(*args)
except ai.AIError as error:
    st.error(str(error))

except Exception:
    st.error(
        "Une erreur inattendue est survenue. "
        "Réessayez dans un instant."
    )

return None
============================================================
HEADER
============================================================
def top(title):
st.markdown(
    """
    <div class="topbar">
        <div class="brand">
            <div class="brand-icon">✨</div>
            <div class="brand-name">
                PAVEL IA <span class="brand-pro">CV PRO</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.button(
    "← Accueil",
    on_click=go,
    args=("home",),
    key="back_" + ss.page,
)

st.markdown(
    f"""
    <div class="glass-card">
        <div class="section-title">{title}</div>
        <div class="section-subtitle">
            Pavel IA vous accompagne pour créer un document
            professionnel adapté à votre objectif.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not has(ss.page):
    st.info(
        "Cette fonctionnalité fait partie de l'offre Premium "
        "(bientôt disponible)."
    )
    st.stop()
============================================================
CHAMPS
============================================================
def field(label, key, area=False, ph=""):
fn = st.text_area if area else st.text_input

ss.cv[key] = fn(
    label,
    value=ss.cv.get(key, ""),
    placeholder=ph,
    key="w_" + key,
)
def pick(label, key, options):
current = ss.cv.get(key, options[0])

index = (
    options.index(current)
    if current in options
    else 0
)

ss.cv[key] = st.selectbox(
    label,
    options,
    index=index,
    key="w_" + key,
)
============================================================
IMPORT CV
============================================================
def import_cv(key):
file = st.file_uploader(
    "📎 Importer votre CV — PDF, 5 Mo maximum",
    type=["pdf"],
    key="up_" + key,
)

if file is not None:

    signature = (file.name, file.size)

    if ss.get("last_" + key) != signature:

        text = run_ai(
            ai.pdf_text,
            file.getvalue(),
        )

        ss["last_" + key] = signature

        if text:
            ss["imp_" + key] = text

return st.text_area(
    "Texte du CV",
    height=210,
    key="imp_" + key,
    placeholder=(
        "Le texte importé apparaîtra ici. "
        "Vous pouvez également coller votre CV directement."
    ),
)
============================================================
DOCUMENTS
============================================================
def save_doc(kind, text, template, poste):
ss.docs.append(
    {
        "kind": kind,
        "text": text,
        "tpl": template,
        "poste": poste,
        "date": datetime.date.today().strftime("%d/%m/%Y"),
    }
)

st.toast("✅ Document enregistré dans Mes documents")
def downloads(text, template, base, key):
try:

    st.download_button(
        "⬇️ Télécharger en PDF",
        exporters.to_pdf(text, template),
        base + ".pdf",
        "application/pdf",
        key="pdf_" + key,
    )

    st.download_button(
        "⬇️ Télécharger en Word (.docx)",
        exporters.to_docx(text, template),
        base + ".docx",
        "application/vnd.openxmlformats-officedocument"
        ".wordprocessingml.document",
        key="docx_" + key,
    )

except Exception:
    st.error(
        "Export PDF/Word impossible avec ce texte. "
        "Vérifiez-le puis réessayez."
    )

st.download_button(
    "⬇️ Télécharger en TXT",
    exporters.to_txt(text),
    base + ".txt",
    "text/plain",
    key="txt_" + key,
)
def result_block(key, kind, poste=""):
if not ss.get(key):
    return

st.markdown(
    """
    <div class="result-card">
        <div class="result-title">
            ✨ Votre document est prêt
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.text_area(
    "Résultat — modifiable",
    key=key,
    height=380,
)

template = st.selectbox(
    "🎨 Choisir le modèle",
    list(TEMPLATES),
    key="tpl_" + key,
    format_func=lambda item: (
        f"{item} — {TEMPLATES[item]}"
    ),
)

st.caption(
    "⚠️ Relisez toujours le document : "
    "l'IA peut se tromper."
)

downloads(
    ss[key],
    template,
    f"{kind}_{datetime.date.today().isoformat()}".replace(
        " ",
        "_",
    ),
    key,
)

st.button(
    "💾 Enregistrer dans Mes documents",
    on_click=save_doc,
    args=(kind, ss[key], template, poste),
    key="save_" + key,
)
============================================================
ATS
============================================================
def show_ats(key):
result = ss.get(key)

if not result:
    return

st.markdown(
    """
    <div class="glass-card">
        <div class="section-title">
            📊 Compatibilité ATS indicative
        </div>
        <div class="section-subtitle">
            Estimation indicative, pas une garantie.
            Certains éléments graphiques complexes peuvent être
            moins bien interprétés par certains systèmes ATS.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

rest = []

for line in result.splitlines():

    match = re.match(
        r"^\s*(.+?)\s*\|\s*(\d{1,3})\s*\|\s*(.+)$",
        line,
    )

    if match:

        name = match.group(1)
        number = min(int(match.group(2)), 100)
        explanation = match.group(3)

        st.write(
            f"**{name}** — {number}/100"
        )

        st.progress(number / 100)

        st.caption(explanation)

    elif line.strip():

        rest.append(line)

if rest:
    st.markdown("\n\n".join(rest))
def ats_button(key, cv, offer=""):
if st.button(
    "📊 ANALYSER LA COMPATIBILITÉ ATS",
    key="ats_btn_" + key,
):

    if not cv.strip():

        st.warning(
            "Ajoutez d'abord le texte de votre CV."
        )

    else:

        ss["ats_" + key] = (
            run_ai(ai.ats, cv, offer)
            or ss.get("ats_" + key, "")
        )

show_ats("ats_" + key)
============================================================
PAGE ACCUEIL
============================================================
def home():
st.markdown(
    """
    <div class="hero">
        <div class="hero-content">

            <div class="hero-badge">
                ✨ INTELLIGENCE ARTIFICIELLE
            </div>

            <h1>
                <span class="gradient-text">
                    PAVEL IA
                </span>
            </h1>

            <p>
                Votre carrière commence par un CV professionnel.
                Créez, améliorez, adaptez et traduisez vos documents
                avec l'intelligence artificielle.
            </p>

            <div class="hero-line"></div>

        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

n_cv = sum(
    document["kind"].startswith("CV")
    for document in ss.docs
)

n_letters = sum(
    document["kind"] == "Lettre"
    for document in ss.docs
)

c1, c2 = st.columns(2)

with c1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-number">{n_cv}</div>
            <div class="metric-label">📄 Mes CV</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-number">{n_letters}</div>
            <div class="metric-label">✉️ Mes lettres</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

features = [
    (
        "📄",
        "CV professionnel",
        "Créez un CV structuré et adapté à votre objectif.",
    ),
    (
        "🎯",
        "CV sur mesure",
        "Adaptez votre candidature à une offre précise.",
    ),
    (
        "🤖",
        "Analyse IA",
        "Analysez votre CV et identifiez les points à améliorer.",
    ),
]

columns = st.columns(3)

for column, feature in zip(columns, features):

    icon, title, description = feature

    with column:

        st.markdown(
            f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">
                    {title}
                </div>
                <div class="feature-text">
                    {description}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")

st.markdown(
    """
    <div class="glass-card">
        <div class="section-title">
            🚀 Que souhaitez-vous faire ?
        </div>
        <div class="section-subtitle">
            Sélectionnez une fonctionnalité.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

actions = [
    ("📄 CRÉER MON CV", "cv"),
    ("✉️ MA LETTRE DE MOTIVATION", "letter"),
    ("🤖 ANALYSER MON CV", "analyze"),
    ("🎯 ADAPTER MON CV À UNE OFFRE", "adapt"),
    ("🌍 TRADUIRE MON CV", if st.button("🤖 ANALYSER", key="an_btn"):
        if len(cv.strip()) < 50:
            st.warning("Importez ou collez d'abord votre CV.")
        else:
            ss["an_res"] = run_ai(ai.analyze, cv) or ss.get("an_res", "")
    if ss.get("an_res"):
        st.markdown("### ANALYSE PAVEL IA")
        st.markdown(ss["an_res"])
        if st.button("✨ AMÉLIORER MON CV", key="imp_btn"):
            out = run_ai(ai.improve_cv, cv, ss["an_res"])
            if out:
                ss["imp_out"] = out
    result_block("imp_out", "CV amélioré")
    ats_button("an", cv)


def page_adapt():
    top("Adapter mon CV à une offre")
    cv = import_cv("ad")
    offer = st.text_area("Collez l'annonce", height=180, key="ad_offer")
    ready = len(cv.strip()) >= 50 and len(offer.strip()) >= 30
    if st.button("🔎 COMPARER CV ↔ OFFRE", key="ad_cmp"):
        if not ready:
            st.warning("Ajoutez votre CV et l'annonce.")
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
    result_block("tr_out", "CV traduit")


def page_express():
    top("CV Express")
    st.caption("Décrivez votre situation librement. L'IA extrait les faits, vous les corrigez, "
               "puis elle génère vos documents sans rien inventer.")
    free = st.text_area("Votre texte libre", height=160, key="ex_text",
                        placeholder="Je cherche un emploi de préparateur de commande à Lyon...")
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
        if st.button("✉️ GÉNÉRER MA LETTRE", key="ex_l_btn"):
            out = run_ai(ai.from_facts, facts, "Lettre", lang, country)
            if out:
                ss["ex_letter"] = out
    result_block("ex_cv", "CV")
    result_block("ex_letter", "Lettre")


def reuse(i):
    d = ss.docs[i]
    ss["cv_out"] = d["text"]
    ss.page = "cv"
    ss.step = 4


def page_docs():
    top("Mes documents")
    st.caption("Conservés pendant votre session uniquement : téléchargez ce que vous voulez garder.")
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
