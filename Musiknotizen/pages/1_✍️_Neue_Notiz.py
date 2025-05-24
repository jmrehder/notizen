import streamlit as st
import time
from utils import add_note
from cloudflare_upload import upload_to_r2
from audio_recorder_streamlit import audio_recorder
from datetime import date
import uuid

st.set_page_config(page_title="Neue Notiz hinzufügen", layout="wide")
st.title("✍️ Neue Notiz zu Musik, Kunst & Kultur")

KATEGORIEN = ["Musik", "Literatur", "Gemälde", "Ausstellung", "Bühnenstück", "Sonstige"]
AUTOREN = ["Cornelia", "Jörg-Martin"]

# Cloudflare-Config aus st.secrets
cf = st.secrets["cloudflare"]
CF_ACCOUNT_ID = cf["account_id"]
CF_ACCESS_KEY = cf["access_key"]
CF_SECRET_KEY = cf["secret_key"]
CF_BUCKET     = cf["bucket"]

with st.form("new_note_form", clear_on_submit=True):
    new_titel        = st.text_input("Titel *")
    new_kategorie    = st.selectbox("Kategorie *", KATEGORIEN)
    new_notiz        = st.text_area("Notiz *", height=160)
    new_autor        = st.selectbox("Autor *", AUTOREN, index=0)
    new_tags         = st.text_input("Tags (kommasepariert, optional)")
    new_radiosendung = st.text_input("Radiosendung (optional)")
    new_moderator    = st.text_input("Moderator (optional)")
    new_datum        = st.date_input("Datum", date.today())

    # ---- Bild-Upload
    bild_file = st.file_uploader("Bild hochladen (optional)", type=["png", "jpg", "jpeg", "gif"])
    bild_url = None
    if bild_file:
        unique_name = f"bilder/{uuid.uuid4()}_{bild_file.name}"
        bild_url = upload_to_r2(
            bild_file.read(), unique_name, bild_file.type,
            CF_ACCOUNT_ID, CF_ACCESS_KEY, CF_SECRET_KEY, CF_BUCKET
        )
        st.success("Bild erfolgreich hochgeladen!")
        st.image(bild_url, width=300)

    # ---- Audio aufnehmen und hochladen
    st.subheader("Audio aufnehmen oder hochladen (optional)")
    audio_bytes = audio_recorder()
    audio_url = None
    if audio_bytes:
        unique_name = f"audio/{uuid.uuid4()}.wav"
        audio_url = upload_to_r2(
            audio_bytes, unique_name, "audio/wav",
            CF_ACCOUNT_ID, CF_ACCESS_KEY, CF_SECRET_KEY, CF_BUCKET
        )
        st.success("Audio erfolgreich hochgeladen!")
        st.audio(audio_url, format="audio/wav")

    # Alternativ auch Upload eines bestehenden Audio-Files:
    audio_file = st.file_uploader("Oder lade eine Audiodatei hoch (optional)", type=["wav", "mp3", "ogg"])
    if audio_file:
        unique_name = f"audio/{uuid.uuid4()}_{audio_file.name}"
        audio_url = upload_to_r2(
            audio_file.read(), unique_name, audio_file.type,
            CF_ACCOUNT_ID, CF_ACCESS_KEY, CF_SECRET_KEY, CF_BUCKET
        )
        st.success("Audiofile erfolgreich hochgeladen!")
        st.audio(audio_url)

    # ---- Formular abschicken
    submitted = st.form_submit_button("Notiz speichern")
    if submitted:
        if new_titel and new_notiz and new_kategorie:
            add_note(
                new_titel, new_kategorie, new_notiz, new_autor, new_tags, new_radiosendung,
                new_moderator, new_datum, bild_url, audio_url
            )
            st.success("Notiz erfolgreich gespeichert!")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("Titel, Kategorie und Notiz sind Pflichtfelder.")
