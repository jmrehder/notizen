"""Startseite – Musiknotizen
Hero‑Banner, Kennzahlen, Quick-Links – plus Pooler‑Verbindung (Secrets) funktioniert jetzt.
"""

import streamlit as st
from utils import get_db_connection

# ---------------------------------------------------------------------------
# Seiteneinstellungen (muss das erste Streamlit-Kommando sein!)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Mamas Notizen zur klassischen Musik 🎼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Auth-Check
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Daten abrufen (Kennzahlen)
# ---------------------------------------------------------------------------
conn = get_db_connection()
cur  = conn.cursor()
cur.execute("SELECT COUNT(*), COUNT(DISTINCT komponist), COUNT(DISTINCT werk) FROM notizen")
count_notes, count_composers, count_works = cur.fetchone()
cur.execute("SELECT tags FROM notizen WHERE tags IS NOT NULL")
all_tags = set()
for (tag_str,) in cur.fetchall():
    all_tags.update(t.strip().capitalize() for t in tag_str.split(',') if t.strip())
count_tags = len(all_tags)
cur.close()

# ---------------------------------------------------------------------------
# Mini‑CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .metric-card{background:#202437;border-radius:.75rem;padding:1.2rem .5rem;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,.25)}
    .metric-card h1{font-size:2.5rem;margin:.2rem 0 .4rem 0}
    .metric-card p{margin:0;color:#aaa}
    .quicklink{display:flex;align-items:center;gap:.45rem;padding:.8rem 1rem;border-radius:.8rem;background:#1b1f30;color:#fff!important;font-weight:600;text-decoration:none;transition:background .2s}
    .quicklink:hover{background:#26304d}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Hero‑Banner
# ---------------------------------------------------------------------------
col_l, col_r = st.columns([4,3], gap="large")
with col_l:
    st.markdown("## 👋 Willkommen bei **Mamas Notizen zur klassischen Musik**")
    st.write("Behalte den Überblick über Lieblingsaufnahmen, spontane Gedanken & 🤳 Sprachnotizen!")
with col_r:
    st.image(
        "https://images.unsplash.com/photo-1508973478649-170737c2ec72?auto=format&fit=crop&w=700&q=80",
        caption="Musik verbindet – © Unsplash",
        use_container_width=True,
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Kennzahlen
# ---------------------------------------------------------------------------
cols = st.columns(4, gap="medium")
labels_values = [
    ("📚 Notizen", count_notes),
    ("🎼 Komponisten", count_composers),
    ("🎵 Werke", count_works),
    ("🏷️ Tags", count_tags),
]
for c, (label, val) in zip(cols, labels_values):
    with c:
        st.markdown(f"<div class='metric-card'><p>{label}</p><h1>{val}</h1></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Quick‑Links
# ---------------------------------------------------------------------------
ql1, ql2, _ = st.columns([1,1,6])
with ql1:
    st.markdown("<a class='quicklink' href='./?page=✍️ Neue Notiz'>📝 ✍️ Neue Notiz</a>", unsafe_allow_html=True)
with ql2:
    st.markdown("<a class='quicklink' href='./?page=📝 Alle Notizen'>📖 Alle Notizen</a>", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Footer-Tipp
# ---------------------------------------------------------------------------
st.info("💡 Tipp: In der Ansicht *Alle Notizen* kannst du per Klick auf ein Tag sofort filtern.")
