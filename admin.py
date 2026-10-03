"""Espace administrateur : tableau de bord, modération des avis, annonce, pages actives, diagnostic.

Accès protégé par un mot de passe défini dans Streamlit Secrets (ADMIN_PASSWORD ou ADMIN_PASSWORD_HASH).
L'administrateur ne voit jamais le contenu des CV : les documents des utilisateurs sont chiffrés avec leur code.
"""
import csv
import hashlib
import hmac
import importlib.metadata as metadata
import io
import os
import sys
import time

import streamlit as st

import ai
import storage

ss = st.session_state
SESSION_SECONDS = 1800
MAX_FAILS, WINDOW = 5, 600
_FAILS = []  # horodatages des échecs de connexion (mémoire du serveur, partagée entre sessions)
PAGE_LABELS = {"cv": "Créer mon CV", "letter": "Lettre de motivation", "express": "CV Express",
               "analyze": "Analyser mon CV", "adapt": "Adapter à une offre", "ats": "Score ATS en direct",
               "translate": "Traduire mon CV", "interview": "Simulation d'entretien",
               "linkedin": "Profil LinkedIn", "tracker": "Suivi des candidatures", "docs": "Mes documents"}
FILES = ["app.py", "ai.py", "config.py", "exporters.py", "ui.py", "social.py", "storage.py", "vault.py",
         "ats_live.py", "interview_coach.py", "linkedin_gen.py", "tracker.py", "admin.py", "admin_users.py",
         "accounts.py", "quota.py", "requirements.txt"]
# Parties d'app.py : nécessaires uniquement si app.py est la version « modulaire » (import core)
SPLIT = ["core.py", "docs_ui.py", "pages_cv.py", "pages_write.py", "pages_analyze.py", "pages_home.py"]
# Début attendu de chaque fichier (détecte un mauvais copier-coller)
MARKERS = {
    "app.py": '"""PAVEL IA CV PRO',
    "ai.py": '"""Appels Gemini (REST) ',
    "config.py": '"""Configuration de PAVE',
    "exporters.py": '"""Exports PDF (reportla',
    "ui.py": '"""Identité visuelle : l',
    "social.py": '"""J\'aime, avis en étoil',
    "storage.py": '"""Stockage SQLite : com',
    "vault.py": '"""Coffre personnel : in',
    "ats_live.py": '"""Analyse ATS en direct',
    "interview_coach.py": '"""Simulation d\'entretie',
    "linkedin_gen.py": '"""Générateur de profil ',
    "tracker.py": '"""Suivi des candidature',
    "admin.py": '"""Espace administrateur',
    "admin_users.py": '"""Onglet « Utilisateurs',
    "accounts.py": '"""Comptes facultatifs :',
    "quota.py": '"""Quotas d\'utilisation ',
    "core.py": '"""Noyau : chargement sû',
    "docs_ui.py": '"""Éléments d\'interface ',
    "pages_cv.py": '"""Assistant de création',
    "pages_write.py": '"""Pages de rédaction : ',
    "pages_analyze.py": '"""Pages d\'analyse : ana',
    "pages_home.py": '"""Accueil et page « Mes',
}
SECRETS = [("GEMINI_API_KEY", "Clé Gemini (IA)"), ("GEMINI_MODEL", "Modèle Gemini (facultatif)"),
           ("SUPABASE_URL", "Supabase : URL"), ("SUPABASE_KEY", "Supabase : clé secrète"),
           ("PAYPAL_URL", "Lien PayPal (sinon config.py)"), ("APP_URL", "Adresse de l'app (facultatif)"),
           ("DB_SALT", "Sel de chiffrement (facultatif)"), ("ADMIN_PASSWORD", "Mot de passe admin"),
           ("ADMIN_PASSWORD_HASH", "Empreinte du mot de passe admin")]


def _secret(name):
    try:
        return str(st.secrets.get(name, "") or "").strip()
    except Exception:
        return ""


# --------------------------------------------------------------------------- accès
def _configured():
    return bool(_secret("ADMIN_PASSWORD_HASH") or _secret("ADMIN_PASSWORD"))


def _check(password):
    hashed = _secret("ADMIN_PASSWORD_HASH").lower()
    if hashed:
        return hmac.compare_digest(hashlib.sha256(password.encode()).hexdigest().encode(), hashed.encode())
    plain = _secret("ADMIN_PASSWORD")
    return bool(plain) and hmac.compare_digest(password.encode(), plain.encode())


def _lock_minutes():
    now = time.time()
    _FAILS[:] = [t for t in _FAILS if now - t < WINDOW]
    return int((_FAILS[0] + WINDOW - now) // 60) + 1 if len(_FAILS) >= MAX_FAILS else 0


def is_admin():
    return ss.get("admin_until", 0) > time.time()


def _try_login():
    wait = _lock_minutes()
    if wait:
        st.toast(f"Trop de tentatives. Réessayez dans {wait} min.")
        return
    password, ss["adm_pw"] = ss.get("adm_pw", ""), ""
    if _check(password):
        ss["admin_until"] = time.time() + SESSION_SECONDS
        _FAILS.clear()
    else:
        _FAILS.append(time.time())
        time.sleep(0.8)  # ralentit les essais automatisés
        st.toast("Mot de passe incorrect.")


def _logout():
    ss.pop("admin_until", None)


# ------------------------------------------------------------ paramètres publics (annonce, pages)
@st.cache_data(ttl=30, show_spinner=False)
def _settings():
    try:
        return {"announcement": storage.get_setting("announcement"),
                "level": storage.get_setting("announcement_level", "info"),
                "disabled": storage.get_setting("disabled_pages")}
    except Exception:
        return {}


def banner():
    """Affiche l'annonce de l'administrateur (appelée en haut de chaque page par app.py)."""
    s = _settings()
    msg = (s.get("announcement") or "").strip()
    if msg:
        {"warning": st.warning, "success": st.success}.get(s.get("level"), st.info)("📣 " + msg)


def disabled_pages():
    return {p for p in (_settings().get("disabled") or "").split(",") if p in PAGE_LABELS}


def _publish():
    try:
        msg = ss.get("adm_msg", "").strip()[:400]
        storage.set_setting("announcement", msg)
        storage.set_setting("announcement_level", ss.get("adm_level", "info"))
        _settings.clear()
        st.toast("Annonce publiée." if msg else "Annonce retirée.")
    except storage.StorageError as e:
        st.toast(str(e))


def _remove_announcement():
    ss["adm_msg"] = ""
    _publish()


def _save_pages():
    try:
        storage.set_setting("disabled_pages", ",".join(p for p in ss.get("adm_off", []) if p in PAGE_LABELS))
        _settings.clear()
        st.toast("Pages mises à jour.")
    except storage.StorageError as e:
        st.toast(str(e))


def _delete_review(review_id):
    try:
        storage.delete_review(review_id)
        try:
            import social
            social._reviews.clear()
        except Exception:
            pass
        st.toast("Avis supprimé.")
    except storage.StorageError as e:
        st.toast(str(e))


# ----------------------------------------------------------------------------- onglets
def _kpis(items):
    for i in range(0, len(items), 2):
        row = items[i:i + 2]
        if row:
            st.markdown('<div class="stats">' + "".join(
                f'<div class="stat"><b style="--num:{int(n)}"></b><span>{label}</span></div>'
                for label, n in row) + "</div>", unsafe_allow_html=True)


def _dashboard():
    try:
        c = storage.admin_counts()
    except Exception as e:
        st.error(f"Statistiques indisponibles ({type(e).__name__}). Vérifiez storage.py et la base de données.")
        return
    extra = getattr(storage, "admin_extra", lambda: {})()
    _kpis([("J'aime", c["likes"]), ("Avis", c["reviews"]), ("Coffres actifs", c["vaults"]),
           ("Documents sauvegardés", c["docs"]), ("Comptes", extra.get("users", 0)),
           ("Appels IA aujourd'hui", extra.get("ai_today", 0))])
    st.metric("Note moyenne", f"{c['avg']:.1f} / 5" if c["reviews"] else "—")
    st.caption(f"Suivis de candidatures sauvegardés : {c['trackers']} · Stockage : {storage.backend_label()}")
    st.info("🔒 Les CV et candidatures des utilisateurs sont chiffrés avec leur code personnel : "
            "vous voyez uniquement des compteurs, jamais leur contenu.")


def _safe_cell(value):
    s = str(value)
    return "'" + s if s[:1] in ("=", "+", "-", "@") else s  # évite l'injection de formule dans Excel


def _reviews_tab():
    try:
        rows = storage.admin_reviews(100)
    except Exception as e:
        st.error(f"Avis indisponibles ({type(e).__name__}).")
        return
    if not rows:
        st.caption("Aucun avis pour l'instant.")
        return
    st.caption(f"{len(rows)} avis les plus récents. Supprimez les contenus abusifs ou publicitaires.")
    for r in rows:
        with st.container(border=True):
            st.markdown("⭐" * max(1, min(5, int(r["stars"]))) + f" · {r['date']} · n°{r['id']}")
            st.text(f"{r['name'] or 'Anonyme'} : {r['comment'] or '(sans commentaire)'}")
            st.button("🗑️ Supprimer cet avis", on_click=_delete_review, args=(r["id"],), key=f"adm_del_{r['id']}")
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "date", "note", "nom", "commentaire"])
    for r in rows:
        w.writerow([r["id"], r["date"], r["stars"], _safe_cell(r["name"]), _safe_cell(r["comment"])])
    st.download_button("⬇️ Exporter les avis (CSV)", buf.getvalue(), "avis.csv", "text/csv", key="adm_csv")


def _content_tab():
    s = _settings()
    st.markdown("#### 📣 Annonce visible par tous")
    kw = {} if "adm_msg" in ss else {"value": s.get("announcement", "")}
    st.text_area("Message (400 caractères max)", max_chars=400, key="adm_msg", height=90, **kw)
    levels = ["info", "warning", "success"]
    cur = s.get("level", "info")
    lkw = {} if "adm_level" in ss else {"index": levels.index(cur) if cur in levels else 0}
    st.selectbox("Style", levels, key="adm_level", **lkw)
    st.button("📣 PUBLIER L'ANNONCE", on_click=_publish, key="adm_pub")
    st.button("🧹 Retirer l'annonce", on_click=_remove_announcement, key="adm_unpub")
    st.markdown("#### 🚧 Pages désactivées (maintenance ou quota IA)")
    okw = {} if "adm_off" in ss else {"default": sorted(disabled_pages())}
    st.multiselect("Pages indisponibles pour les utilisateurs", list(PAGE_LABELS), key="adm_off",
                   format_func=lambda p: PAGE_LABELS[p], **okw)
    st.button("💾 ENREGISTRER", on_click=_save_pages, key="adm_pages_save")


def _version(pkg):
    try:
        return metadata.version(pkg)
    except Exception:
        return "absent"


def _diagnostic_tab():
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(here, "app.py"), encoding="utf-8") as fh:
            modular = "import core" in fh.read()
    except OSError:
        modular = False
    needed = FILES + (SPLIT if modular else [])
    missing = [f for f in needed if not os.path.exists(os.path.join(here, f))]
    wrong = []
    for name, start in MARKERS.items():
        if name in SPLIT and not modular:
            continue
        path = os.path.join(here, name)
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as fh:
                    if not fh.readline().strip().startswith(start):
                        wrong.append(name)
            except OSError:
                wrong.append(name)
    st.markdown("#### 📁 Fichiers du dépôt")
    if not missing and not wrong:
        st.success("Tous les fichiers sont présents et semblent corrects.")
    if missing:
        st.error("Manquants : " + ", ".join(missing))
    if wrong:
        st.error("Contenu inattendu (mauvais fichier collé ?) : " + ", ".join(wrong))
    st.markdown("#### 🔑 Secrets configurés (valeurs jamais affichées)")
    st.markdown("\n".join(f"- {'✅' if _secret(k) else '⬜'} **{k}** : {label}" for k, label in SECRETS))
    st.markdown("#### 🧩 Environnement")
    st.markdown(f"- Python {sys.version.split()[0]} · Streamlit {getattr(st, '__version__', '?')}\n"
                f"- reportlab {_version('reportlab')} · python-docx {_version('python-docx')} · "
                f"cryptography {_version('cryptography')} · pypdf {_version('pypdf')}\n"
                f"- Stockage : {storage.backend_label()}")
    if st.button("🤖 Tester la connexion IA", key="adm_ai"):
        try:
            with st.spinner("Test en cours…"):
                out = ai.ask("Réponds uniquement par le mot OK.")
            models = getattr(ai, "_models", lambda: ["?"])()
            st.success(f"IA opérationnelle (modèle : {models[0]}) : {out[:60]}")
        except ai.AIError as e:
            st.error(str(e))
    if st.button("🗄️ Tester le stockage", key="adm_db"):
        try:
            c = storage.admin_counts()
            st.success(f"Stockage opérationnel ({storage.backend_label()}) : {c['likes']} J'aime, {c['reviews']} avis.")
        except Exception as e:
            st.error(f"Stockage en erreur : {type(e).__name__}.")
    if st.button("♻️ Vider les caches", key="adm_cache"):
        st.cache_data.clear()
        st.toast("Caches vidés.")


def _users_tab():
    try:
        import admin_users
    except ImportError:
        st.error("Le fichier admin_users.py est absent : ajoutez-le dans GitHub.")
        return
    admin_users.tab()


# -------------------------------------------------------------------------------- page
def page(h):
    """Page Streamlit (h = outils partagés fournis par app.py)."""
    h.top("Espace administrateur")
    if not _configured():
        st.error("Aucun mot de passe administrateur n'est configuré. Ajoutez-le dans Streamlit Secrets "
                 "(Settings > Secrets), puis redémarrez l'application :")
        st.code('ADMIN_PASSWORD = "choisissez-un-mot-de-passe-long-et-unique"', language="toml")
        st.caption("Option plus sûre : ADMIN_PASSWORD_HASH = empreinte SHA-256 du mot de passe.")
        return
    if not is_admin():
        wait = _lock_minutes()
        if wait:
            st.error(f"Trop de tentatives échouées. Réessayez dans {wait} minute(s).")
            return
        st.text_input("Mot de passe administrateur", type="password", key="adm_pw")
        st.button("🔓 SE CONNECTER", on_click=_try_login, key="adm_login")
        return
    st.caption(f"Session administrateur active (environ {int((ss['admin_until'] - time.time()) // 60)} min).")
    st.button("🚪 Se déconnecter", on_click=_logout, key="adm_logout")
    t1, t2, t3, t4, t5 = st.tabs(["📊 Tableau de bord", "💬 Avis", "📣 Contenu", "🛠️ Diagnostic", "👥 Utilisateurs"])
    with t1:
        _dashboard()
    with t2:
        _reviews_tab()
    with t3:
        _content_tab()
    with t4:
        _diagnostic_tab()
    with t5:
        _users_tab()
def page(h):
    """Page Streamlit (h = outils partagés fournis par app.py)."""
    h.top("Espace administrateur")
    if not _configured():
        st.error("Aucun mot de passe administrateur n'est configuré. Ajoutez-le dans Streamlit Secrets "
                 "(Settings > Secrets), puis redémarrez l'application :")
        st.code('ADMIN_PASSWORD = "choisissez-un-mot-de-passe-long-et-unique"', language="toml")
        st.caption("Option plus sûre : ADMIN_PASSWORD_HASH = empreinte SHA-256 du mot de passe.")
        return
    if not is_admin():
        wait = _lock_minutes()
        if wait:
            st.error(f"Trop de tentatives échouées. Réessayez dans {wait} minute(s).")
            return
        st.text_input("Mot de passe administrateur", type="password", key="adm_pw")
        st.button("🔓 SE CONNECTER", on_click=_try_login, key="adm_login")
        return
    st.caption(f"Session administrateur active (environ {int((ss['admin_until'] - time.time()) // 60)} min).")
    st.button("🚪 Se déconnecter", on_click=_logout, key="adm_logout")
    t1, t2, t3, t4, t5 = st.tabs(["📊 Tableau de bord", "💬 Avis", "📣 Contenu", "🛠️ Diagnostic", "👥 Utilisateurs"])
    with t1:
        _dashboard()
    with t2:
        _reviews_tab()
    with t3:
        _content_tab()
    with t4:
        _diagnostic_tab()
    with t5:
        _users_tab()
      
