import streamlit as st
from utils import get_notes, delete_note, update_note
from audio_recorder_streamlit import audio_recorder
import datetime

st.set_page_config(page_title="Alle Notizen (Musik)", layout="wide")
st.title("📝 Alle Notizen (Musik)")

# ----------- Suchfeld und Filter ----------
with st.expander("🔎 Erweiterte Suche & Filter", expanded=True):
    col1, col2, col3 = st.columns([3,2,3])
    with col1:
        search_query = st.text_input(
            "Suche in Titel, Werk, Komponist, Interpret, Notiz, Tags, Radiosendung, Moderator",
            value=st.session_state.get("search_query", ""),
            key="search_query",
        )
    with col2:
        tag_filter = st.text_input("Nach Tag filtern (optional)", value=st.session_state.get("tag_filter", ""), key="tag_filter")
    with col3:
        date_mode = st.radio("Filtern nach Datum", ["Kein Filter", "Bestimmtes Datum", "Zeitraum"], horizontal=True)
        if date_mode == "Bestimmtes Datum":
            date_exact = st.date_input("Datum auswählen", key="date_exact")
        elif date_mode == "Zeitraum":
            date_from = st.date_input("Von", key="date_from")
            date_to   = st.date_input("Bis", key="date_to")

# ----------- Daten holen & filtern ----------
notes = get_notes()
if not notes:
    st.info("Keine Notizen gefunden.")
    st.stop()

def matches(note):
    (
        _id, titel, werk, komponist, epoche, verzeichnis, interpret,
        notiz, von, tags, radiosendung, moderator, datum, audio_bytes
    ) = note
    query = search_query.lower()
    tagf = tag_filter.lower()
    # Suchen in allen relevanten Feldern
    haystack = " ".join(str(x or "").lower() for x in [
        titel, werk, komponist, epoche, verzeichnis, interpret, notiz, von, tags, radiosendung, moderator
    ])
    # Suche
    if query and query not in haystack:
        return False
    if tagf and (tagf not in (tags or "").lower()):
        return False
    # Datumsfilter
    if date_mode == "Bestimmtes Datum":
        if not datum or datum != date_exact:
            return False
    elif date_mode == "Zeitraum":
        if not datum or not (date_from <= datum <= date_to):
            return False
    return True

notes = list(filter(matches, notes))

# ----------- Pagination ----------
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

# ----------- Anzeige und Bearbeiten ----------
start = (st.session_state[page_key] - 1) * NOTES_PER_PAGE
for note in notes[start : start + NOTES_PER_PAGE]:
    (
        note_id, titel, werk, komponist, epoche, verzeichnis, interpret,
        notiz, von, tags, radiosendung, moderator, datum, audio_bytes
    ) = note

    edit_flag = f"edit_{note_id}"
    st.session_state.setdefault(edit_flag, False)

    with st.expander(f"{titel} ({werk or ''}, {komponist or ''})"):
        if st.session_state[edit_flag]:
            st.subheader("Notiz bearbeiten")
            with st.form(f"form_{note_id}"):
                t_in  = st.text_input("Titel *", titel)
                w_in  = st.text_input("Werk", werk or "")
                k_in  = st.text_input("Komponist", komponist or "")
                e_in  = st.text_input("Epoche", epoche or "")
                v_in  = st.text_input("Verzeichnis", verzeichnis or "")
                i_in  = st.text_input("Interpret", interpret or "")
                n_in  = st.text_area("Notiz *", notiz)
                von_in= st.text_input("Von", von or "")
                tag_in= st.text_input("Tags", tags or "")
                r_in  = st.text_input("Radiosendung", radiosendung or "")
                m_in  = st.text_input("Moderator", moderator or "")
                d_in  = st.date_input("Datum", value=datum if datum else datetime.date.today())
                
                # Audio-Bereich
                st.markdown("**Vorhandene Audio-Notiz:**")
                remove_audio = False
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/wav")
                    remove_audio = st.checkbox("Sprachnotiz löschen", key=f"remove_audio_{note_id}")
                else:
                    st.info("Kein Audio gespeichert.")
                st.markdown("**Neues Audio aufnehmen oder hochladen (optional, ersetzt vorhandene Aufnahme):**")
                new_audio = audio_recorder()
                audio_file = st.file_uploader("Oder lade eine Audiodatei hoch", type=["wav", "mp3", "ogg"])
                updated_audio = None
                if new_audio:
                    updated_audio = new_audio
                    st.success("Neue Aufnahme bereit!")
                elif audio_file:
                    updated_audio = audio_file.read()
                    st.success("Audiodatei bereit!")

                col_s, col_c = st.columns(2)
                with col_s:
                    if st.form_submit_button("Speichern"):
                        if t_in and n_in:
                            # Audio löschen geht vor Upload/Beibehalten!
                            if remove_audio:
                                final_audio = None
                            elif updated_audio is not None:
                                final_audio = updated_audio
                            else:
                                final_audio = audio_bytes

                            update_note(
                                note_id, t_in, w_in, k_in, e_in, v_in, i_in,
                                n_in, von_in, tag_in, r_in, m_in, d_in, final_audio
                            )
                            st.session_state[edit_flag] = False
                            st.success("Gespeichert.")
                            st.rerun()
                        else:
                            st.warning("Titel und Notiz sind Pflichtfelder.")
                with col_c:
                    if st.form_submit_button("Abbrechen"):
                        st.session_state[edit_flag] = False
                        st.rerun()
        else:
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
            with col_e:
                if st.button("✏️ Bearbeiten", key=f"editbtn_{note_id}"):
                    st.session_state[edit_flag] = True
                    st.rerun()
            with col_d:
                if st.button("🗑️ Löschen", key=f"delbtn_{note_id}"):
                    delete_note(note_id)
                    st.success("Notiz gelöscht.")
                    st.rerun()

_paginator("bottom")
