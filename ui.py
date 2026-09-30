"""Identité visuelle : logo, en-tête et effets CSS sur mesure de Pavel IA CV 4.0."""
import streamlit as st

LOGO = ('<svg width="{s}" height="{s}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">'
        '<defs><linearGradient id="pg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3b82f6"/>'
        '<stop offset="1" stop-color="#8b5cf6"/></linearGradient></defs>'
        '<rect width="64" height="64" rx="16" fill="url(#pg)"/>'
        '<path d="M20 14h16l8 8v26a2 2 0 0 1-2 2H20a2 2 0 0 1-2-2V16a2 2 0 0 1 2-2z" fill="#fff" opacity="0.95"/>'
        '<path d="M36 14v8h8z" fill="#cbd5e1"/><rect x="23" y="28" width="16" height="3" rx="1.5" fill="#4f46e5"/>'
        '<rect x="23" y="34" width="11" height="3" rx="1.5" fill="#818cf8"/>'
        '<rect x="23" y="40" width="14" height="3" rx="1.5" fill="#c7d2fe"/></svg>')

_HOME = ["cv", "letter", "analyze", "adapt", "translate", "express", "docs"]
_COLORS = {"cv": "#2563eb,#1e40af", "letter": "#8b5cf6,#5b21b6", "analyze": "#06b6d4,#155e75",
           "adapt": "#ec4899,#9d174d", "translate": "#10b981,#065f46",
           "express": "#f59e0b,#b45309", "docs": "#64748b,#1e293b"}

CSS = """
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.stApp{background:#f8fafc}
.block-container{max-width:720px;padding-top:0.5rem;animation:fadeIn .3s ease both}

/* En-tête minimaliste ultra-fin et élégant */
.hero-minimal{display:flex;align-items:center;gap:1rem;background:#fff;border:1px solid #e2e8f0;
 padding:0.75rem 1rem;border-radius:16px;margin-bottom:0.6rem;box-shadow:0 2px 6px rgba(0,0,0,.02)}
.hero-minimal .texts h1{margin:0;font-size:1.25rem;font-weight:800;color:#0f172a;letter-spacing:-.3px}
.hero-minimal .texts h1 span{color:#6366f1}
.hero-minimal .texts p{margin:0;font-size:0.8rem;color:#64748b}

.minilogo{display:flex;align-items:center;gap:.5rem;font-weight:800;color:#0f172a;margin:.2rem 0}
.minilogo b{color:#6366f1}

/* Boutons modernes ultra-plats et dynamiques */
.stButton>button,.stDownloadButton>button{width:100%;min-height:3rem;border:none;border-radius:12px;
 background:linear-gradient(135deg,#2563eb,#4f46e5);color:#fff;font-weight:700;font-size:0.9rem;
 box-shadow:0 4px 12px rgba(37,99,235,.15);transition:all .2s ease}
.stButton>button p,.stDownloadButton>button p{color:#fff!important}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-1px);filter:brightness(1.1);
 box-shadow:0 6px 16px rgba(79,70,229,.25)}

[class*="st-key-home_"] button{min-height:3.2rem}
[class*="st-key-back_"] button{background:#fff;border:1px solid #cbd5e1;box-shadow:none;min-height:2.2rem}
[class*="st-key-back_"] button p{color:#1e293b!important}
.st-key-like_btn button{background:linear-gradient(135deg,#fb7185,#e11d48)}

[data-testid="stLinkButton"] a{display:flex;align-items:center;justify-content:center;min-height:2.6rem;border-radius:10px;
 font-weight:700;text-decoration:none;background:#f1f5f9;color:#0f172a!important;border:1px solid #e2e8f0}

/* Cadres métriques (les 0) ultra-plats et discrets */
[data-testid="stMetric"]{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:0.2rem 0.6rem !important;box-shadow:none}
[data-testid="stMetricLabel"]{font-size:0.7rem !important;color:#64748b !important;text-transform:uppercase;letter-spacing:.5px}
[data-testid="stMetricValue"]{font-size:1.1rem !important;font-weight:800 !important;color:#0f172a !important}

.stTextInput input,.stTextArea textarea,.stSelectbox [data-baseweb="select"]>div{border-radius:10px!important;
 border:1px solid #cbd5e1!important;background:#fff!important}
[data-testid="stExpander"]{border-radius:12px;border:1px solid #e2e8f0;background:#fff}
[data-testid="stDecoration"]{height:2px!important;background:linear-gradient(90deg,#2563eb,#8b5cf6,#ec4899)!important}
"""


def inject_css():
    delays = "".join(
        f".st-key-home_{k} button{{background:linear-gradient(135deg,{_COLORS[k]})}}"
        for i, k in enumerate(_HOME))
    st.markdown("<style>" + CSS + delays + "</style>", unsafe_allow_html=True)


def hero():
    st.markdown('<div class="hero-minimal">'
                f'<div class="logo">{LOGO.format(s=38)}</div>'
                '<div class="texts"><h1>Pavel IA <span>CV 4.0</span></h1>'
                '<p>Votre carrière commence par un bon CV.</p></div></div>',
                unsafe_allow_html=True)


def mini_logo():
    st.markdown(f'<div class="minilogo">{LOGO.format(s=24)}<span>Pavel IA <b>CV 4.0</b></span></div>',
                unsafe_allow_html=True)
