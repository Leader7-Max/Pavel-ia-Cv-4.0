"""Identité visuelle : logo, en-tête et effets CSS de Pavel IA CV 4.0."""
import urllib.parse

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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
@property --num{syntax:"<integer>";initial-value:0;inherits:false}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes flow{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(245,158,11,.55)}50%{box-shadow:0 0 0 12px rgba(245,158,11,0)}}
@keyframes bob{0%,100%{transform:translateY(0) rotate(-2deg)}50%{transform:translateY(-6px) rotate(2deg)}}
@keyframes float{0%,100%{transform:translate(0,0)}50%{transform:translate(18px,-14px)}}
@keyframes shine{to{left:135%}}
@keyframes beat{0%,100%{transform:scale(1)}15%{transform:scale(1.06)}30%{transform:scale(1)}45%{transform:scale(1.06)}}
.stApp{background:radial-gradient(1100px 520px at 50% -10%,#e0e7ff 0%,#f8fafc 55%,#fff 100%)}
.block-container{max-width:760px;padding-top:1.2rem;animation:fadeUp .5s ease both}
.hero{position:relative;overflow:hidden;background:linear-gradient(120deg,#0f172a,#1e3a8a,#7c3aed,#2563eb);
 background-size:300% 300%;animation:flow 12s ease infinite;color:#fff;padding:1.8rem 1.2rem;border-radius:24px;
 margin-bottom:1.2rem;text-align:center;box-shadow:0 18px 40px rgba(30,58,138,.3)}
.hero .orb{position:absolute;border-radius:50%;filter:blur(34px);opacity:.55;animation:float 9s ease-in-out infinite}
.hero .o1{width:140px;height:140px;background:#ec4899;top:-40px;left:-30px}
.hero .o2{width:160px;height:160px;background:#22d3ee;bottom:-60px;right:-40px;animation-delay:-4s}
.hero>*:not(.orb){position:relative;z-index:1}
.hero .logo svg{animation:bob 4s ease-in-out infinite;filter:drop-shadow(0 8px 14px rgba(0,0,0,.35))}
.hero h1{margin:.4rem 0 0;font-size:2.3rem;color:#fff;font-weight:800;letter-spacing:-.5px}
.hero h1 span{background:linear-gradient(90deg,#fde68a,#f9a8d4);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{margin:.4rem 0;opacity:.93;font-size:1.05rem}
.hero .badge{display:inline-block;margin-top:.5rem;padding:.35rem .95rem;border-radius:999px;
 background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.32);font-weight:600;font-size:.9rem;backdrop-filter:blur(6px)}
.minilogo{display:flex;align-items:center;gap:.55rem;font-weight:800;color:#1e3a8a;margin:.2rem 0 .4rem}
.minilogo b{background:linear-gradient(90deg,#1e3a8a,#7c3aed);-webkit-background-clip:text;background-clip:text;color:transparent}
.stButton>button,.stDownloadButton>button{position:relative;overflow:hidden;width:100%;min-height:3.3rem;border:none;
 border-radius:16px;background:linear-gradient(135deg,#1e3a8a,#3b82f6);color:#fff;font-weight:700;font-size:1rem;
 box-shadow:0 6px 16px rgba(37,99,235,.22);transition:transform .2s ease,box-shadow .2s ease,filter .2s ease}
.stButton>button::after,.stDownloadButton>button::after{content:"";position:absolute;top:0;left:-75%;width:45%;height:100%;
 background:linear-gradient(120deg,transparent,rgba(255,255,255,.4),transparent);transform:skewX(-20deg)}
.stButton>button:hover::after,.stDownloadButton>button:hover::after{animation:shine .8s ease}
.stButton>button p,.stDownloadButton>button p{color:#fff!important}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-3px);filter:brightness(1.08);
 box-shadow:0 12px 26px rgba(59,130,246,.4);color:#fff}
.stButton>button:active{transform:scale(.97)}
[class*="st-key-home_"] button{min-height:3.7rem;font-size:1.05rem}
[class*="st-key-back_"] button{background:#fff;border:1px solid #cbd5e1;box-shadow:none;min-height:2.6rem}
[class*="st-key-back_"] button p{color:#1e293b!important}
.st-key-like_btn button{background:linear-gradient(135deg,#fb7185,#e11d48)}
.st-key-like_btn button:disabled{opacity:1;animation:beat 1.6s infinite}
[data-testid="stLinkButton"] a{display:flex;align-items:center;justify-content:center;min-height:3rem;border-radius:14px;
 font-weight:700;text-decoration:none;background:linear-gradient(135deg,#e0e7ff,#c7d2fe);color:#1e1b4b!important;transition:transform .2s}
[data-testid="stLinkButton"] a:hover{transform:translateY(-2px)}
[class*="paypal"] a,.st-key-paypal_btn button{background:linear-gradient(135deg,#fde68a,#f59e0b)!important;color:#3b2300!important;
 animation:pulse 2.4s infinite;min-height:3.4rem;font-weight:800}
.st-key-paypal_btn button p{color:#3b2300!important}
.support{background:linear-gradient(135deg,#fffbeb,#fef3c7);border:1px solid #fcd34d;border-radius:18px;
 padding:1rem 1.1rem;margin:.5rem 0 .7rem;color:#78350f;text-align:center}
.social{background:linear-gradient(135deg,#eef2ff,#fae8ff);border:1px solid #c7d2fe;border-radius:18px;
 padding:1rem 1.1rem;margin:.5rem 0 .7rem;color:#3730a3;text-align:center}
[data-testid="stMetric"]{background:rgba(255,255,255,.8);backdrop-filter:blur(8px);border:1px solid #e2e8f0;
 border-radius:18px;padding:.8rem 1rem;box-shadow:0 4px 14px rgba(15,23,42,.06);transition:transform .2s}
[data-testid="stMetric"]:hover{transform:translateY(-3px)}
.stTextInput input,.stTextArea textarea,.stSelectbox [data-baseweb="select"]>div{border-radius:12px!important;
 border:1px solid #cbd5e1!important;background:#fff!important;transition:box-shadow .2s,border-color .2s}
.stTextInput input:focus,.stTextArea textarea:focus{border-color:#3b82f6!important;box-shadow:0 0 0 3px rgba(59,130,246,.22)!important}
.stProgress>div>div>div>div{background-image:linear-gradient(to right,#1e3a8a,#7c3aed,#ec4899);border-radius:10px}
[data-testid="stExpander"]{border-radius:16px;border:1px solid #e2e8f0;background:rgba(255,255,255,.78)}
@keyframes bar{0%{background-position:0% 50%}100%{background-position:200% 50%}}
@keyframes breathe{0%,100%{box-shadow:0 4px 14px rgba(99,102,241,.18)}50%{box-shadow:0 4px 24px rgba(99,102,241,.5)}}
[data-testid="stDecoration"]{height:4px!important;background:linear-gradient(90deg,#2563eb,#7c3aed,#ec4899,#f59e0b,#2563eb)!important;
 background-size:200% 100%!important;animation:bar 1.6s linear infinite}
[data-testid="stSpinner"]{display:flex;align-items:center;gap:.6rem;padding:.75rem 1rem;border-radius:14px;
 background:rgba(255,255,255,.92);border:1px solid #c7d2fe;animation:breathe 1.6s ease-in-out infinite}
[data-testid="stSpinner"] p,[data-testid="stSpinner"] div{background:linear-gradient(90deg,#1e3a8a,#7c3aed,#ec4899,#1e3a8a);
 background-size:200% 100%;-webkit-background-clip:text;background-clip:text;color:transparent!important;font-weight:700;
 animation:bar 2s linear infinite}
.stProgress>div>div>div>div{background-size:200% 100%!important;animation:bar 2.2s linear infinite;
 box-shadow:0 0 12px rgba(124,58,237,.55)}
.stButton>button,.stDownloadButton>button{background-size:200% 200%}
.stButton>button:hover{background-position:100% 50%}
.stButton>button:focus-visible{outline:3px solid rgba(124,58,237,.55);outline-offset:2px}
.stButton>button:disabled{filter:saturate(.7);opacity:.8}
.st-key-share_btn button{background:linear-gradient(135deg,#7c3aed,#db2777)}
.st-key-rv_submit button{background:linear-gradient(135deg,#10b981,#047857)}
.rating{text-align:center;font-size:1.8rem;font-weight:800;color:#b45309;margin:.3rem 0 .6rem}
.rating small{display:block;font-size:.85rem;font-weight:600;color:#64748b}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:16px;animation:fadeUp .4s ease both}
@keyframes count{from{--num:0}}
@keyframes rise{from{opacity:0;transform:translateY(18px) scale(.97)}to{opacity:1;transform:none}}
html{scroll-behavior:smooth}
.stMarkdown,.stButton button,label,h1,h2,h3,h4,input,textarea{font-family:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif}
[data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:.6rem!important}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"],[data-testid="stHorizontalBlock"]>[data-testid="column"]{
 min-width:0!important;flex:1 1 0!important;width:auto!important}
.stButton>button::before{content:"";position:absolute;inset:0;background:radial-gradient(circle,rgba(255,255,255,.5) 0%,transparent 60%);
 opacity:0;transform:scale(.2);transition:transform .5s,opacity .5s}
.stButton>button:active::before{opacity:1;transform:scale(2.4);transition:0s}
[class*="st-key-home_"] button{min-height:5.4rem;font-size:.98rem;line-height:1.25;padding:.6rem .5rem;border-radius:20px}
[class*="st-key-like_btn"] button,[class*="st-key-rv_btn"] button,[class*="st-key-share_btn"] button{
 font-size:.9rem;padding:.3rem .2rem;min-height:3rem}
.st-key-rv_btn button{background:linear-gradient(135deg,#0ea5e9,#4f46e5)}
.badges{display:flex;flex-wrap:wrap;gap:.45rem;justify-content:center;margin:.2rem 0 .8rem}
.badges span{padding:.3rem .75rem;border-radius:999px;background:#fff;border:1px solid #c7d2fe;color:#3730a3;
 font-size:.82rem;font-weight:600;box-shadow:0 2px 8px rgba(79,70,229,.08);animation:rise .6s ease both}
.badges span:nth-child(2){animation-delay:.1s}.badges span:nth-child(3){animation-delay:.2s}.badges span:nth-child(4){animation-delay:.3s}
.stats{display:flex;gap:.8rem;margin:.4rem 0 .8rem}
.stat{flex:1;text-align:center;padding:.9rem .4rem;border-radius:20px;background:rgba(255,255,255,.85);
 border:1px solid #e2e8f0;box-shadow:0 6px 18px rgba(15,23,42,.07);transition:transform .25s,box-shadow .25s;animation:rise .6s .15s ease both}
.stat:hover{transform:translateY(-4px);box-shadow:0 12px 26px rgba(79,70,229,.18)}
.stat b{display:block;font-size:2.1rem;font-weight:800;color:#1e3a8a;counter-reset:num var(--num);animation:count 1.4s ease-out both}
.stat b::after{content:counter(num)}
.stat span{font-size:.85rem;font-weight:600;color:#64748b}
.sec{margin:1.1rem 0 .6rem;font-size:1.15rem;font-weight:800;color:#0f172a;display:flex;align-items:center;gap:.5rem}
.sec::after{content:"";flex:1;height:2px;border-radius:2px;background:linear-gradient(90deg,#c7d2fe,transparent)}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:.6rem;margin:.6rem 0 1rem}
.step{text-align:center;padding:.8rem .5rem;border-radius:18px;background:rgba(255,255,255,.85);border:1px solid #e2e8f0;
 box-shadow:0 4px 14px rgba(15,23,42,.05);animation:rise .6s ease both;transition:transform .25s}
.step:hover{transform:translateY(-4px)}
.step:nth-child(2){animation-delay:.12s}.step:nth-child(3){animation-delay:.24s}
.step i{display:inline-flex;align-items:center;justify-content:center;width:1.9rem;height:1.9rem;border-radius:50%;font-style:normal;
 font-weight:800;color:#fff;background:linear-gradient(135deg,#2563eb,#7c3aed);margin-bottom:.35rem}
.step b{display:block;font-size:.9rem;color:#0f172a}.step span{font-size:.75rem;color:#64748b}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""


def inject_css():
    delays = "".join(
        f".st-key-home_{k} button{{background:linear-gradient(135deg,{_COLORS[k]})}}"
        f".st-key-home_{k}{{animation:fadeUp .55s {0.12 + i * 0.07:.2f}s ease both}}"
        for i, k in enumerate(_HOME))
    st.markdown("<style>" + CSS + delays + _css_v2() + "</style>", unsafe_allow_html=True)


def hero():
    st.markdown('<div class="hero"><div class="orb o1"></div><div class="orb o2"></div>'
                f'<div class="logo">{LOGO.format(s=76)}</div><h1>Pavel IA <span>CV 4.0</span></h1>'
                '<p>Votre carrière commence par un bon CV.</p>'
                '<span class="badge">Créez. Améliorez. Adaptez. Postulez.</span></div>',
                unsafe_allow_html=True)


def mini_logo():
    st.markdown(f'<div class="minilogo">{LOGO.format(s=30)}<span>Pavel IA <b>CV 4.0</b></span></div>',
                unsafe_allow_html=True)


def badges():
    st.markdown('<div class="badges"><span>✓ Gratuit</span><span>✓ Sans rien inventer</span>'
                '<span>✓ PDF &amp; Word</span><span>✓ Mobile</span></div>', unsafe_allow_html=True)


def stats(n_cv, n_letters):
    st.markdown('<div class="stats">'
                f'<div class="stat"><b style="--num:{int(n_cv)}"></b><span>CV créés</span></div>'
                f'<div class="stat"><b style="--num:{int(n_letters)}"></b><span>Lettres générées</span></div>'
                '</div>', unsafe_allow_html=True)


def section(title):
    st.markdown(f'<h3 class="sec">{title}</h3>', unsafe_allow_html=True)


def steps():
    st.markdown('<h3 class="sec">Comment ça marche</h3><div class="steps">'
                '<div class="step"><i>1</i><b>Décrivez</b><span>vos infos ou importez votre CV</span></div>'
                '<div class="step"><i>2</i><b>L\'IA rédige</b><span>sans rien inventer</span></div>'
                '<div class="step"><i>3</i><b>Téléchargez</b><span>PDF, Word ou TXT</span></div></div>',
                unsafe_allow_html=True)


# Logos (SVG) : réalisés pour l'app. Pour utiliser les fichiers officiels, remplacez les valeurs ci-dessous.
ICONS = {
    'heart_outline': "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M12 21 C12 21 3 15 3 8.8 C3 6 5.2 4 7.6 4 C9.4 4 11 5 12 6.6 C13 5 14.6 4 16.4 4 C18.8 4 21 6 21 8.8 C21 15 12 21 12 21 Z' fill='none' stroke='white' stroke-width='2' stroke-linejoin='round'/></svg>",
    'heart_filled': "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M12 21 C12 21 3 15 3 8.8 C3 6 5.2 4 7.6 4 C9.4 4 11 5 12 6.6 C13 5 14.6 4 16.4 4 C18.8 4 21 6 21 8.8 C21 15 12 21 12 21 Z' fill='white'/></svg>",
    'star': "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><polygon points='12.00,2.40 14.53,9.12 21.70,9.45 16.09,13.93 18.00,20.85 12.00,16.90 6.00,20.85 7.91,13.93 2.30,9.45 9.47,9.12' fill='white'/></svg>",
    'whatsapp': "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><circle cx='16' cy='16' r='16' fill='#25D366'/><circle cx='16' cy='15.4' r='9.4' fill='white'/><polygon points='6.8,25.6 8.9,19.2 13.2,23.6' fill='white'/><path d='M12.1 11.6 C11.6 12.2 11.5 13.4 12.3 15 C13.4 17.2 15.1 18.9 17.3 20 C18.9 20.8 20.1 20.7 20.6 20.1 L20.6 18.7 L18.4 17.4 L17.3 18.1 C16.1 17.5 14.9 16.3 14.3 15.1 L15 14 L13.7 11.8 Z' fill='#25D366'/></svg>",
    'telegram': "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><circle cx='16' cy='16' r='16' fill='#229ED9'/><polygon points='25.2,8.6 6.8,15.7 13.2,18.2 21.8,11.6 15.4,19.4 15.6,23.6 18.5,20.8 22.6,23.9' fill='white'/></svg>",
    'facebook': "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><circle cx='16' cy='16' r='16' fill='#1877F2'/><path d='M17.6 26 V17.4 H20.5 L21 14 H17.6 V12 C17.6 11 18 10.3 19.4 10.3 H21 V7.2 C20.7 7.2 19.6 7 18.4 7 C15.7 7 14 8.6 14 11.5 V14 H11 V17.4 H14 V26 Z' fill='white'/></svg>",
    'linkedin': "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='#0A66C2'/><rect x='6.5' y='12.5' width='4' height='13' fill='white'/><circle cx='8.5' cy='8.6' r='2.4' fill='white'/><path d='M13.5 12.5 H17.3 V14.3 C18 13.1 19.3 12.2 21.3 12.2 C24.9 12.2 25.7 14.5 25.7 17.6 V25.5 H21.7 V18.5 C21.7 16.8 21.6 15.5 19.8 15.5 C18 15.5 17.6 16.7 17.6 18.5 V25.5 H13.5 Z' fill='white'/></svg>",
    'x': "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='black'/><line x1='9' y1='8.5' x2='23' y2='23.5' stroke='white' stroke-width='2.6' stroke-linecap='round'/><line x1='23' y1='8.5' x2='9' y2='23.5' stroke='white' stroke-width='2.6' stroke-linecap='round'/></svg>",
    'sms': "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='8' fill='#34C759'/><ellipse cx='16' cy='14.6' rx='9.6' ry='7.4' fill='white'/><polygon points='8.6,24.4 11,18.4 15,20.6' fill='white'/></svg>",
    'paypal_mono': "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 26 28'><path d='M8.50 2.00 H18.00 C22.50 2.00 25.10 4.50 24.50 8.30 C23.80 13.00 20.50 15.20 16.30 15.20 H13.10 L11.70 24.00 H6.30 Z' fill='#009cde'/><path d='M3.60 4.00 H13.10 C17.60 4.00 20.20 6.50 19.60 10.30 C18.90 15.00 15.60 17.20 11.40 17.20 H8.20 L6.80 26.00 H1.40 Z' fill='#003087'/></svg>",
    'paypal_word': "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 112 30'><g transform='translate(1 1) scale(.95)'><path d='M8.50 2.00 H18.00 C22.50 2.00 25.10 4.50 24.50 8.30 C23.80 13.00 20.50 15.20 16.30 15.20 H13.10 L11.70 24.00 H6.30 Z' fill='#009cde'/><path d='M3.60 4.00 H13.10 C17.60 4.00 20.20 6.50 19.60 10.30 C18.90 15.00 15.60 17.20 11.40 17.20 H8.20 L6.80 26.00 H1.40 Z' fill='#003087'/></g><text x='30' y='22' font-family='Verdana,Arial,sans-serif' font-weight='bold' font-style='italic' font-size='20' fill='#003087'>Pay</text><text x='67' y='22' font-family='Verdana,Arial,sans-serif' font-weight='bold' font-style='italic' font-size='20' fill='#009cde'>Pal</text></svg>",
}

def _uri(name):
    return 'url("data:image/svg+xml,' + urllib.parse.quote(ICONS[name], safe="") + '")'


def _css_v2():
    """Corrections de mise en page (mobile) et logos. Les couleurs, dégradés et effets existants sont conservés."""
    links = [('a[href*="wa.me"]', "whatsapp"), ('a[href*="t.me"]', "telegram"),
             ('a[href*="facebook.com"]', "facebook"), ('a[href*="linkedin.com"]', "linkedin"),
             ('a[href*="twitter.com"]', "x"), ('a[href^="sms:"]', "sms"), ('a[href*="paypal"]', "paypal_mono")]
    link_css = "".join(
        '[data-testid="stLinkButton"] ' + sel + '::before{content:"";flex:none;width:1.3em;height:1.3em;'
        'margin-right:.55rem;background:' + _uri(name) + ' center/contain no-repeat}' for sel, name in links)
    css = """
.block-container{padding-top:calc(3.4rem + env(safe-area-inset-top,0px))!important}
header[data-testid="stHeader"]{background:transparent!important}
.hero{margin-top:0}
.stats{gap:.6rem;margin:.1rem 0 .7rem}
.stat{display:flex;align-items:center;justify-content:center;gap:.5rem;padding:.4rem .7rem;border-radius:14px;
 box-shadow:0 3px 10px rgba(15,23,42,.06)}
.stat:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(79,70,229,.15)}
.stat b{display:inline;font-size:1.2rem;line-height:1}
.stat span{font-size:.8rem;line-height:1}
[class*="st-key-like_btn"] button,[class*="st-key-rv_btn"] button,[class*="st-key-share_btn"] button{
 height:3rem!important;min-height:3rem!important;padding:0 .25rem!important;font-size:.9rem!important;
 display:flex;align-items:center;justify-content:center}
[class*="st-key-like_btn"] button p,[class*="st-key-rv_btn"] button p,[class*="st-key-share_btn"] button p{
 display:flex;align-items:center;justify-content:center;gap:.4rem;margin:0;white-space:nowrap}
[class*="st-key-like_btn"] button p::before,[class*="st-key-rv_btn"] button p::before,
[class*="st-key-share_btn"] button p::before{content:"";flex:none;width:1.2em;height:1.2em;
 background-repeat:no-repeat;background-position:center;background-size:contain}
.st-key-like_btn button p::before{background-image:@HEART@}
.st-key-lik
