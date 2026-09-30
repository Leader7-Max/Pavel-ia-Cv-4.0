"""Identité visuelle : logo, en-tête et effets CSS sur mesure de Pavel IA CV 4.0."""
import streamlit as st

LOGO = ('<svg width="{s}" height="{s}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">'
        '<defs><linearGradient id="pg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#60a5fa"/>'
        '<stop offset="1" stop-color="#a78bfa"/></linearGradient></defs>'
        '<rect width="64" height="64" rx="18" fill="url(#pg)"/>'
        '<path d="M20 12h18l10 10v28a3 3 0 0 1-3 3H20a3 3 0 0 1-3-3V15a3 3 0 0 1 3-3z" fill="#fff"/>'
        '<path d="M38 12v10h10z" fill="#c7d2fe"/><rect x="23" y="29" width="18" height="3.2" rx="1.6" fill="#6366f1"/>'
        '<rect x="23" y="36" width="13" height="3.2" rx="1.6" fill="#a5b4fc"/>'
        '<rect x="23" y="43" width="16" height="3.2" rx="1.6" fill="#c7d2fe"/>'
        '<path d="M51 7l2 4.6L57.6 13.6 53 15.6 51 20.2 49 15.6 44.4 13.6 49 11.6z" fill="#fde68a"/></svg>')

_HOME = ["cv", "letter", "analyze", "adapt", "translate", "express", "docs"]
_COLORS = {"cv": "#2563eb,#1e40af", "letter": "#8b5cf6,#5b21b6", "analyze": "#06b6d4,#155e75",
           "adapt": "#ec4899,#9d174d", "translate": "#10b981,#065f46",
           "express": "#f59e0b,#b45309", "docs": "#64748b,#1e293b"}

CSS = """
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes glowBorder{0%,100%{border-color:rgba(99,102,241,.4);box-shadow:0 8px 25px rgba(15,23,42,.12)}50%{border-color:rgba(168,85,247,.8);box-shadow:0 8px 30px rgba(124,58,237,.25)}}
@keyframes bob{0%,100%{transform:translateY(0) rotate(-2deg)}50%{transform:translateY(-4px) rotate(2deg)}}
@keyframes shine{to{left:135%}}
@keyframes beat{0%,100%{transform:scale(1)}15%{transform:scale(1.06)}30%{transform:scale(1)}45%{transform:scale(1.06)}}

.stApp{background:radial-gradient(1100px 520px at 50% -10%,#e0e7ff 0%,#f8fafc 55%,#fff 100%)}
.block-container{max-width:760px;padding-top:1rem;animation:fadeUp .5s ease both}

/* En-tête compact et lumineux */
.hero{position:relative;overflow:hidden;background:rgba(15, 23, 42, 0.82);
 backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
 border:1.5px solid rgba(99,102,241,.4);animation:glowBorder 6s ease-in-out infinite;
 color:#fff;padding:0.9rem 1rem;border-radius:18px;margin-bottom:0.8rem;text-align:center;}

.hero .logo svg{animation:bob 4s ease-in-out infinite;filter:drop-shadow(0 4px 10px rgba(167,139,250,.5))}
.hero h1{margin:.1rem 0 0;font-size:1.55rem;color:#fff;font-weight:800;letter-spacing:-.5px}
.hero h1 span{background:linear-gradient(90deg,#93c5fd,#c4b5fd);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{margin:.2rem 0;opacity:.9;font-size:0.88rem}
.hero .badge{display:inline-block;margin-top:.25rem;padding:.2rem .7rem;border-radius:999px;
 background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);font-weight:600;font-size:0.75rem;}

.minilogo{display:flex;align-items:center;gap:.55rem;font-weight:800;color:#1e3a8a;margin:.2rem 0 .4rem}
.minilogo b{background:linear-gradient(90deg,#1e3a8a,#7c3aed);-webkit-background-clip:text;background-clip:text;color:transparent}

/* Boutons interactifs */
.stButton>button,.stDownloadButton>button{position:relative;overflow:hidden;width:100%;min-height:3.2rem;border:none;
 border-radius:14px;background:linear-gradient(135deg,#1e3a8a,#3b82f6);color:#fff;font-weight:700;font-size:0.95rem;
 box-shadow:0 5px 14px rgba(37,99,235,.2);transition:transform .2s ease,box-shadow .2s ease}
.stButton>button::after,.stDownloadButton>button::after{content:"";position:absolute;top:0;left:-75%;width:45%;height:100%;
 background:linear-gradient(120deg,transparent,rgba(255,255,255,.4),transparent);transform:skewX(-20deg)}
.stButton>button:hover::after,.stDownloadButton>button:hover::after{animation:shine .75s ease}
.stButton>button p,.stDownloadButton>button p{color:#fff!important}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-2px);filter:brightness(1.08);
 box-shadow:0 8px 20px rgba(124,58,237,.35);color:#fff}
.stButton>button:active{transform:scale(.97)}

[class*="st-key-home_"] button{min-height:3.4rem;font-size:1rem}
[class*="st-key-back_"] button{background:#fff;border:1px solid #cbd5e1;box-shadow:none;min-height:2.4rem}
[class*="st-key-back_"] button p{color:#1e293b!important}
.st-key-like_btn button{background:linear-gradient(135deg,#fb7185,#e11d48)}
.st-key-like_btn button:disabled{opacity:1;animation:beat 1.6s infinite}

[data-testid="stLinkButton"] a{display:flex;align-items:center;justify-content:center;min-height:2.8rem;border-radius:12px;
 font-weight:700;text-decoration:none;background:linear-gradient(135deg,#e0e7ff,#c7d2fe);color:#1e1b4b!important}

[class*="paypal"] a,.st-key-paypal_btn button{background:linear-gradient(135deg,#fde68a,#f59e0b)!important;color:#3b2300!important;min-height:3.2rem;font-weight:800}
.st-key-paypal_btn button p{color:#3b2300!important}

/* Cadres de statistiques ultra-compacts sur mesure */
[data-testid="stMetric"]{background:rgba(255,255,255,.9);backdrop-filter:blur(8px);border:1px solid #cbd5e1;
 border-radius:12px;padding:0.25rem 0.7rem !important;box-shadow:0 2px 8px rgba(15,23,42,.04);margin-bottom:-0.5rem;}
[data-testid="stMetricLabel"]{font-size:0.75rem !important;margin-bottom:-2px !important;}
[data-testid="stMetricValue"]{font-size:1.2rem !important;font-weight:800 !important;color:#1e3a8a !important;}

.stTextInput input,.stTextArea textarea,.stSelectbox [data-baseweb="select"]>div{border-radius:10px!important;
 border:1px solid #cbd5e1!important;background:#fff!important}
[data-testid="stExpander"]{border-radius:14px;border:1px solid #e2e8f0;background:rgba(255,255,255,.85)}

@keyframes bar{0%{background-position:0% 50%}100%{background-position:200% 50%}}
[data-testid="stDecoration"]{height:3px!important;background:linear-gradient(90deg,#2563eb,#7c3aed,#ec4899,#f59e0b,#2563eb)!important;background-size:200% 100%!important;animation:bar 1.6s linear infinite}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:14px;animation:fadeUp .4s ease both}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""


def inject_css():
    delays = "".join(
        f".st-key-home_{k} button{{background:linear-gradient(135deg,{_COLORS[k]})}}"
        f".st-key-home_{k}{{animation:fadeUp .55s {0.12 + i * 0.07:.2f}s ease both}}"
        for i, k in enumerate(_HOME))
    st.markdown("<style>" + CSS + delays + "</style>", unsafe_allow_html=True)


def hero():
    st.markdown('<div class="hero">'
                f'<div class="logo">{LOGO.format(s=44)}</div><h1>Pavel IA <span>CV 4.0</span></h1>'
                '<p>Votre carrière commence par un bon CV.</p>'
                '<span class="badge">Créez. Améliorez. Adaptez. Postulez.</span></div>',
                unsafe_allow_html=True)


def mini_logo():
    st.markdown(f'<div class="minilogo">{LOGO.format(s=26)}<span>Pavel IA <b>CV 4.0</b></span></div>',
                unsafe_allow_html=True)
