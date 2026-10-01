"""Coffre personnel : interface de sauvegarde durable chiffrée."""
import datetime
import json

import streamlit as st

import storage

ss = st.session_state
MIN_CODE = 6


def _load():
    try:
        ss["vault_docs"] = storage.list_docs(ss["vault_active"])
    except storage.StorageError as e:
        st.toast(str(e))


def _activate():
    code = ss.get("vault_code", "").strip()
    if len(code) < MIN_CODE:
        st.toast(f"Code trop court ({MIN_CODE} caractères minimum).")
        return
    ss["vault_active"] = code
    _load()


def _off():
    ss.pop("vault_active", None)
    ss.pop("vault_docs", None)


def _delete(doc_id):
    try:
        storage.delete_doc(ss["vault_active"], doc_id)
        _load()
    except storage.StorageError as e:
        st.toast(str(e))


def save(kind, poste, tpl, date, text):
    """Sauvegarde dans le coffre si actif. Retourne True si sauvegardé."""
    if not ss.get("vault_active"):
        return False
    try:
        storage.save_doc(ss["vault_active"], kind, poste, tpl, date, text)
        return True
    except storage.StorageError as e:
        st.toast(str(e))
        return False


def panel(downloads):
    st.markdown("#### 🔐 Coffre personnel")
    st.caption("Sauvegarde chiffrée avec votre code : sans lui, vos documents sont illisibles, "
               "et introuvables si vous l'oubliez. Choisissez un code long et unique.")
    st.caption(f"Stockage : {storage.backend_label()}")
    if not ss.get("vault_active"):
        st.text_input("Votre code personnel (6 caractères minimum)", type="password", key="vault_code")
        st.button("🔓 Activer mon coffre", on_click=_activate, key="vault_on")
        return
    st.success("Coffre actif : vos prochains enregistrements y sont sauvegardés.")
    st.button("🔄 Actualiser", on_click=_load, key="vault_ref")
    st.button("🔒 Fermer le coffre", on_click=_off, key="vault_off")
    for d in ss.get("vault_docs", []):
        if str(d.get("kind", "")).startswith("__"):
            continue  # documents internes (suivi des candidatures)
        with st.expander(f"{d['kind']} — {d['poste'] or 'sans titre'} — {d['date']}"):
            downloads(d["text"], d["tpl"], f"{d['kind']}_{d['id']}".replace(" ", "_"), f"v{d['id']}")
            st.button("🗑️ Supprimer", on_click=_delete, args=(d["id"],), key=f"vdel{d['id']}")


# --------------------------------------------------------- Suivi des candidatures (Job Tracker)
TRACKER_KIND = "__tracker__"


def tracker_load():
    """Liste des candidatures du coffre, [] si aucune, None si le coffre est inactif, False si erreur."""
    code = ss.get("vault_active")
    if not code:
        return None
    try:
        for d in storage.list_docs(code):
            if d["kind"] == TRACKER_KIND:
                data = json.loads(d["text"])
                return data if isinstance(data, list) else []
        return []
    except (storage.StorageError, ValueError):
        return False


def tracker_save(rows):
    """Remplace le suivi stocké dans le coffre. Retourne True si sauvegardé."""
    code = ss.get("vault_active")
    if not code:
        return False
    try:
        for d in storage.list_docs(code):
            if d["kind"] == TRACKER_KIND:
                storage.delete_doc(code, d["id"])
        storage.save_doc(code, TRACKER_KIND, "", "", datetime.date.today().strftime("%d/%m/%Y"),
                         json.dumps(rows, ensure_ascii=False))
        return True
    except storage.StorageError as e:
        st.toast(str(e))
        return False
        
