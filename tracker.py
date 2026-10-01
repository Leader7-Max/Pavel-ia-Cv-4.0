"""Suivi des candidatures (Job Tracker), relié au coffre chiffré."""
import datetime
import uuid

import streamlit as st

import ai

STATUS = ["À postuler", "Postulé", "Relance à faire", "Entretien", "Offre reçue", "Refusé"]
ICON = {"À postuler": "📝", "Postulé": "📤", "Relance à faire": "⏰", "Entretien": "🎤",
        "Offre reçue": "🎉", "Refusé": "❌"}


def _rows(h):
    return h.ss.setdefault("tracker", [])


def _load(h):
    if h.ss.get("tracker_loaded") or not h.ss.get("vault_active"):
        return
    rows = h.vault.tracker_load()
    if isinstance(rows, list):
        h.ss["tracker"] = rows
        h.ss["tracker_loaded"] = True


def _persist(h):
    if h.ss.get("vault_active"):
        ok = h.vault.tracker_save(_rows(h))
        st.toast("Suivi sauvegardé dans votre coffre." if ok else "Sauvegarde impossible pour le moment.")


def _add(h):
    ss = h.ss
    company, poste = ss.get("tr_company", "").strip(), ss.get("tr_poste", "").strip()
    if not company or not poste:
        st.toast("Renseignez l'entreprise et le poste.")
        return
    day = ss.get("tr_date") or datetime.date.today()
    _rows(h).insert(0, {"id": uuid.uuid4().hex[:8], "company": company[:80], "poste": poste[:80],
                        "status": ss.get("tr_status", STATUS[1]), "date": str(day),
                        "link": ss.get("tr_link", "").strip()[:300], "notes": ss.get("tr_notes", "").strip()[:500]})
    for k in ("tr_company", "tr_poste", "tr_link", "tr_notes"):
        ss[k] = ""
    _persist(h)


def _set_status(h, rid):
    for r in _rows(h):
        if r["id"] == rid:
            r["status"] = h.ss.get("tr_st_" + rid, r["status"])
    _persist(h)


def _delete(h, rid):
    h.ss["tracker"] = [r for r in _rows(h) if r["id"] != rid]
    _persist(h)


def _kpis(rows):
    count = lambda *s: sum(r["status"] in s for r in rows)
    items = [("Candidatures", len(rows)), ("En cours", count("Postulé", "Relance à faire", "Entretien")),
             ("Entretiens", count("Entretien")), ("Offres", count("Offre reçue"))]
    for a in (items[:2], items[2:]):
        st.markdown('<div class="stats">' + "".join(
            f'<div class="stat"><b style="--num:{int(n)}"></b><span>{label}</span></div>' for label, n in a)
            + "</div>", unsafe_allow_html=True)


def _days(date_str):
    try:
        return (datetime.date.today() - datetime.date.fromisoformat(date_str)).days
    except ValueError:
        return 0


def page(h):
    """Page Streamlit (h = outils partagés fournis par app.py)."""
    h.top("Suivi des candidatures")
    _load(h)
    rows = _rows(h)
    if h.ss.get("vault_active"):
        st.success("🔐 Coffre actif : vos candidatures sont sauvegardées, chiffrées avec votre code.")
    else:
        st.info("Vos candidatures ne sont conservées que pendant cette session. Activez le coffre "
                "(Mes documents) pour les sauvegarder de façon chiffrée.")
    _kpis(rows)
    with st.expander("➕ Ajouter une candidature", expanded=not rows):
        st.text_input("Entreprise *", key="tr_company")
        st.text_input("Poste *", key="tr_poste")
        st.selectbox("Statut", STATUS, index=1, key="tr_status")
        st.date_input("Date de candidature", value=datetime.date.today(), key="tr_date")
        st.text_input("Lien de l'offre (facultatif)", key="tr_link")
        st.text_area("Notes (contact, salaire, étapes…)", key="tr_notes", height=90)
        st.button("💾 ENREGISTRER LA CANDIDATURE", on_click=_add, args=(h,), key="tr_add")
    flt = st.selectbox("Filtrer", ["Tous"] + STATUS, key="tr_filter")
    shown = [r for r in rows if flt == "Tous" or r["status"] == flt]
    if not shown:
        st.caption("Aucune candidature à afficher.")
    for r in shown:
        rid = r["id"]
        with st.container(border=True):
            st.markdown(f"**{ICON.get(r['status'], '•')} {r['poste']}** · {r['company']}")
            st.caption(f"Candidature du {r['date']} · il y a {_days(r['date'])} jour(s)")
            st.selectbox("Statut", STATUS, index=STATUS.index(r["status"]) if r["status"] in STATUS else 1,
                         key="tr_st_" + rid, on_change=_set_status, args=(h, rid))
            if r.get("link", "").startswith(("https://", "http://")):
                st.link_button("🔗 Voir l'offre", r["link"], use_container_width=True)
            if r.get("notes"):
                st.text(r["notes"])
            if st.button("✉️ Rédiger un mail de relance", key="tr_mail_" + rid):
                out = h.run_ai(ai.followup_mail, r["company"], r["poste"], _days(r["date"]), "Français")
                if out:
                    h.ss["tr_out_" + rid] = out
            if h.ss.get("tr_out_" + rid):
                st.code(h.ss["tr_out_" + rid], language=None)
            st.button("🗑️ Supprimer", on_click=_delete, args=(h, rid), key="tr_del_" + rid)
      
