"""
scout_app.py
------------
Streamlit front-end for the Field Hockey Scout Web Scraper.

Run with:
    streamlit run scout_app.py

Dependencies:
    pip install streamlit
"""

import re
import streamlit as st
from url_decider import url_decider


# ---------------------------------------------------------------------------
# Page config — must be the very first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Field Hockey Scout",
    page_icon="🏑",
    layout="centered",
)


# ---------------------------------------------------------------------------
# Davidson College color palette + custom CSS
# Davidson official colors: Black #000000, Red #CC0000, White #FFFFFF
# ---------------------------------------------------------------------------
DAVIDSON_BLACK = "#000000"
DAVIDSON_RED   = "#CC0000"
DAVIDSON_WHITE = "#FFFFFF"
DAVIDSON_GRAY  = "#1A1A1A"   # slightly lighter black for card backgrounds
DAVIDSON_LIGHT = "#F5F5F5"   # near-white for input backgrounds

st.markdown(f"""
<style>
/* ── Global reset ─────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {{
    background-color: {DAVIDSON_BLACK};
    color: {DAVIDSON_WHITE};
    font-family: 'Georgia', serif;
}}

/* Remove Streamlit's default white page background */
[data-testid="stApp"] {{
    background-color: {DAVIDSON_BLACK};
}}

/* ── Header banner ────────────────────────────────────────── */
.scout-header {{
    background-color: {DAVIDSON_BLACK};
    border-bottom: 4px solid {DAVIDSON_RED};
    padding: 2rem 0 1.2rem 0;
    text-align: center;
    margin-bottom: 0.5rem;
}}

.scout-title {{
    font-size: 2.4rem;
    font-weight: 700;
    color: {DAVIDSON_WHITE};
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin: 0;
    line-height: 1.15;
}}

.scout-title span {{
    color: {DAVIDSON_RED};
}}

/* ── Welcome card ─────────────────────────────────────────── */
.welcome-card {{
    background-color: {DAVIDSON_GRAY};
    border-left: 5px solid {DAVIDSON_RED};   /* signature: red clipboard margin line */
    border-radius: 4px;
    padding: 1.1rem 1.4rem;
    margin: 1.2rem 0 1rem 0;
    font-size: 0.97rem;
    line-height: 1.65;
    color: {DAVIDSON_WHITE};
}}

.sidearm-warning {{
    font-weight: 700;
    color: {DAVIDSON_RED};
}}

/* ── Instructions block ───────────────────────────────────── */
.instructions-block {{
    background-color: {DAVIDSON_GRAY};
    border-left: 5px solid {DAVIDSON_RED};
    border-radius: 4px;
    padding: 1rem 1.4rem;
    margin: 0.5rem 0 1.2rem 0;
}}

.instructions-title {{
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {DAVIDSON_RED};
    margin-bottom: 0.5rem;
}}

.instructions-block ol {{
    margin: 0;
    padding-left: 1.3rem;
    color: {DAVIDSON_WHITE};
    font-size: 0.95rem;
    line-height: 1.7;
}}

.instructions-block ol li {{
    margin-bottom: 0.3rem;
}}

/* ── Submit note ──────────────────────────────────────────── */
.submit-note {{
    font-size: 0.92rem;
    color: #CCCCCC;
    margin: 0.4rem 0 1.4rem 0;
    font-style: italic;
}}

/* ── Form labels ──────────────────────────────────────────── */
label, .stTextInput label, .stForm label {{
    color: {DAVIDSON_WHITE} !important;
    font-weight: 600 !important;
    font-size: 0.93rem !important;
    letter-spacing: 0.03em !important;
}}

/* ── Text inputs ──────────────────────────────────────────── */
.stTextInput input {{
    background-color: {DAVIDSON_LIGHT} !important;
    color: {DAVIDSON_BLACK} !important;
    border: 2px solid #444 !important;
    border-radius: 3px !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 0.75rem !important;
}}

.stTextInput input:focus {{
    border-color: {DAVIDSON_RED} !important;
    box-shadow: 0 0 0 2px rgba(204,0,0,0.25) !important;
    outline: none !important;
}}

/* ── Submit button ────────────────────────────────────────── */
.stFormSubmitButton button, .stButton button {{
    background-color: {DAVIDSON_RED} !important;
    color: {DAVIDSON_WHITE} !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 3px !important;
    padding: 0.6rem 2.2rem !important;
    cursor: pointer !important;
    transition: background-color 0.15s ease !important;
    width: 100% !important;
}}

.stFormSubmitButton button:hover, .stButton button:hover {{
    background-color: #A30000 !important;
}}

/* ── Error / success messages ─────────────────────────────── */
.stAlert {{
    border-radius: 3px !important;
    font-size: 0.93rem !important;
}}

/* ── Hide Streamlit branding ──────────────────────────────── */
#MainMenu, footer, header {{
    visibility: hidden;
}}

/* ── Divider ──────────────────────────────────────────────── */
hr {{
    border: none;
    border-top: 1px solid #333;
    margin: 1.2rem 0;
}}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def is_valid_url(url: str) -> bool:
    """
    Return True if `url` starts with http:// or https:// and has a domain.

    We don't do a full RFC-3986 parse — we just check the two things a
    user is most likely to get wrong: missing the protocol prefix and
    pasting a bare domain like 'bucknellbison.com'.

    Args:
        url: The string the user typed into the URL field.

    Returns:
        True if the URL looks valid enough to attempt a scrape.
    """
    pattern = re.compile(
        r'^https?://'           # must start with http:// or https://
        r'[a-zA-Z0-9.-]+'      # domain name
        r'(\.[a-zA-Z]{2,})'    # top-level domain (.com, .edu, etc.)
        r'(/.*)?$'              # optional path
    )
    return bool(pattern.match(url.strip()))


def is_valid_team_name(name: str) -> bool:
    """
    Return True if `name` is non-empty and contains at least one
    alphabetic character (i.e. is an actual word/acronym, not spaces
    or punctuation only).

    Args:
        name: The string the user typed into the team name field.

    Returns:
        True if the name passes the minimum check.
    """
    stripped = name.strip()
    # Must have at least one letter and be at least 2 characters long
    return len(stripped) >= 2 and bool(re.search(r'[a-zA-Z]', stripped))


# ---------------------------------------------------------------------------
# Placeholder for the scrape + report function
# ---------------------------------------------------------------------------

def run_scraper(url: str, scouted_team:str):
    """
    PLACEHOLDER — replace the body of this function with your real scraper.

    This is where you plug in:
        from boxscore_scraper import scrape_and_report
        ...

    For now it returns a dummy .txt string so the download button works
    and you can test the UI end-to-end before wiring in the real scraper.

    Args:
        url:       The schedule/boxscore URL the user submitted.
        scouted_team: The team acronym/name the user submitted.

    Returns:
        A string that will be written to the downloadable .txt file.
    """
    # ── INSERT YOUR SCRAPER CALL HERE ──────────────────────────────────────
    # Example:
    #   from boxscore_scraper import scrape_and_report
    #   result = scrape_and_report(url=url, scouted_team=team_name)
    #   return result
    # ───────────────────────────────────────────────────────────────────────
    placeholder_report=url_decider(url=url,scouted_team=scouted_team)
    # # Dummy output so the UI is testable right now
    # placeholder_report = (
    #     f"FIELD HOCKEY SCOUT REPORT\n"
    #     f"{'=' * 50}\n"
    #     f"  Scouted Team : {scouted_team}\n"
    #     f"  Source URL   : {url}\n"
    #     f"{'=' * 50}\n\n"
    #     f"[PLACEHOLDER] Real scraper output will appear here.\n"
    #     f"Replace the body of run_scraper() in scout_app.py\n"
    #     f"with your actual scrape_and_report() call.\n"
    # )
    return placeholder_report


# ---------------------------------------------------------------------------
# UI — Header
# ---------------------------------------------------------------------------

st.markdown("""
<div class="scout-header">
    <p class="scout-title">🏑 Field Hockey Scout<br><span>Web Scraper</span></p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# UI — Welcome message
# ---------------------------------------------------------------------------

st.markdown("""
<div class="welcome-card">
    Welcome to the <strong>Field Hockey Scout Web Scraper</strong>. To use the scraper,
    please follow the instructions directly below.
    <br><br>
    <span class="sidearm-warning">⚠ This web scraper only works with college field hockey
    websites built by SideArm Sports.</span>
    If your target website was not built by SideArm Sports, please scout manually.
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# UI — Instructions
# ---------------------------------------------------------------------------

st.markdown("""
<div class="instructions-block">
    <div class="instructions-title">Instructions</div>
    <ol>
        <li>
            Load in the URL of the team's <strong>schedule page</strong> you wish to scout
            (e.g. <em>https://bucknellbison.com/sports/field-hockey/schedule/2025</em>).
        </li>
        <li>
            Type the <strong>acronym or name</strong> of the team you wish to scout.
            This can be found by opening any game boxscore on the team's website and
            checking how the team refers to itself in the play-by-play section
            (e.g. <em>Bucknell</em>, <em>VCU</em>, <em>American</em>).
        </li>
    </ol>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<p class="submit-note">Once both fields are filled out, hit <strong>Run Scout</strong> '
    'and you will receive a <strong>.txt file</strong> of your scouting report to download.</p>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# UI — Form
# ---------------------------------------------------------------------------

with st.form(key="scout_form", clear_on_submit=False):

    url_input = st.text_input(
        label="Schedule URL",
        placeholder="https://bucknellbison.com/sports/field-hockey/schedule/2025",
        help="Paste the full URL of the team's schedule page (must start with http:// or https://).",
    )

    team_input = st.text_input(
        label="Team Acronym / Name",
        placeholder="e.g.  Bucknell  or  VCU  or  American",
        help="Type exactly how the team appears in the play-by-play section of their boxscore.",
    )

    submitted = st.form_submit_button("🏑  Run Scout")


# ---------------------------------------------------------------------------
# Form submission logic — validation then scraper call
# ---------------------------------------------------------------------------

if submitted:

    # ── Validate URL ───────────────────────────────────────────────────────
    if not url_input or not url_input.strip():
        st.error("⚠ Please enter a schedule URL before submitting.")

    elif not is_valid_url(url_input):
        st.error(
            "⚠ The URL you entered doesn't look valid. "
            "Make sure it starts with **http://** or **https://** "
            "and points to a full web address (e.g. https://bucknellbison.com/...)."
        )

    # ── Validate team name ─────────────────────────────────────────────────
    elif not team_input or not team_input.strip():
        st.error("⚠ Please enter the team acronym or name before submitting.")

    elif not is_valid_team_name(team_input):
        st.error(
            "⚠ The team name must contain at least two characters and include letters. "
            "Enter the acronym or name as it appears in the play-by-play "
            "(e.g. **Bucknell**, **VCU**, **American**)."
        )

    # ── All checks passed — run the scraper ───────────────────────────────
    else:
        with st.spinner(f"Scouting **{team_input.strip()}** — this may take a minute..."):
            try:
                report_text = run_scraper(
                    url=url_input.strip(),
                    scouted_team=team_input.strip()
                )
                st.success(f"✅ Scout complete for **{team_input.strip()}**! Download your report below.")

                # Offer the report as a downloadable .txt file
                st.download_button(
                    label="⬇ Download Scout Report (.txt)",
                    data=report_text,
                    file_name=f"scout_{team_input.strip().replace(' ', '_').lower()}.txt",
                    mime="text/plain",
                )

            except Exception as e:
                # Surface a friendly error rather than crashing the whole app
                st.error(
                    f"⚠ The scraper ran into a problem: **{e}**\n\n"
                    "Double-check that the URL is a valid SideArm Sports schedule page "
                    "and that the team name matches what appears in the play-by-play."
                )
