import streamlit as st
from utils import get_notes, delete_note
import datetime

st.set_page_config(page_title="Alle Notizen", layout="wide")
st.title("📝 Alle Notizen (Musik)")

notes = get_notes()
if not notes:
    st.info("Keine Notizen gefunden.")
    st.stop()

NOTES_PER_PAGE = 5
page_key = "current_page_all"
st.session_state.setdefault(page_key, 1)
total_pages = (len(notes) - 1) // NOTES_PER_PAGE + 1
st.session_state[page_key] = max(1, min(st.session_state[page_key], total_pages))

def _paginator(pos: str):
    col_prev, col_mid, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.session_state[page_key] > 1 and st.button("⬅️", key=f"prev_{pos}"):
            st.session_state[page_key] -= 1
            st.rerun()
    with col_mid:
        st.markdown(
            f"<h4 style='text-align:center;'>Seite {st.session_state[page_key]} von {total_pages}</h4>",
            unsafe_allow_html=True,
        )
    with col_next:
        if st.session_state[page_key] < total_pages and st.button("➡️", key=f"next_{pos}"):
            st.session_state[page_key] += 1
            st.rerun()

_paginator("top")

start = (st.session_state[page_key] - 1) * NOTES_PER_PAGE
for note in notes[start : start + NOTES_PER_PAGE]:
    (
        note_id, titel, werk, komponist, epoche, verzeichnis, interpret,
        notiz, von, tags, radiosendung, moderator, datum, audio_bytes
    ) = note

    with st.expander(f"{titel} ({werk or ''}, {komponist or ''})"):
        st.markdown(f"**Werk:** {werk or '-'}")
        st.markdown(f"**Komponist:** {komponist or '-'}")
        st.markdown(f"**Epoche:** {epoche or '-'}")
        st.markdown(f"**Verzeichnis:** {verzeichnis or '-'}")
        st.markdown(f"**Interpret:** {interpret or '-'}")
        st.markdown(f"**Von:** {von}")
        st.markdown(f"**Datum:** {datum.strftime('%d.%m.%Y') if isinstance(datum, (datetime.date, datetime.datetime)) else datum}")
        st.markdown(f"**Tags:** {tags or '-'}")
        st.markdown(f"**Radiosendung:** {radiosendung or '-'}")
        st.markdown(f"**Moderator:** {moderator or '-'}")
        st.markdown("---")
        st.write(notiz)
        if audio_bytes:
            st.markdown("**Audio:**")
            st.audio(audio_bytes, format="audio/wav")
        col_e, col_d = st.columns(2)
        with col_d:
            if st.button("🗑️ Löschen", key=f"delbtn_{note_id}"):
                delete_note(note_id)
                st.success("Notiz gelöscht.")
                st.rerun()

_paginator("bottom")
