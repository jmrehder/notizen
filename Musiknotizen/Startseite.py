"""Startseite – Musiknotizen
Schicker Welcome‑Screen mit Kennzahlen, Quick‑Links & sanftem Dark‑Theme‑Styling
"""




# ---------------------------------------------------------------------------
# Seiteneinstellungen
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Mamas Notizen zur klassischen Musik 🎼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Login‑Gate
# ---------------------------------------------------------------------------
if not check_password():
    st.info("Bitte melde dich an, um die Notizen anzuzeigen und zu verwalten.")
    st.stop()

# ---------------------------------------------------------------------------
# Mini‑CSS für weichere Karten & zentriertes Layout
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* zarte Karten für Kennzahlen */
.metric-card {
    background: #202437;
    border-radius: 0.75rem;
    padding: 1.2rem 0.5rem;
    text-align: center;
    box-shadow: 0 2px 6px rgba(0,0,0,0.25);
}
.metric-card h1 {
    font-size: 2.5rem;
    margin: 0.2rem 0 0.4rem 0;
}
.metric-card p {
    margin: 0;
    letter-spacing: .5px;
    color: #aaa;
}
/* Link‑Buttons */
.quicklink {
    display: flex;
    align-items: center;
    gap: .45rem;
    padding: .8rem 1rem;
    border-radius: .8rem;
    background:#1b1f30;
    color: #fff !important;
    text-decoration:none;
    font-weight:600;
    transition:background .2s;
}
.quicklink:hover {
    background:#26304d;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Datenbank‑Kennzahlen
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
# Hero‑Banner
# ---------------------------------------------------------------------------
col_hero_l, col_hero_r = st.columns([4, 3], gap="large")

with col_hero_l:
    st.markdown(
        """
        ## 👋 Willkommen bei **Mamas Notizen zur klassischen Musik**
        Behalte den Überblick über deine Lieblingsaufnahmen, spontanen Gedanken
        & <span style='white-space:nowrap;'>🤳 Sprachnotizen</span>!
        """,
        unsafe_allow_html=True,
    )
    st.write("Nutze die Navigation links, um neue Einträge zu erstellen oder deine Sammlung zu durchsuchen.")

with col_hero_r:
    st.image(
        "https://images.unsplash.com/photo-1508973478649-170737c2ec72?auto=format&fit=crop&w=700&q=80",
        caption="Musik verbindet – © Unsplash",
        use_container_width=True,
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Kennzahlen in Karten
# ---------------------------------------------------------------------------
metric_cols = st.columns(4, gap="medium")
metrics = [
    ("📚 Notizen", count_notes),
    ("🎼 Komponisten", count_composers),
    ("🎵 Werke", count_works),
    ("🏷️ Tags", count_tags),
]
for col, (label, val) in zip(metric_cols, metrics):
    with col:
        st.markdown(
            f"""
            <div class='metric-card'>
                <p>{label}</p>
                <h1>{val}</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Quick‑Links als hübsche Buttons
# ---------------------------------------------------------------------------
link_cols = st.columns([1, 1, 6])
with link_cols[0]:
    st.markdown("<a class='quicklink' href='./?page=✍️ Neue Notiz'>📝 ✍️ Neue Notiz</a>", unsafe_allow_html=True)
with link_cols[1]:
    st.markdown("<a class='quicklink' href='./?page=📝 Alle Notizen'>📖 Alle Notizen</a>", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Footer‑Hinweis
# ---------------------------------------------------------------------------
st.info("💡 **Tipp:** Klicke in der Ansicht *Alle Notizen* auf ein Tag‑Label, um sofort nach diesem Tag zu filtern.")
