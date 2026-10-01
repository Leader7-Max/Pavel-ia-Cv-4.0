"""Simulation d'entretien d'embauche par IA : questions personnalisées, évaluation et bilan."""
import streamlit as st

import ai

KINDS = ["RH et motivation", "Comportemental (méthode STAR)", "Technique et métier", "Mixte"]


def _reset():
    st.session_state.pop("iv", None)


def _next(iv):
    iv["i"] += 1


def _setup(h):
    ss = h.ss
    st.caption("Entraînez-vous avec un recruteur virtuel : questions adaptées à votre poste, évaluation de "
               "chaque réponse et bilan final. L'IA ne s'appuie que sur votre CV et vos réponses.")
    poste = st.text_input("Poste visé *", key="iv_poste")
    company = st.text_input("Entreprise (facultatif)", key="iv_company")
    kind = st.selectbox("Type d'entretien", KINDS, key="iv_kind")
    lang = st.selectbox("Langue", ["Français", "English", "Deutsch", "Español", "Italiano"], key="iv_lang")
    n = st.select_slider("Nombre de questions", options=[3, 5, 8], value=5, key="iv_n")
    offer = st.text_area("Offre d'emploi (facultatif, pour personnaliser)", height=120, key="iv_offer")
    cv = h.import_cv("iv")
    if not cv.strip() and ss.get("cv_out"):
        cv = ss["cv_out"]
        st.caption("Votre dernier CV généré sera utilisé.")
    if st.button("🎤 DÉMARRER L'ENTRETIEN", key="iv_start"):
        if not poste.strip():
            st.warning("Indiquez le poste visé.")
            return
        raw = h.run_ai(ai.interview_questions, poste, company, kind, lang, cv, offer, n)
        qs = ai.parse_questions(raw, n) if raw else []
        if not qs:
            if raw:
                st.error("Impossible de préparer les questions. Réessayez.")
            return
        ss["iv"] = {"q": qs, "i": 0, "ans": {}, "fb": {}, "poste": poste.strip(), "kind": kind,
                    "lang": lang, "cv": cv, "summary": ""}
        st.rerun()


def _summary(h, iv):
    n = len(iv["q"])
    rows = [(iv["q"][i], iv["ans"].get(i, ""), ai.parse_note(iv["fb"].get(i, "")) or 0) for i in range(n)]
    avg = sum(r[2] for r in rows) / n
    st.progress(1.0)
    h.ui.score(round(avg * 10), "Bilan de votre entretien blanc", "Moyenne de vos notes sur 10, ×10 (indicatif).")
    for i, (q, _a, note) in enumerate(rows):
        st.write(f"**Q{i + 1}** — {note}/10 · {q}")
    if st.button("📝 OBTENIR MON BILAN PERSONNALISÉ", key="iv_sum_btn"):
        out = h.run_ai(ai.interview_summary, rows, iv["poste"], iv["lang"])
        if out:
            iv["summary"] = out
    if iv.get("summary"):
        st.markdown(iv["summary"])
    st.button("🔁 NOUVEL ENTRETIEN", on_click=_reset, key="iv_again")


def _session(h, iv):
    n, i = len(iv["q"]), iv["i"]
    if i >= n:
        return _summary(h, iv)
    st.progress(i / n)
    st.caption(f"Question {i + 1} sur {n} · {iv['poste']} · {iv['kind']}")
    st.info(f"🎤 {iv['q'][i]}")
    ans = st.text_area("Votre réponse", height=170, key=f"iv_ans_{i}",
                       placeholder="Répondez comme en entretien : contexte, actions, résultats…")
    fb = iv["fb"].get(i)
    if st.button("✅ ÉVALUER MA RÉPONSE", key=f"iv_eval_{i}"):
        if len(ans.strip()) < 15:
            st.warning("Écrivez une vraie réponse (quelques phrases) avant l'évaluation.")
        else:
            raw = h.run_ai(ai.interview_feedback, iv["q"][i], ans, iv["poste"], iv["kind"], iv["lang"], iv["cv"])
            if raw:
                iv["fb"][i], iv["ans"][i], fb = raw, ans, raw
    if fb:
        note = ai.parse_note(fb)
        if note is not None:
            st.write(f"**Note : {note}/10**")
            st.progress(note / 10)
        st.markdown(fb)
        st.button("➡️ QUESTION SUIVANTE" if i + 1 < n else "🏁 VOIR MON BILAN", on_click=_next,
                  args=(iv,), key=f"iv_next_{i}")
    st.button("↩️ Recommencer", on_click=_reset, key="iv_reset")


def page(h):
    """Page Streamlit (h = outils partagés fournis par app.py)."""
    h.top("Simulation d'entretien IA")
    iv = h.ss.get("iv")
    if iv:
        _session(h, iv)
    else:
        _setup(h)
        
