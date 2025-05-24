import streamlit as st
import time
import uuid

from utils import (
    get_notes,
    delete_note,
    get_youtube_id,
    update_note,
)

from audio_recorder_streamlit import audio_recorder

# ---------------------------------------------------------------------------
# Seite konfigurieren
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Alle Notizen", layout="wide")


st.title("📝 Alle Notizen")
st.markdown("Hier findest du alle deine Notizen – inkl. eingebetteter Audio-Memos aus der Datenbank.")

# ---------------------------------------------------------------------------
# Filter & Sortierung
# ---------------------------------------------------------------------------
st.subheader("Filter und Sortierung")
col_search, col_tag, col_sort = st.columns([3, 2, 2])

with col_search:
    search_query = st.text_input(
        "Suchen (Titel, Komponist, Werk, Interpret, Notiz, Tags)",
        key="search_query_all",
    )

# Tag-Liste für Dropdown sammeln (ohne Bytea mitzuliefern)
all_notes_raw = get_notes()
all_tags = set()
for n in all_notes_raw:
    if n[7]:
        all_tags.update([t.strip().capitalize() for t in n[7].split(",") if t.strip()])

with col_tag:
    tag_choice = st.selectbox("Nach Tag filtern", ["Alle Tags"] + sorted(all_tags), key="tag_all")
    selected_tag = None if tag_choice == "Alle Tags" else tag_choice

with col_sort:
    sort_map = {
        "Datum (Neueste zuerst)": "datum_desc",
        "Datum (Älteste zuerst)": "datum_asc",
        "Titel (A-Z)": "titel_asc",
        "Titel (Z-A)": "titel_desc",
        "Komponist (A-Z)": "komponist_asc",
        "Komponist (Z-A)": "komponist_desc",
        "Interpret (A-Z)": "interpret_asc",
        "Interpret (Z-A)": "interpret_desc",
    }
    sort_by = sort_map[st.selectbox("Sortieren nach", list(sort_map.keys()), key="sort_all")]

st.markdown("---")

# ---------------------------------------------------------------------------
# Notizen abrufen
# ---------------------------------------------------------------------------
notes = get_notes(search_query, selected_tag, sort_by)

if not notes:
    st.info("Keine Notizen gefunden. Erstelle doch eine Neue auf der entsprechenden Seite.")
    st.stop()

# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------
NOTES_PER_PAGE = 5
page_key = "current_page_all"
st.session_state.setdefault(page_key, 1)

total_pages = (len(notes) - 1) // NOTES_PER_PAGE + 1
st.session_state[page_key] = max(1, min(st.session_state[page_key], total_pages))

# Helper für Paginator

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

# ---------------------------------------------------------------------------
# Seite anzeigen
# ---------------------------------------------------------------------------
start = (st.session_state[page_key] - 1) * NOTES_PER_PAGE
for note in notes[start : start + NOTES_PER_PAGE]:
    (
        note_id,
        titel,
        komponist,
        werk,
        interpret,
        notiz_text,
        youtube_link,
        tags_text,
        datum,
        audio_bytes,  # BYTEA-Spalte ‼️
    ) = note

    edit_flag = f"edit_{note_id}"
    st.session_state.setdefault(edit_flag, False)

    header = f"**{titel}** – *{komponist or 'Unbekannter Komponist'}* ({werk or 'Unbekanntes Werk'})"
    with st.expander(header):
        # -------------------------------------------------------------------
        # Bearbeitungsmodus
        # -------------------------------------------------------------------
        if st.session_state[edit_flag]:
            st.subheader("Notiz bearbeiten")
            with st.form(f"form_{note_id}"):
                t_in  = st.text_input("Titel *", titel)
                c_in  = st.text_input("Komponist", komponist or "")
                w_in  = st.text_input("Werk", werk or "")
                i_in  = st.text_input("Interpret", interpret or "")
                n_in  = st.text_area("Notiz *", notiz_text)
                y_in  = st.text_input("YouTube-Link", youtube_link or "")
                tag_in= st.text_input("Tags", tags_text or "")

                st.markdown("---")
                st.subheader("Sprachnotiz")

                # Vorhandene Memo abspielen & Löschoption
                choice_audio = audio_bytes  # default bleibt unverändert
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/wav")
                    if st.checkbox("Sprachnotiz löschen", key=f"del_{note_id}"):
                        choice_audio = None

                # Neue Aufnahme
                new_audio = audio_recorder(key=f"rec_{note_id}")
                if new_audio:
                    st.success("Neue Sprachnotiz aufgenommen.")
                    choice_audio = new_audio

                # Buttons
                col_s, col_c = st.columns(2)
                with col_s:
                    if st.form_submit_button("Speichern"):
                        if t_in and n_in:
                            update_note(
                                note_id,
                                t_in,
                                c_in,
                                w_in,
                                i_in,
                                n_in,
                                y_in,
                                tag_in,
                                choice_audio,
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

        # -------------------------------------------------------------------
        # Anzeige-Modus
        # -------------------------------------------------------------------
        else:
            st.markdown(f"**Datum:** {datum.strftime('%d.%m.%Y %H:%M')}")
            if komponist:
                st.markdown(f"**Komponist:** {komponist}")
            if werk:
                st.markdown(f"**Werk:** {werk}")
            if interpret:
                st.markdown(f"**Interpret:** {interpret}")
            st.write(notiz_text)

            if audio_bytes:
                st.markdown("**Sprachnotiz:**")
                st.audio(audio_bytes, format="audio/wav")

            if tags_text:
                st.markdown("**Tags:**")
                tl = [t.strip() for t in tags_text.split(",") if t.strip()]
                tag_cols = st.columns(len(tl) or 1)
                for idx, tg in enumerate(tl):
                    with tag_cols[idx]:
                        if st.button(f"#{tg}", key=f"tag_{note_id}_{tg}"):
                            st.session_state["tag_all"] = tg.capitalize()
                            st.rerun()

            if youtube_link:
                vid = get_youtube_id(youtube_link)
                if vid:
                    st.video(f"https://www.youtube-nocookie.com/embed/{vid}")
                else:
                    st.warning("Ungültiger YouTube-Link")

            st.markdown("---")
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
