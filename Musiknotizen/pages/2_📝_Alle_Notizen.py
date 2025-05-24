import streamlit as st
import time
from utils import (
    get_notes,
    delete_note,
    get_youtube_id,
    update_note,
)

st.set_page_config(page_title="Alle Notizen", layout="wide")
st.title("📝 Alle Notizen")
st.markdown("Hier findest du alle deine Notizen – inkl. Bildern, Audio, Radiosendungen & mehr.")

# Filter & Sortierung
st.subheader("Filter und Sortierung")
col_search, col_tag, col_sort = st.columns([3, 2, 2])

with col_search:
    search_query = st.text_input(
        "Suchen (Titel, Notiz, Kategorie, Autor, Tags, Radiosendung, Moderator)",
        key="search_query_all",
    )

# Tags sammeln
all_notes_raw = get_notes()
all_tags = set()
for n in all_notes_raw:
    if n[5]:  # tags
        all_tags.update([t.strip().capitalize() for t in n[5].split(",") if t.strip()])

with col_tag:
    tag_choice = st.selectbox("Nach Tag filtern", ["Alle Tags"] + sorted(all_tags), key="tag_all")
    selected_tag = None if tag_choice == "Alle Tags" else tag_choice

with col_sort:
    sort_map = {
        "Datum (Neueste zuerst)": "datum_desc",
        "Datum (Älteste zuerst)": "datum_asc",
        "Titel (A-Z)": "titel_asc",
        "Titel (Z-A)": "titel_desc",
    }
    sort_by = sort_map[st.selectbox("Sortieren nach", list(sort_map.keys()), key="sort_all")]

st.markdown("---")

notes = get_notes(search_query, selected_tag, sort_by)

if not notes:
    st.info("Keine Notizen gefunden. Erstelle doch eine Neue auf der entsprechenden Seite.")
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
        note_id, titel, kategorie, notiz, autor, tags,
        radiosendung, moderator, datum, bild_url, audio_url
    ) = note

    edit_flag = f"edit_{note_id}"
    st.session_state.setdefault(edit_flag, False)
    header = f"**{titel}** – *{kategorie}* ({autor})"

    with st.expander(header):
        if st.session_state[edit_flag]:
            st.subheader("Notiz bearbeiten")
            with st.form(f"form_{note_id}"):
                t_in  = st.text_input("Titel *", titel)
                k_in  = st.text_input("Kategorie", kategorie or "")
                n_in  = st.text_area("Notiz *", notiz)
                a_in  = st.text_input("Autor", autor or "")
                tag_in= st.text_input("Tags", tags or "")
                r_in  = st.text_input("Radiosendung", radiosendung or "")
                m_in  = st.text_input("Moderator", moderator or "")
                d_in  = st.date_input("Datum", value=datum)
                b_in  = st.text_input("Bild-URL", bild_url or "")
                au_in = st.text_input("Audio-URL", audio_url or "")

                col_s, col_c = st.columns(2)
                with col_s:
                    if st.form_submit_button("Speichern"):
                        if t_in and n_in:
                            update_note(
                                note_id, t_in, k_in, n_in, a_in, tag_in, r_in,
                                m_in, d_in, b_in, au_in
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
            st.markdown(f"**Datum:** {datum.strftime('%d.%m.%Y') if hasattr(datum,'strftime') else datum}")
            st.markdown(f"**Kategorie:** {kategorie}")
            st.markdown(f"**Autor:** {autor}")
            if radiosendung:
                st.markdown(f"**Radiosendung:** {radiosendung}")
            if moderator:
                st.markdown(f"**Moderator:** {moderator}")
            st.write(notiz)
            if bild_url:
                st.image(bild_url, caption="Bild zur Notiz", width=350)
            if audio_url:
                st.markdown("**Audio:**")
                st.audio(audio_url)
            if tags:
                st.markdown("**Tags:**")
                tag_list = [t.strip() for t in tags.split(",") if t.strip()]
                tag_cols = st.columns(len(tag_list) or 1)
                for idx, tg in enumerate(tag_list):
                    with tag_cols[idx]:
                        if st.button(f"#{tg}", key=f"tag_{note_id}_{tg}"):
                            st.session_state["tag_all"] = tg.capitalize()
                            st.rerun()

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
