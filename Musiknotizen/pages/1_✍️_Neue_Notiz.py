import streamlit as st
import time
from utils import add_note
from audio_recorder_streamlit import audio_recorder
from datetime import date

st.set_page_config(page_title="Neue Notiz hinzufügen", layout="wide")
st.title("✍️ Neue Notiz hinzufügen")
st.markdown(
    "Fülle die Felder aus, um eine neue Notiz aus allen Bereichen der Kunst zu speichern – egal ob Musik, Literatur, Malerei, Ausstellung, Bühnenstück, Radiosendung, …"
)

KATEGORIEN = [
    "Musik", "Literatur", "Gemälde", "Ausstellung", "Bühnenstück", "Sonstige"
]
AUTOREN = ["Cornelia", "Jörg-Martin"]

with st.form("new_note_form", clear_on_submit=True):
    new_titel       = st.text_input("Titel *")
    new_kategorie   = st.selectbox("Kategorie *", KATEGORIEN)
    new_notiz       = st.text_area("Notiz *", height=180)
    new_autor       = st.selectbox("Autor *", AUTOREN, index=0)
    new_tags        = st.text_input("Tags (kommasepariert, optional)")
    new_radiosendung = st.text_input("Radiosendung (optional)")
    new_moderator   = st.text_input("Moderator (optional)")
    new_zusatzinfo  = st.text_area("Zusatzinfo (optional)", height=80)
    new_datum       = st.date_input("Datum", date.today())
    
    st.markdown("---")
    # Bild-Upload (Cloudflare-Link muss selbst erzeugt werden nach Upload!)
    new_bild_url = st.text_input("Bild-URL (optional, nach Upload zu Cloudflare)")
    
    st.subheader("Audio aufnehmen (optional, nach Upload URL einfügen)")
    # Aufnahme-Widget (Tondatei ggf. selbst nach Cloudflare laden)
    audio_bytes = audio_recorder()
    new_audio_url = st.text_input("Audio-URL (optional, nach Upload zu Cloudflare)")
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        st.info("Du kannst die Datei lokal speichern und dann zu Cloudflare hochladen.")

    # Speichern
    if st.form_submit_button("Notiz speichern"):
        if new_titel and new_notiz:
            # Zusatzinfo als JSON, wenn du später strukturierte Daten willst, ansonsten als Text
            zusatzinfo = new_zusatzinfo
            add_note(
                new_titel, new_kategorie, new_notiz, new_autor, new_tags, new_radiosendung, new_moderator,
                zusatzinfo, new_datum, new_bild_url, new_audio_url
            )
            st.success("Notiz erfolgreich gespeichert!")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("Titel, Kategorie und Notiz sind Pflichtfelder.")
