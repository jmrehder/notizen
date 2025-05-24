import streamlit as st
from utils import get_db_connection

st.set_page_config(
    page_title="Mamas Notizen zur Musik & Kunst 🎼🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------- Mini-CSS für mehr Charme --------------------------
st.markdown("""
    <style>
    body { background: #22243a !important; }
    .big-hello { font-size: 2.2rem; font-weight: bold; color: #fff; margin-bottom: 0.6em; }
    .subtitle { font-size: 1.25rem; color: #d9dbe8; margin-bottom: 1.3em; }
    .metric-card{background:#202437;border-radius:.75rem;padding:1.2rem .5rem;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,.25)}
    .metric-card h1{font-size:2.5rem;margin:.2rem 0 .4rem 0}
    .metric-card p{margin:0;color:#aaa}
    .quicklink{display:flex;align-items:center;gap:.45rem;padding:.8rem 1rem;border-radius:.8rem;background:#33436d;color:#fff!important;font-weight:600;text-decoration:none;transition:background .2s}
    .quicklink:hover{background:#415b9c}
    .note-hint{background: #f7f6ee; border-radius: .7rem; padding: 1.2em 1em; color: #444; margin: 2em 0 1.2em 0; font-size: 1.06rem;}
    .footer-jmr {text-align: center; color: #aaa; font-size: 1.07em; margin-top: 2em; letter-spacing: 0.03em;}
    </style>
""", unsafe_allow_html=True)

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
# Hero-Banner (zentriert, ohne Bild, mit JmrStudios)
# ---------------------------------------------------------------------------
st.markdown('<div class="big-hello">👋 Willkommen, Mama!</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">'
    'Hier ist dein persönliches Tagebuch für alles rund um Musik und Kunst – egal ob Klassik, Jazz, Rock, moderne Musik, Lesungen, '
    'Künstler:innen, Ausstellungen oder deine liebsten Radiosendungen!<br>'
    'Halte besondere Erlebnisse, Werke, Namen, Ideen und auch spontane Inspirationen jederzeit fest. '
    '<b>Deine Notizen sind für die ganze Welt der Kunst gemacht!</b>'
    '</div>',
    unsafe_allow_html=True
)
st.markdown("""
    <div class="note-hint">
        <b>Neu:</b> Notiere jetzt alles zu <span style="color:#4761ab"><b>Radiosendungen</b></span> – mit Moderator, Sendedatum oder besonderen Eindrücken!
        <br>
        Aber auch alles andere aus der Welt der Kunst: Konzertmomente, Gemälde, Gedichte, Lesungen oder Ausstellungen – deiner Kreativität sind keine Grenzen gesetzt! 🎙️🎨🎶
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Kennzahlen
# ---------------------------------------------------------------------------
cols = st.columns(4, gap="medium")
labels_values = [
    ("📚 Notizen", count_notes),
    ("🎼 Komponist:innen", count_composers),
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
# Footer-Tipp & JmrStudios
# ---------------------------------------------------------------------------
st.info(
    "💡 Tipp: In der Ansicht *Alle Notizen* kannst du per Klick auf ein Tag sofort filtern. "
    "Und in jeder Notiz kannst du jetzt nicht nur Musik, sondern auch Kunstwerke, Künstler:innen, Radiosendungen, Moderatoren und all deine persönlichen Eindrücke festhalten! 🎶🎨"
)
st.markdown('<div class="footer-jmr">Musik & Kunst verbinden – <b>JmrStudios</b></div>', unsafe_allow_html=True)
