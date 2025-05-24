import streamlit as st
import time

from utils import add_note
from audio_recorder_streamlit import audio_recorder

# ---------------------------------------------------------------------------
# Seite konfigurieren
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Neue Notiz hinzufügen", layout="wide")


st.title("✍️ Neue Notiz hinzufügen")
st.markdown("Fülle die Felder aus, um eine neue Notiz inklusive optionaler Sprachnotiz anzulegen.")

# ---------------------------------------------------------------------------
# Formular
# ---------------------------------------------------------------------------
with st.form("new_note_form", clear_on_submit=True):
    # Pflicht- & optionale Textfelder
    new_titel        = st.text_input("Titel *")
    new_komponist    = st.text_input("Komponist")
    new_werk         = st.text_input("Werk")
    new_interpret    = st.text_input("Interpret (optional)")
    new_notiz        = st.text_area("Notiz *", height=200)
    new_youtube_link = st.text_input("YouTube-Link (optional)")
    new_tags         = st.text_input("Tags (kommasepariert, optional)")

    st.markdown("---")
    st.subheader("Sprachnotiz aufnehmen (optional)")
    audio_bytes = audio_recorder()          # Start/Stop-Button

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        st.success("Sprachnotiz aufgenommen – sie wird zusammen mit der Notiz gespeichert.")

    # -----------------------------------------------------------------------
    # Speichern-Button
    # -----------------------------------------------------------------------
    if st.form_submit_button("Notiz speichern"):
        if new_titel and new_notiz:
            add_note(
                new_titel,
                new_komponist,
                new_werk,
                new_interpret,
                new_notiz,
                new_youtube_link,
                new_tags,
                audio_bytes,           # direkt als BYTEA in Postgres
            )
            st.success("Notiz erfolgreich gespeichert!")
            time.sleep(1)
            st.rerun()                # Streamlit ≥ 1.22
        else:
            st.warning("Titel und Notiz sind Pflichtfelder und dürfen nicht leer sein.")
