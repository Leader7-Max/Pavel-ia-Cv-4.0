"""J'aime, avis en étoiles, partage et soutien PayPal."""
import re
import urllib.parse
import uuid

import streamlit as st

import storage
import config as _cfg

APP_URL = getattr(_cfg, "APP_URL", "")
BUILD = getattr(_cfg, "BUILD", "?")
PAYPAL_URL = getattr(_cfg, "PAYPAL_URL", "")

ss = st.session_state


def _secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def app_url():
    """Adresse publique : secret APP_URL > config.py > détection automatique."""
    u = str(_secret("APP_URL", "") or APP_URL).strip()
    if u.startswith("https://"):
        return u
    try:
        h = st.context.headers
        origin, host = h.get("Origin") or "", h.get("Host") or ""
        if origin.startswith("https://"):
            return origin
        if host and not host.startswith(("localhost", "127.", "0.0.0.0")):
            return "https://" + host
    except Exception:
        pass
    return ""


@st.cache_data(ttl=10, show_spinner=False)
def _likes():
    return storage.like_count()


@st.cache_data(ttl=20, show_spinner=False)
def _reviews():
    avg, n = storage.review_stats()
    return avg, n, storage.list_reviews(8)


def _clean_name(name):
    return re.sub(r"[^\w '\-.]", "", str(name)).replace("_", "").strip()[:40]


def _toggle(key):
    ss[key] = not ss.get(key, False)


def _like():
    try:
        storage.add_like(ss["visitor"])
        ss["liked"] = True
        _likes.clear()
        st.toast("Merci pour votre soutien !", icon="❤️")
    except storage.StorageError as e:
        st.toast(str(e))


# ---------------------------------------------------------------- Partage
def share_panel():
    url = app_url()
    if not url:
        st.info("Adresse de l'application non détectée : ajoutez APP_URL dans Streamlit Secrets.")
        return
    msg = "Je crée mon CV et ma lettre de motivation avec Pavel IA CV 4.0, c'est gratuit : "
    q, u = urllib.parse.quote(msg + url), urllib.parse.quote(url)
    with st.container(border=True):
        st.markdown("**📤 Inviter mes amis**")
        st.caption("Copiez le lien (icône à droite) :")
        st.code(url, language=None)
        c1, c2 = st.columns(2)
        c1.link_button("💬 WhatsApp", f"https://wa.me/?text={q}", use_container_width=True)
        c2.link_button("✈️ Telegram", f"https://t.me/share/url?url={u}&text={urllib.parse.quote(msg)}",
                       use_container_width=True)
        c1.link_button("📘 Facebook", f"https://www.facebook.com/sharer/sharer.php?u={u}",
                       use_container_width=True)
        c2.link_button("💼 LinkedIn", f"https://www.linkedin.com/sharing/share-offsite/?url={u}",
                       use_container_width=True)
        c1.link_button("🐦 X", f"https://twitter.com/intent/tweet?text={q}", use_container_width=True)
        c2.link_button("✉️ SMS", f"sms:?&body={q}", use_container_width=True)


# ------------------------------------------------------------------- Avis
def _submit_review():
    stars = ss.get("rv_stars")
    if stars is None:
        st.toast("Choisissez d'abord une note en étoiles.")
        return
    comment = str(ss.get("rv_comment", "")).strip()[:500]
    if re.search(r"https?://|www\.", comment, re.I):
        st.toast("Les liens ne sont pas autorisés dans les commentaires.")
        return
    try:
        storage.add_review(_clean_name(ss.get("rv_name", "")) or "Anonyme", int(stars) + 1, comment)
    except storage.StorageError as e:
        st.toast(str(e))
        return
    ss["reviewed"] = True
    ss["rv_open"] = False
    _reviews.clear()
    st.toast("Merci pour votre avis !", icon="🌟")


def review_form():
    if ss.get("reviewed"):
        st.success("Merci pour votre avis !")
        return
    with st.container(border=True):
        st.markdown("**✍️ Votre avis**")
        st.feedback("stars", key="rv_stars")
        st.text_input("Votre prénom (facultatif)", max_chars=40, key="rv_name")
        st.text_area("Votre commentaire (facultatif)", max_chars=500, key="rv_comment",
                     placeholder="Ce que vous avez aimé, ce qu'on peut améliorer...")
        st.button("⭐ ENVOYER MON AVIS", on_click=_submit_review, key="rv_submit")


def reviews_section():
    st.markdown('<h3 class="sec">⭐ Avis des utilisateurs</h3>', unsafe_allow_html=True)
    try:
        avg, n, items = _reviews()
    except storage.StorageError:
        st.info("Les avis sont momentanément indisponibles.")
        return
    if n:
        st.markdown(f'<div class="rating">⭐ {avg:.1f} / 5<small>{n} avis</small></div>',
                    unsafe_allow_html=True)
    else:
        st.caption("Soyez le premier à laisser un avis (bouton 💬 Avis).")
    for r in items:
        with st.container(border=True):
            stars = max(1, min(5, int(r["stars"])))
            who = _clean_name(r["name"]) or "Anonyme"
            st.markdown("⭐" * stars + "☆" * (5 - stars) + f" **{who}** · {r['date']}")
            if r["comment"]:
                st.text(r["comment"])


# ------------------------------------------------------- Barre J'aime/Avis/Partage
def social_bar():
    ss.setdefault("visitor", uuid.uuid4().hex)
    liked = ss.get("liked", False)
    st.markdown('<div class="social"><b>❤️ Vous aimez Pavel IA ?</b><br>Likez, donnez votre avis et '
                'partagez-le à vos amis.</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.button(f"{'❤️' if liked else '🤍'} {_likes()}", on_click=_like, key="like_btn", disabled=liked)
    c2.button("💬 Avis", on_click=_toggle, args=("rv_open",), key="rv_btn")
    c3.button("📤 Partager", on_click=_toggle, args=("share_open",), key="share_btn")
    if ss.get("rv_open"):
        review_form()
    if ss.get("share_open"):
        share_panel()


# ---------------------------------------------------------------- PayPal
def support_card():
    url = str(_secret("PAYPAL_URL", "") or PAYPAL_URL).strip()
    st.markdown('<div class="support"><b>💛 Pavel IA est gratuit</b><br>Il vous a été utile ? '
                'Un petit soutien aide à le faire grandir.</div>', unsafe_allow_html=True)
    if url.startswith("https://"):
        st.link_button("💛 SOUTENIR PAVEL IA VIA PAYPAL", url, use_container_width=True)
    else:
        st.button("💛 SOUTENIR VIA PAYPAL", key="paypal_btn",
                  on_click=lambda: st.toast("Le lien PayPal arrive bientôt. Merci ! 🙏"))


def footer(show_social=True):
    if show_social:
        social_bar()
    reviews_section()
    support_card()
    st.caption(f"Pavel IA CV 4.0 · version {BUILD} · stockage : {storage.backend_label()}")
    
