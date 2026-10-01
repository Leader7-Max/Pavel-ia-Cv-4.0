"""Générateur de profil LinkedIn optimisé (titres, À propos, expériences, compétences)."""
import streamlit as st

import ai


def page(h):
    """Page Streamlit (h = outils partagés fournis par app.py)."""
    h.top("Profil LinkedIn")
    st.caption("Transformez votre CV en profil LinkedIn prêt à coller. Rien n'est inventé : les informations "
               "manquantes sont marquées [à compléter].")
    cv = h.import_cv("li")
    if not cv.strip() and h.ss.get("cv_out"):
        cv = h.ss["cv_out"]
        st.caption("Votre dernier CV généré sera utilisé.")
    goal = st.text_input("Objectif professionnel (facultatif)", key="li_goal",
                         placeholder="Ex. : trouver un poste de responsable logistique à Lyon")
    tone = st.selectbox("Ton", ["Professionnel", "Dynamique", "Chaleureux", "Sobre"], key="li_tone")
    lang = st.selectbox("Langue", list(ai.LANGS), key="li_lang")
    if st.button("💼 GÉNÉRER MON PROFIL LINKEDIN", key="li_btn"):
        if len(cv.strip()) < 50:
            st.warning("Importez ou collez d'abord votre CV.")
        elif not h.cv_gate(cv, "li"):
            st.warning("Confirmez d'abord que vous voulez utiliser ce document.")
        else:
            out = h.run_ai(ai.linkedin_profile, cv, goal, lang, tone)
            if out:
                h.ss["li_out"] = out
                h.ss["li_ready"] = True
    elif len(cv.strip()) >= 50:
        h.cv_gate(cv, "li")
    sections = ai.split_sections(h.ss.get("li_out", ""))
    if h.ss.get("li_out") and not sections:
        st.code(h.ss["li_out"], language=None)
    for title, body in sections:
        with st.expander(f"📌 {title}", expanded=title.lower().startswith(("à propos", "a propos", "titre"))):
            st.code(body, language=None)  # le bouton de copie est intégré
