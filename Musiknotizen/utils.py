from __future__ import annotations
import re
import psycopg2
from psycopg2 import sql
import streamlit as st

# -----------------------------------------------------------------------------
# 1) Konfiguration  – Cloud‑Secrets haben Vorrang
# -----------------------------------------------------------------------------
if "postgres" in st.secrets:
    DB_CONFIG = dict(st.secrets["postgres"])
else:
    DB_CONFIG: dict[str, str] = {
        "host": "localhost",
        "database": "musiknotizen",
        "user": "postgres",
        "password": "Klavier-4",
        "port": 5433,
        "sslmode": "disable",
    }

# -----------------------------------------------------------------------------
# 2) YouTube‑Helper (optional, wenn gebraucht)
# -----------------------------------------------------------------------------
_YT_RE = re.compile(r"(?:https?://)?(?:www\.)?(?:m\.)?(?:youtube\.com|youtu\.be|youtube-nocookie\.com)/(?:watch\?v=|embed/|v/|)?([\w-]{11})")

def get_youtube_id(url: str | None) -> str | None:
    m = _YT_RE.search(url or "")
    return m.group(1) if m else None

# -----------------------------------------------------------------------------
# 3) DB‑Verbindung
# -----------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# -----------------------------------------------------------------------------
# 4) interne Helper
# -----------------------------------------------------------------------------
def _exec(query: str, params: tuple | list):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        st.error(f"Datenbank‑Fehler: {e}")
    finally:
        cur.close()

# -----------------------------------------------------------------------------
# 5) CRUD‑Funktionen
# -----------------------------------------------------------------------------
def add_note(titel, kategorie, notiz, autor, tags, radiosendung, moderator, datum, bild_url, audio_url):
    _exec(
        """INSERT INTO notizen (titel, kategorie, notiz, autor, tags, radiosendung, moderator, datum, bild_url, audio_url)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (titel, kategorie, notiz, autor, tags, radiosendung, moderator, datum, bild_url, audio_url),
    )

def update_note(
    note_id: int,
    titel: str,
    kategorie: str,
    notiz: str,
    autor: str,
    tags: str | None,
    radiosendung: str | None,
    moderator: str | None,
    datum: str | None,
    bild_url: str | None,
    audio_url: str | None,
):
    _exec(
        """UPDATE notizen SET
               titel=%s,
               kategorie=%s,
               notiz=%s,
               autor=%s,
               tags=%s,
               radiosendung=%s,
               moderator=%s,
               datum=%s,
               bild_url=%s,
               audio_url=%s
           WHERE id=%s""",
        (titel, kategorie, notiz, autor, tags, radiosendung, moderator, datum, bild_url, audio_url, note_id),
    )

def get_notes(search_query: str = "", selected_tag: str | None = None, sort_by: str = "datum_desc"):
    conn = get_db_connection()
    cur = conn.cursor()
    base = sql.SQL(
        "SELECT id, titel, kategorie, notiz, autor, tags, radiosendung, moderator, datum, bild_url, audio_url FROM notizen"
    )
    where, params = [], []
    if search_query:
        like = f"%{search_query}%"
        where.append("(" + " OR ".join([f"{col} ILIKE %s" for col in ["titel","kategorie","notiz","autor","tags","radiosendung","moderator"]]) + ")")
        params.extend([like] * 7)
    if selected_tag:
        where.append("LOWER(tags) LIKE %s")
        params.append(f"%{selected_tag.lower()}%")
    if where:
        base += sql.SQL(" WHERE " + " AND ".join(where))
    order_map = {
        "datum_desc": "datum DESC",
        "datum_asc": "datum ASC",
        "titel_asc": "titel ASC",
        "titel_desc": "titel DESC",
        # ggf. mehr Sortierungen nach Bedarf
    }
    base += sql.SQL(" ORDER BY " + order_map.get(sort_by, "datum DESC"))
    try:
        cur.execute(base, params)
        rows = cur.fetchall()
        return rows
    except psycopg2.Error as e:
        st.error(f"Fehler beim Abrufen der Notizen: {e}")
        return []
    finally:
        cur.close()

def delete_note(note_id: int):
    _exec("DELETE FROM notizen WHERE id=%s", (note_id,))
