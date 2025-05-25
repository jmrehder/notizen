import streamlit as st
from utils import get_notes, delete_note, update_note
from audio_recorder_streamlit import audio_recorder
import datetime

st.set_page_config(page_title="Alle Notizen (Musik)", layout="wide")
st.title("📝 Alle Notizen (Musik)")

notes_all = get_notes()
if not notes_all:
    st.info("Keine Notizen gefunden.")
    st.stop()

# ----------------------------- FILTER ------------------------------
with st.expander("🔎 Erweiterte Suche & Filter", expanded=True):

    # --- 1. Zeile: Freitext + Tag ---
    col_search, col_tag = st.columns([3, 2])
    with col_search:
        search_query = st.text_input(
            "Suche (Titel, Werk, Komponist, Notiz, ...)",
            key="search_query",
            placeholder="z.B. Mozart, Sonate, Lieblingsstück ..."
        )
    # Tag-Dropdown aus allen Tags generieren
    tag_set = {t.strip().capitalize()
               for n in notes_all for t in (n[9] or "").split(",") if t.strip()}
    tags_sorted = sorted(tag_set)
    with col_tag:
        tag_choice = st.selectbox("Nach Tag filtern", ["Alle"] + tags_sorted, key="tag_choice")
        selected_tag = None if tag_choice == "Alle" else tag_choice

    st.markdown("----")  # Trennlinie in Expander

    # --- 2. Zeile: Datums-Filter ---
    date_mode = st.radio(
        "Datumsfilter", ["Kein Filter", "Bestimmtes Datum", "Zeitraum"],
        horizontal=True, key="date_mode"
    )
    date_exact = date_from = date_to = None
    if date_mode == "Bestimmtes Datum":
        date_exact = st.date_input("Datum auswählen", value=datetime.date.today(), key="date_exact")
    elif date_mode == "Zeitraum":
        col_from, col_to = st.columns(2)
        with col_from:
            date_from = st.date_input("Von", value=datetime.date.today() - datetime.timedelta(days=30), key="date_from")
        with col_to:
            date_to   = st.date_input("Bis", value=datetime.date.today(), key="date_to")

# ------------------------ FILTER-LOGIK -----------------------------
def passes_filter(note):
    (
        _id, titel, werk, komponist, epoche, verzeichnis, interpret,
        notiz, von, tags, radiosendung, moderator, datum, audio_bytes
    ) = note

    # 1) Freitext
    if search_query:
        haystack = " ".join(str(x or "").lower() for x in
            [titel, werk, komponist, epoche, verzeichnis, interpret,
             notiz, von, tags, radiosendung, moderator])
        if search_query.lower() not in haystack:
            return False

    # 2) Tag-Filter
    if selected_tag and selected_tag.lower() not in (tags or "").lower():
        return False

    # 3) Datums-Filter
    if date_mode == "Bestimmtes Datum":
        if not datum or datum != date_exact:
            return False
    elif date_mode == "Zeitraum":
        if not datum or datum < date_from or datum > date_to:
            return False

    return True

notes = [n for n in notes_all if passes_filter(n)]

# ------------------------ PAGINATION -------------------------------
NOTES_PER_PAGE = 5
page_key = "current_page_all"
st.session_state.setdefault(page_key, 1)
total_pages = (len(notes) - 1) // NOTES_PER_PAGE + 1
st.session_state[page_key] = max(1, min(st.session_state[page_key], total_pages))

def paginator(where):
    c1, c2, c3 = st.columns([1, 2, 1])
    if st.session_state[page_key] > 1:
        if c1.button("⬅️", key=f"prev_{where}"):
            st.session_state[page_key] -= 1
            st.rerun()
    c2.markdown(
        f"<h4 style='text-align:center;'>Seite {st.session_state[page_key]} / {total_pages}</h4>",
        unsafe_allow_html=True,
    )
    if st.session_state[page_key] < total_pages:
        if c3.button("➡️", key=f"next_{where}"):
            st.session_state[page_key] += 1
            st.rerun()

paginator("top")

# ------------------- ANZEIGE & BEARBEITEN --------------------------
start = (st.session_state[page_key] - 1) * NOTES_PER_PAGE
for note in notes[start:start + NOTES_PER_PAGE]:
    (
        note_id, titel, werk, komponist, epoche, verzeichnis, interpret,
        notiz, von, tags, radiosendung, moderator, datum, audio_bytes
    ) = note

    edit_key = f"edit_{note_id}"
    st.session_state.setdefault(edit_key, False)

    with st.expander(f"{titel} ({werk or ''} – {komponist or '-'})"):
        if st.session_state[edit_key]:
            # ---------- Bearbeitungs-Form ----------
            with st.form(f"form_{note_id}"):
                t = st.text_input("Titel *", titel)
                w = st.text_input("Werk", werk or "")
                k = st.text_input("Komponist", komponist or "")
                e = st.text_input("Epoche", epoche or "")
                v = st.text_input("Verzeichnis", verzeichnis or "")
                i = st.text_input("Interpret", interpret or "")
                n = st.text_area("Notiz *", notiz)
                von_in = st.text_input("Von", von or "")
                tg = st.text_input("Tags", tags or "")
                r = st.text_input("Radiosendung", radiosendung or "")
                m = st.text_input("Moderator", moderator or "")
                d = st.date_input("Datum", value=datum or datetime.date.today())
                # ---- Audio: bestehend / neu / löschen
                remove_audio = st.checkbox("Audio löschen", value=False, key=f"rem_{note_id}")
                if audio_bytes and not remove_audio:
                    st.audio(audio_bytes, format="audio/wav")
                new_audio = audio_recorder()
                up_file   = st.file_uploader("Audiodatei hochladen", type=["wav","mp3","ogg"])
                new_audio_bytes = new_audio or (up_file.read() if up_file else None)

                col_save, col_cancel = st.columns(2)
                if col_save.form_submit_button("Speichern"):
                    if t and n:
                        final_audio = None if remove_audio else (new_audio_bytes or audio_bytes)
                        update_note(note_id, t, w, k, e, v, i, n, von_in, tg, r, m, d, final_audio)
                        st.session_state[edit_key] = False
                        st.success("Gespeichert.")
                        st.rerun()
                    else:
                        st.warning("Titel und Notiz sind Pflichtfelder.")
                if col_cancel.form_submit_button("Abbrechen"):
                    st.session_state[edit_key] = False
                    st.rerun()
        else:
            # ---------- Anzeige-Modus ----------
            st.markdown(f"**Werk:** {werk or '-'}")
            st.markdown(f"**Komponist:** {komponist or '-'}")
            st.markdown(f"**Epoche:** {epoche or '-'}")
            st.markdown(f"**Verzeichnis:** {verzeichnis or '-'}")
            st.markdown(f"**Interpret:** {interpret or '-'}")
            st.markdown(f"**Von:** {von}")
            if datum:
                st.markdown(f"**Datum:** {datum:%d.%m.%Y}")
            st.markdown(f"**Tags:** {tags or '-'}")
            st.markdown(f"**Radiosendung:** {radiosendung or '-'}")
            st.markdown(f"**Moderator:** {moderator or '-'}")
            st.write(notiz)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
            col_edit, col_delete = st.columns(2)
            if col_edit.button("✏️ Bearbeiten", key=f"editbtn_{note_id}"):
                st.session_state[edit_key] = True
                st.rerun()
            if col_delete.button("🗑️ Löschen", key=f"del_{note_id}"):
                delete_note(note_id)
                st.success("Notiz gelöscht.")
                st.rerun()

paginator("bottom")
