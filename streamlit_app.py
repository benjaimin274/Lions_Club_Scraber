import streamlit as st
from backend import get_urls, main_all_days, main_current_day

# --- Initialization ----------------------------------------------------------

def init_sessionstates():
    if "all_days" not in st.session_state:
        st.session_state["all_days"] = False
    if "relevant_urls" not in st.session_state:
        st.session_state["relevant_urls"] = get_urls()

init_sessionstates()


# --- Page Setup --------------------------------------------------------------

st.set_page_config(
    page_title="🎄 Adventskalender Auswertung",
    page_icon="🎅",
    layout="centered"
)

st.title("🎄 Lions Club Adventskalender – Auswertung")
st.markdown(
    "<p style='color: gray; font-size: 1.1rem;'>"
    "Finde heraus, ob eine Losnummer gewonnen hat!"
    "</p>",
    unsafe_allow_html=True
)

# --- Mode Selection ----------------------------------------------------------

with st.container():
    st.markdown("### ⚙️ Modus wählen")

    st.toggle(
        "Alle Tage auswerten",
        key="all_days",
        help="Wenn aktiviert, werden alle bisher bekannten Tage ausgewertet."
    )

# --- Divider ----------------------------------------------------------------

st.divider()

# --- Current Day Mode --------------------------------------------------------

if not st.session_state["all_days"]:
    st.markdown("### 📅 Heutige Tagesauswertung")

    if st.button("🔍 Heutigen Tag auswerten", type="primary"):
        wins, failed_extractions = main_current_day(st.session_state["relevant_urls"])

        if wins is None:
            st.warning("Keine Nummer hat heute gewonnen.")
        else:
            num_of_wins = wins.shape[0]
            st.success(f"🎉 Glückwunsch! Du hast **{num_of_wins} Preise** gewonnen!")
            st.table(wins)

        if failed_extractions is not None:
            st.error("Die Extraktion war heute nicht erfolgreich.")
            st.write(f"**Titel:** {failed_extractions['Titel']}")
            st.write(f"**Betroffene URL:** {failed_extractions['Url']}")


# --- All Days Mode -----------------------------------------------------------
else:
    st.markdown("### 📊 Auswertung aller bisherigen Tage")

    if st.button("🗂️ Alle Tage auswerten", type="primary"):
        with st.spinner("⏳ Bitte warten – die vollständige Auswertung läuft…"):
            wins, failed_extractions = main_all_days(st.session_state["relevant_urls"])

        if wins is None:
            st.warning("Es wurde bisher keine gewinnende Nummer gefunden.")
        else:
            num_of_wins = wins.shape[0]
            st.success(f"🎉 Insgesamt wurden **{num_of_wins} Gewinne** erzielt!")
            st.table(wins)

        if failed_extractions is None:
            st.success("Alle Tage konnten erfolgreich ausgewertet werden.")
        else:
            st.error("Bei folgenden Tagen gab es Fehler:")
            st.table(failed_extractions)
            st.info("Bitte überprüfe diese URLs manuell.")