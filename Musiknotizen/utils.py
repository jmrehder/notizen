"""utils.py – verbindet sich entweder mit Supabase (per st.secrets) oder lokalem Postgres.
Audio‑Memos werden als BYTEA gespeichert.
"""
from __future__ import annotations

import re
import psycopg2
from psycopg2 import sql
import streamlit as st

# ---------------------------------------------------------------------------
# 1) Konfiguration  – Cloud‑Secrets haben Vorrang
# ---------------------------------------------------------------------------
if "postgres" in st.secrets:          # Streamlit Cloud / .streamlit/secrets.toml
    DB_CONFIG = dict(st.secrets["postgres"])  # type: ignore[arg-type]
else:                                  # Fallback: lokale Dev‑Datenbank
    DB_CONFIG: dict[str, str] = {
        "host": "localhost",
        "database": "musiknotizen",
        "user": "postgres",
        "password": "Klavier-4",
        "port": 5433,
        "sslmode": "disable",      # lokal kein SSL
    }





# ---------------------------------------------------------------------------
# 3) YouTube‑Helper
# ---------------------------------------------------------------------------
_YT_RE = re.compile(r"(?:https?://)?(?:www\\.)?(?:m\\.)?(?:youtube\\.com|youtu\\.be|youtube-nocookie\\.com)/(?:watch\\?v=|embed/|v/|)?([\\w-]{11})")

def get_youtube_id(url: str | None) -> str | None:
    m = _YT_RE.search(url or ""); return m.group(1) if m else None

# ---------------------------------------------------------------------------
# 4) DB‑Verbindung
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)  # sslmode kommt aus config

# ---------------------------------------------------------------------------
# 5) interne Helper
# ---------------------------------------------------------------------------

def _exec(query: str, params: tuple | list):
    conn = get_db_connection(); cur = conn.cursor()
    try:
        cur.execute(query, params); conn.commit()
    except psycopg2.Error as e:
        conn.rollback(); st.error(f"Datenbank‑Fehler: {e}")
    finally:
        cur.close()

# ---------------------------------------------------------------------------
# 6) CRUD‑Funktionen
# ---------------------------------------------------------------------------

def add_note(titel: str, komponist: str | None, werk: str | None, interpret: str | None,
             notiz: str, youtube_link: str | None, tags: str | None, sprachnotiz_data: bytes | None = None):
    _exec(
        """INSERT INTO notizen (titel, komponist, werk, interpret, notiz, youtube_link, tags, sprachnotiz_data)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (titel, komponist, werk, interpret, notiz, youtube_link, tags,
         psycopg2.Binary(sprachnotiz_data) if sprachnotiz_data else None),
    )

def update_note(note_id: int, titel: str, komponist: str | None, werk: str | None, interpret: str | None,
                notiz: str, youtube_link: str | None, tags: str | None, sprachnotiz_data: bytes | None = None):
    _exec(
        """UPDATE notizen SET titel=%s, komponist=%s, werk=%s, interpret=%s, notiz=%s,
               youtube_link=%s, tags=%s, sprachnotiz_data=%s WHERE id=%s""",
        (titel, komponist, werk, interpret, notiz, youtube_link, tags,
         psycopg2.Binary(sprachnotiz_data) if sprachnotiz_data else None, note_id),
    )

def get_notes(search_query: str = "", selected_tag: str | None = None, sort_by: str = "datum_desc"):
    conn = get_db_connection(); cur = conn.cursor()
    base = sql.SQL("SELECT id,titel,komponist,werk,interpret,notiz,youtube_link,tags,datum,sprachnotiz_data FROM notizen")
    where, params = [], []
    if search_query:
        like = f"%{search_query}%"; where.append("("+" OR ".join([f"{col} ILIKE %s" for col in ["titel","komponist","werk","interpret","notiz","tags"]])+")"); params.extend([like]*6)
    if selected_tag:
        where.append("LOWER(tags) LIKE %s"); params.append(f"%{selected_tag.lower()}%")
    if where:
        base += sql.SQL(" WHERE " + " AND ".join(where))
    order_map = {"datum_desc":"datum DESC","datum_asc":"datum ASC","titel_asc":"titel ASC","titel_desc":"titel DESC","komponist_asc":"komponist ASC NULLS LAST","komponist_desc":"komponist DESC NULLS LAST","interpret_asc":"interpret ASC NULLS LAST","interpret_desc":"interpret DESC NULLS LAST"}
    base += sql.SQL(" ORDER BY " + order_map.get(sort_by, "datum DESC"))
    try:
        cur.execute(base, params)
        rows = cur.fetchall(); fixed=[]
        for r in rows:
            lst=list(r); lst[9]=bytes(lst[9]) if lst[9] is not None else None; fixed.append(tuple(lst))
        return fixed
    except psycopg2.Error as e:
        st.error(f"Fehler beim Abrufen der Notizen: {e}"); return []
    finally:
        cur.close()

def delete_note(note_id: int):
    _exec("DELETE FROM notizen WHERE id=%s", (note_id,))
