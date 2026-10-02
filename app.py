"""PAVEL IA CV PRO : point d'entrée (configuration, routage et pied de page)."""
import types

import streamlit as st

try:
    import core
    import docs_ui
    import pages_analyze
    import pages_cv
    import pages_home
    import pages_write
except Exception as _err:  # fichier essentiel absent ou incorrect
    st.error(f"🛠️ Fichier essentiel manquant ou incorrect : {type(_err).__name__} : {_err}. "
             "Vérifiez que tous les fichiers du projet sont dans GitHub, à jour, puis faites Reboot.")
    st.stop()

st.set_page_config(page_title="Pavel IA CV Pro", page_icon="📄", layout="centered",
                   initial_sidebar_state="collapsed")
core.init_state()
ss = core.ss
if core.PROBLEMS:
    st.error("🛠️ Le design est désactivé : corrigez ces fichiers dans GitHub puis faites Reboot.\n\n"
             + "\n\n".join("- " + p for p in core.PROBLEMS))

core.ui.inject_css()
core.admin.banner()
core.accounts.enforce()
if hasattr(core.ai, "set_guard"):
    core.ai.set_guard(core.quota.guard)

H = types.SimpleNamespace(ss=ss, ai=core.ai, ui=core.ui, vault=core.vault, top=core.top, run_ai=core.run_ai,
                          import_cv=core.import_cv, cv_gate=docs_ui.cv_gate, show_ats=docs_ui.show_ats,
                          ats_button=docs_ui.ats_button, go=core.go)


def ext_page(mod, name):
    """Page fournie par un module externe, avec un message clair si le fichier manque."""
    def run():
        if getattr(mod, "_mod", None) is None or not hasattr(mod._mod, "page"):
            st.button("← Accueil", on_click=core.go, args=("home",), key="back_ext_" + name)
            st.error(f"Le fichier {name}.py est absent ou obsolète dans GitHub : ajoutez-le, puis redémarrez l'app.")
            return
        mod.page(H)
    return run


PAGES = {"home": pages_home.home, "cv": pages_cv.page_cv, "letter": pages_write.page_letter,
         "analyze": pages_analyze.page_analyze, "adapt": pages_analyze.page_adapt,
         "translate": pages_write.page_translate, "express": pages_write.page_express,
         "docs": pages_home.page_docs,
         "ats": ext_page(core.ats_live, "ats_live"), "interview": ext_page(core.interview_coach, "interview_coach"),
         "linkedin": ext_page(core.linkedin_gen, "linkedin_gen"), "tracker": ext_page(core.tracker, "tracker"),
         "admin": ext_page(core.admin, "admin"), "account": ext_page(core.accounts, "accounts")}
PAGES.get(ss.page, pages_home.home)()
st.divider()
core.social.footer(ss.page != "home")
st.button("Espace administrateur", key="admin_link", on_click=core.go, args=("admin",))
if core.MISSING:
    st.warning("⚠️ Fichiers à vérifier dans GitHub : " + " · ".join(core.MISSING))
                   
