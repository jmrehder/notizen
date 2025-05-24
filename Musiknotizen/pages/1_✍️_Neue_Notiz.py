import streamlit as st
from datetime import date
from utils import add_note
from audio_recorder_streamlit import audio_recorder
import time

st.set_page_config(page_title="Neue Musik-Notiz", layout="wide")
st.title("✍️ Neue Notiz (Musik)")

with st.form("new_note_form", clear_on_submit=True):
    titel        = st.text_input("Titel *")
    werk         = st.text_input("Werk")
    komponist    = st.text_input("Komponist")
    epoche       = st.text_input("Epoche")
    verzeichnis  = st.text_input("Verzeichnis")
    interpret    = st.text_input("Interpret")
    notiz        = st.text_area("Notiz *", height=150)
    von          = st.text_input("Von", value="Cornelia")
    tags         = st.text_input("Tags (optional)")
    radiosendung = st.text_input("Radiosendung (optional)")
    moderator    = st.text_input("Moderator (optional)")
    datum        = st.date_input("Datum", date.today())
    st.markdown("---")
    st.subheader("Audio aufnehmen (optional)")
    audio_bytes = audio_recorder()

    submitted = st.form_submit_button("Notiz speichern")
    if submitted:
        if titel and notiz:
            add_note(
                titel, werk, komponist, epoche, verzeichnis, interpret, notiz, von,
                tags, radiosendung, moderator, datum, audio_bytes
            )
            st.success("Notiz gespeichert!")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("Titel und Notiz sind Pflichtfelder.")
