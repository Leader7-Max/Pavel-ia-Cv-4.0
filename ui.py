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
@keyframes flow{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes pulseGlow{0%,100%{box-shadow:0 0 15px rgba(99,102,241,.4), 0 12px 25px rgba(30,58,138,.25)}50%{box-shadow:0 0 30px rgba(167,139,250,.7), 0 15px 30px rgba(30,58,138,.4)}}
@keyframes bob{0%,100%{transform:translateY(0) rotate(-2deg)}50%{transform:translateY(-6px) rotate(2deg)}}
@keyframes float{0%,100%{transform:translate(0,0)}50%{transform:translate(18px,-14px)}}
@keyframes shine{to{left:135%}}
@keyframes beat{0%,100%{transform:scale(1)}15%{transform:scale(1.06)}30%{transform:scale(1)}45%{transform:scale(1.06)}}

.stApp{background:radial-gradient(1100px 520px at 50% -10%,#e0e7ff 0%,#f8fafc 55%,#fff 100%)}
.block-container{max-width:760px;padding-top:1.2rem;animation:fadeUp .5s ease both}

/* Bannière principale avec effet de lueur sur mesure */
.hero{position:relative;overflow:hidden;background:linear-gradient(120deg,#0f172a,#1e3a8a,#7c3aed,#2563eb);
 background-size:300% 300%;animation:flow 12s ease infinite, pulseGlow 5s ease-in-out infinite;color:#fff;
 padding:1.2rem 1rem;border-radius:20px;margin-bottom:1rem;text-align:center;}
 
.hero .orb{position:absolute;border-radius:50%;filter:blur(34px);opacity:.6;animation:float 9s ease-in-out infinite}
.hero .o1{width:110px;height:110px;background:#ec4899;top:-30px;left:-20px}
.hero .o2{width:130px;height:130px;background:#22d3ee;bottom:-40px;right:-30px;animation-delay:-4s}
.hero>*:not(.orb){position:relative;z-index:1}
.hero .logo svg{animation:bob 4s ease-in-out infinite;filter:drop-shadow(0 8px 16px rgba(167,139,250,.6))}
.hero h1{margin:.2rem 0 0;font-size:1.8rem;color:#fff;font-weight:800;letter-spacing:-.5px}
.hero h1 span{background:linear-gradient(90deg,#fde68a,#f9a8d4);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{margin:.2rem 0;opacity:.93;font-size:0.95rem}
.hero .badge{display:inline-block;margin-top:.3rem;padding:.25rem .8rem;border-radius:999px;
 background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.35);font-weight:600;font-size:0.8rem;backdrop-filter:blur(6px)}

.minilogo{display:flex;align-items:center;gap:.55rem;font-weight:800;color:#1e3a8a;margin:.2rem 0 .4rem}
.minilogo b{background:linear-gradient(90deg,#1e3a8a,#7c3aed);-webkit-background-clip:text;background-clip:text;color:transparent}

/* Boutons interactifs avec effet néon et survol fluide */
.stButton>button,.stDownloadButton>button{position:relative;overflow:hidden;width:100%;min-height:3.3rem;border:none;
 border-radius:16px;background:linear-gradient(135deg,#1e3a8a,#3b82f6);color:#fff;font-weight:700;font-size:1rem;
 box-shadow:0 6px 16px rgba(37,99,235,.25);transition:transform .25s ease,box-shadow .25s ease,filter .25s ease}
.stButton>button::after,.stDownloadButton>button::after{content:"";position:absolute;top:0;left:-75%;width:45%;height:100%;
 background:linear-gradient(120deg,transparent,rgba(255,255,255,.45),transparent);transform:skewX(-20deg)}
.stButton>button:hover::after,.stDownloadButton>button:hover::after{animation:shine .75s ease}
.stButton>button p,.stDownloadButton>button p{color:#fff!important}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-3px);filter:brightness(1.1);
 box-shadow:0 10px 25px rgba(124,58,237,.45);color:#fff}
.stButton>button:active{transform:scale(.97)}

[class*="st-key-home_"] button{min-height:3.6rem;font-size:1.05rem;border: 1px solid rgba(255,255,255,0.2)}
[class*="st-key-back_"] button{background:#fff;border:1px solid #cbd5e1;box-shadow:none;min-height:2.6rem}
[class*="st-key-back_"] button p{color:#1e293b!important}
.st-key-like_btn button{background:linear-gradient(135deg,#fb7185,#e11d48)}
.st-key-like_btn button:disabled{opacity:1;animation:beat 1.6s infinite}

[data-testid="stLinkButton"] a{display:flex;align-items:center;justify-content:center;min-height:3rem;border-radius:14px;
 font-weight:700;text-decoration:none;background:linear-gradient(135deg,#e0e7ff,#c7d2fe);color:#1e1b4b!important;transition:transform .2s}
[data-testid="stLinkButton"] a:hover{transform:translateY(-2px)}

[class*="paypal"] a,.st-key-paypal_btn button{background:linear-gradient(135deg,#fde68a,#f59e0b)!important;color:#3b2300!important;
 min-height:3.4rem;font-weight:800}
.st-key-paypal_btn button p{color:#3b2300!important}

/* Blocs de statistiques modernes sur mesure */
[data-testid="stMetric"]{background:rgba(255,255,255,.85);backdrop-filter:blur(8px);border:1px solid #c7d2fe;
 border-radius:16px;padding:.6rem 1rem;box-shadow:0 4px 15px rgba(99,102,241,.08);transition:all .3s ease}
[data-testid="stMetric"]:hover{transform:translateY(-3px);border-color:#818cf8;box-shadow:0 6px 20px rgba(99,102,241,.18)}
[data-testid="stMetricValue"]{font-size:1.6rem !important; font-weight: 800; color: #1e3a8a;}

.stTextInput input,.stTextArea textarea,.stSelectbox [data-baseweb="select"]>div{border-radius:12px!important;
 border:1px solid #cbd5e1!important;background:#fff!important;transition:box-shadow .2s,border-color .2s}
.stTextInput input:focus,.stTextArea textarea:focus{border-color:#3b82f6!important;box-shadow:0 0 0 3px rgba(59,130,246,.22)!important}

[data-testid="stExpander"]{border-radius:16px;border:1px solid #e2e8f0;background:rgba(255,255,255,.85)}
@keyframes bar{0%{background-position:0% 50%}100%{background-position:200% 50%}}

[data-testid="stDecoration"]{height:4px!important;background:linear-gradient(90deg,#2563eb,#7c3aed,#ec4899,#f59e0b,#2563eb)!important;
 background-size:200% 100%!important;animation:bar 1.6s linear infinite}

[data-testid="stVerticalBlockBorderWrapper"]{border-radius:16px;animation:fadeUp .4s ease both}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""


def inject_css():
    delays = "".join(
        f".st-key-home_{k} button{{background:linear-gradient(135deg,{_COLORS[k]})}}"
        f".st-key-home_{k}{{animation:fadeUp .55s {0.12 + i * 0.07:.2f}s ease both}}"
        for i, k in enumerate(_HOME))
    st.markdown("<style>" + CSS + delays + "</style>", unsafe_allow_html=True)


def hero():
    st.markdown('<div class="hero"><div class="orb o1"></div><div class="orb o2"></div>'
                f'<div class="logo">{LOGO.format(s=56)}</div><h1>Pavel IA <span>CV 4.0</span></h1>'
                '<p>Votre carrière commence par un bon CV.</p>'
                '<span class="badge">Créez. Améliorez. Adaptez. Postulez.</span></div>',
                unsafe_allow_html=True)


def mini_logo():
    st.markdown(f'<div class="minilogo">{LOGO.format(s=30)}<span>Pavel IA <b>CV 4.0</b></span></div>',
                unsafe_allow_html=True)
