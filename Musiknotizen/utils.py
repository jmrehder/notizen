from __future__ import annotations
import psycopg2
from psycopg2 import sql
import streamlit as st

# --- DB-Konfiguration ---
if "postgres" in st.secrets:
    DB_CONFIG = dict(st.secrets["postgres"])
else:
    DB_CONFIG = {
        "host": "localhost",
        "database": "musiknotizen",
        "user": "postgres",
        "password": "Klavier-4",
        "port": 5433,
        "sslmode": "disable",
    }

@st.cache_resource(show_spinner=False)
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

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

def add_note(
    titel, werk, komponist, epoche, verzeichnis, interpret, notiz, von,
    tags, radiosendung, moderator, datum, audio_bytes
):
    _exec(
        """INSERT INTO notizen
        (titel, werk, komponist, epoche, verzeichnis, interpret, notiz, von, tags, radiosendung, moderator, datum, audio_bytes)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (titel, werk, komponist, epoche, verzeichnis, interpret, notiz, von, tags, radiosendung, moderator, datum, psycopg2.Binary(audio_bytes) if audio_bytes else None),
    )

def get_notes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, titel, werk, komponist, epoche, verzeichnis, interpret, notiz, von, tags, radiosendung, moderator, datum, audio_bytes FROM notizen ORDER BY datum DESC, id DESC"
    )
    rows = cur.fetchall()
    # Bytes richtig umwandeln
    result = []
    for r in rows:
        lst = list(r)
        lst[13] = bytes(lst[13]) if lst[13] is not None else None
        result.append(tuple(lst))
    cur.close()
    return result

def delete_note(note_id: int):
    _exec("DELETE FROM notizen WHERE id=%s", (note_id,))
