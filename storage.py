"""Stockage SQLite : compteur de likes (global) et documents chiffrés (par code personnel)."""
import base64
import datetime
import hashlib
import os
import sqlite3
import threading

import requests
import streamlit as st

MAX_DOCS = 50
MAX_CHARS = 60000
_LOCK = threading.Lock()


class StorageError(Exception):
    """Erreur de stockage avec message destiné à l'utilisateur."""


def _secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def _db_path():
    return (os.environ.get("PAVEL_DB_PATH") or str(_secret("DB_PATH", "") or "")
            or os.path.join(os.path.dirname(os.path.abspath(__file__)), "pavel_data.db"))


@st.cache_resource(show_spinner=False)
def _conn():
    try:
        c = sqlite3.connect(_db_path(), check_same_thread=False)
        c.execute("CREATE TABLE IF NOT EXISTS likes(visitor TEXT PRIMARY KEY, ts TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS docs(id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT, "
                  "kind TEXT, poste TEXT, tpl TEXT, date TEXT, data TEXT)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_docs_owner ON docs(owner)")
        c.commit()
        return c
    except (sqlite3.Error, OSError):
        raise StorageError("Base de données indisponible pour le moment.")


def _run(sql, args=(), fetch=False, commit=False):
    try:
        with _LOCK:
            c = _conn()
            cur = c.execute(sql, args)
            rows = cur.fetchall() if fetch else None
            if commit:
                c.commit()
            return rows
    except sqlite3.Error:
        raise StorageError("Erreur de base de données. Réessayez.")


# ------------------------------------------------- Supabase (base externe)
def _remote():
    return bool(_secret("SUPABASE_URL", "") and _secret("SUPABASE_KEY", ""))


def backend_label():
    return "Supabase (durable)" if _remote() else "fichier local du serveur (peut être effacé)"


def _rest(method, path, params=None, body=None, prefer=None):
    url = str(_secret("SUPABASE_URL")).strip().rstrip("/") + "/rest/v1/" + path
    key = str(_secret("SUPABASE_KEY")).strip()
    headers = {"apikey": key, "Content-Type": "application/json"}
    
    # Prise en charge des clés sb_secret_ et des anciens JWT (eyJ)
    if key.startswith("eyJ") or key.startswith("sb_secret_"):
        headers["Authorization"] = "Bearer " + key
        
    if prefer:
        headers["Prefer"] = prefer
    try:
        r = requests.request(method, url, params=params, json=body, headers=headers, timeout=10)
    except requests.RequestException:
        raise StorageError("Base de données distante injoignable. Réessayez.")
    if r.status_code >= 400:
        raise StorageError(f"Erreur de la base de données ({r.status_code}). "
                           "Vérifiez la configuration Supabase.")
    return r


def _r_count():
    r = _rest("GET", "likes", {"select": "visitor", "limit": "1"}, prefer="count=exact")
    try:
        return int(r.headers.get("Content-Range", "*/0").split("/")[-1])
    except ValueError:
        return 0


def _r_add_like(visitor):
    _rest("POST", "likes", {"on_conflict": "visitor"}, {"visitor": visitor},
          "resolution=ignore-duplicates,return=minimal")


def _r_save(owner, kind, poste, tpl, date, data):
    _rest("POST", "docs", None, {"owner": owner, "kind": kind, "poste": poste, "tpl": tpl,
                                 "date": date, "data": data}, "return=minimal")
    old = _rest("GET", "docs", {"select": "id", "owner": "eq." + owner, "order": "id.desc",
                                "offset": str(MAX_DOCS)}).json()
    if old:
        ids = ",".join(str(int(o["id"])) for o in old)
        _rest("DELETE", "docs", {"id": "in.(" + ids + ")", "owner": "eq." + owner})


def _r_list(owner):
    rows = _rest("GET", "docs", {"select": "id,kind,poste,tpl,date,data",
                                 "owner": "eq." + owner, "order": "id.desc"}).json()
    return [(x["id"], x["kind"], x["poste"], x["tpl"], x["date"], x["data"]) for x in rows]


def _r_delete(owner, doc_id):
    _rest("DELETE", "docs", {"id": "eq." + str(int(doc_id)), "owner": "eq." + owner})


# ------------------------------------------------------------------ likes
def like_count():
    if _remote():
        try:
            return _r_count()
        except StorageError:
            return 0
    try:
        return _run("SELECT COUNT(*) FROM likes", fetch=True)[0][0]
    except StorageError:
        return 0


def add_like(visitor):
    if _remote():
        return _r_add_like(visitor)
    _run("INSERT OR IGNORE INTO likes VALUES(?,?)", (visitor, datetime.datetime.utcnow().isoformat()),
         commit=True)


# -------------------------------------------------------------- documents
def _salt():
    return str(_secret("DB_SALT", "pavel-ia-cv-4.0")).encode()


def _owner(code):
    return hashlib.pbkdf2_hmac("sha256", code.encode(), _salt() + b"owner", 100_000).hex()


def _fernet(code):
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        raise StorageError("Chiffrement indisponible : ajoutez 'cryptography' à requirements.txt.")
    key = hashlib.pbkdf2_hmac("sha256", code.encode(), _salt() + b"key", 200_000, 32)
    return Fernet(base64.urlsafe_b64encode(key))


def save_doc(code, kind, poste, tpl, date, text):
    if len(text) > MAX_CHARS:
        raise StorageError("Document trop long pour être sauvegardé.")
    owner = _owner(code)
    data = _fernet(code).encrypt(text.encode("utf-8")).decode()
    if _remote():
        return _r_save(owner, kind, poste, tpl, date, data)
    _run("INSERT INTO docs(owner,kind,poste,tpl,date,data) VALUES(?,?,?,?,?,?)",
         (owner, kind, poste, tpl, date, data), commit=True)
    _run("DELETE FROM docs WHERE owner=? AND id NOT IN "
         "(SELECT id FROM docs WHERE owner=? ORDER BY id DESC LIMIT ?)",
         (owner, owner, MAX_DOCS), commit=True)


def list_docs(code):
    owner = _owner(code)
    if _remote():
        rows = _r_list(owner)
    else:
        rows = _run("SELECT id,kind,poste,tpl,date,data FROM docs WHERE owner=? ORDER BY id DESC",
                    (owner,), fetch=True)
    f = _fernet(code)
    out = []
    for i, kind, poste, tpl, date, data in rows:
        try:
            out.append({"id": i, "kind": kind, "poste": poste, "tpl": tpl, "date": date,
                        "text": f.decrypt(data.encode()).decode("utf-8")})
        except Exception:
            continue
    return out


def delete_doc(code, doc_id):
    if _remote():
        return _r_delete(_owner(code), doc_id)
    _run("DELETE FROM docs WHERE id=? AND owner=?", (doc_id, _owner(code)), commit=True)
