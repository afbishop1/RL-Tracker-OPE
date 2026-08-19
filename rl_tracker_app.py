import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from collections import defaultdict
import pytz
# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="RL Match Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ============================================================
# CUSTOM CSS - ROCKET LEAGUE THEME
# ============================================================
st.markdown("""
<style>
    :root {
        --rl-orange: #FF6B00;
        --rl-blue: #1E90FF;
        --rl-dark: #0A0E27;
        --rl-darker: #050913;
        --rl-light: #E8EAED;
    }
    body {
        background-color: var(--rl-darker);
        color: var(--rl-light);
    }
    .stApp {
        background-color: var(--rl-darker);
    }
    [data-testid="stMainBlockContainer"] {
        background-color: var(--rl-darker);
        padding: 2rem;
    }
    .match-card {
        background: linear-gradient(135deg, #1a1f3a 0%, #0f1428 100%);
        border: 2px solid var(--rl-orange);
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 4px 15px rgba(255, 107, 0, 0.3);
    }
    .team-card {
        background: linear-gradient(135deg, #1a1f3a 0%, #0f1428 100%);
        border-left: 4px solid var(--rl-orange);
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
    }
    .team-card.team-2 {
        border-left-color: var(--rl-blue);
    }
    .stat-box {
        background: rgba(30, 144, 255, 0.1);
        border: 1px solid var(--rl-blue);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        text-align: center;
    }
    .stat-box.orange {
        background: rgba(255, 107, 0, 0.1);
        border: 1px solid var(--rl-orange);
    }
    h1, h2, h3 {
        color: var(--rl-light);
    }
    .title-main {
        font-size: 3em;
        font-weight: bold;
        background: linear-gradient(90deg, var(--rl-orange) 0%, var(--rl-blue) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px;
    }
    .series-header {
        background: linear-gradient(135deg, var(--rl-orange) 0%, #FF8C00 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-size: 1.8em;
        font-weight: bold;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(255, 107, 0, 0.4);
    }
    .stButton>button {
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1.6em !important;
        padding: 20px 40px !important;
        transition: transform 0.2s;
        background: linear-gradient(90deg, var(--rl-orange) 0%, #FF8C00 100%) !important;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(255, 107, 0, 0.6) !important;
    }
    [data-testid="stRadio"] label:nth-child(1) input {
        accent-color: #FF6B00 !important;
    }
    [data-testid="stRadio"] label:nth-child(2) input,
    [data-testid="stRadio"] label:nth-child(3) input {
        accent-color: #1E90FF !important;
    }
    .tab-content {
        background-color: var(--rl-darker);
    }
    .metric-box {
        background: linear-gradient(
            135deg,
            rgba(30, 144, 255, 0.1),
            rgba(255, 107, 0, 0.1)
        );
        border: 1px solid var(--rl-orange);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        text-align: center;
    }
    [data-testid="stMetricValue"] {
        color: var(--rl-orange);
    }
    /* ========================================================
       LEFT ALIGNED PLAYER STATS TABLES
       ======================================================== */
    .rl-table-wrapper {
        width: 100%;
        overflow-x: auto;
        margin-bottom: 20px;
    }
    .rl-stats-table {
        width: 100%;
        border-collapse: collapse;
        background: #0f1428;
        color: #E8EAED;
        font-size: 16px;
        text-align: left !important;
    }
    .rl-stats-table th {
        background: #1a1f3a;
        color: #E8EAED;
        font-weight: bold;
        padding: 12px 15px;
        border: 1px solid #303653;
        text-align: left !important;
        white-space: nowrap;
    }
    .rl-stats-table td {
        padding: 12px 15px;
        border: 1px solid #303653;
        text-align: left !important;
        vertical-align: middle;
        white-space: nowrap;
    }
    .rl-stats-table tr:hover {
        background: rgba(30, 144, 255, 0.08);
    }
    .rl-stats-table th *,
    .rl-stats-table td * {
        text-align: left !important;
    }
    /* ========================================================
       PREMIUM TAB STYLING
       ======================================================== */
    [data-testid="stTabs"] {
        gap: 0;
    }
    [data-testid="stTabs"] [role="tablist"] {
        background: linear-gradient(90deg, rgba(10, 14, 39, 0.8) 0%, rgba(5, 9, 19, 0.8) 100%);
        border-bottom: 3px solid transparent;
        border-image: linear-gradient(90deg, var(--rl-orange) 0%, var(--rl-blue) 100%) 1;
        padding: 10px 0;
        gap: 5px;
    }
    [data-testid="stTabs"] [role="tab"] {
        background: rgba(30, 50, 80, 0.4);
        border: 2px solid rgba(255, 107, 0, 0.3);
        border-radius: 12px 12px 0 0;
        padding: 12px 16px !important;
        margin: 0 4px;
        color: #E8EAED !important;
        font-weight: 600;
        font-size: 0.95em;
        transition: all 0.3s ease;
        white-space: nowrap;
    }
    [data-testid="stTabs"] [role="tab"]:hover {
        background: linear-gradient(135deg, rgba(255, 107, 0, 0.2) 0%, rgba(30, 144, 255, 0.2) 100%);
        border-color: var(--rl-orange);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 107, 0, 0.2);
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, var(--rl-orange) 0%, #FF8C00 100%);
        border: 2px solid var(--rl-orange);
        color: white !important;
        box-shadow: 0 6px 20px rgba(255, 107, 0, 0.4);
        transform: translateY(-2px);
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"]:hover {
        box-shadow: 0 8px 25px rgba(255, 107, 0, 0.5);
    }
    /* ========================================================
       MOBILE OPTIMIZATION
       ======================================================== */
    @media (max-width: 768px) {
        [data-testid="stTabs"] [role="tab"] {
            padding: 10px 10px !important;
            font-size: 0.85em;
            margin: 0 2px;
        }
        [data-testid="stTabs"] [role="tablist"] {
            overflow-x: auto;
            padding: 8px 0;
        }
        [data-testid="stMainBlockContainer"] {
            padding: 1rem;
        }
    }
    @media (max-width: 480px) {
        [data-testid="stTabs"] [role="tab"] {
            padding: 8px 8px !important;
            font-size: 0.75em;
            margin: 0 1px;
            border-radius: 8px;
        }
        [data-testid="stTabs"] [role="tablist"] {
            gap: 2px;
        }
        [data-testid="stMainBlockContainer"] {
            padding: 1rem 0.75rem;
        }
    }
    /* ========================================================
       HEADER & BRANDING
       ======================================================== */
    .ope-header {
        background: linear-gradient(135deg, rgba(255, 107, 0, 0.15) 0%, rgba(30, 144, 255, 0.15) 100%);
        border: 2px solid;
        border-image: linear-gradient(90deg, var(--rl-orange) 0%, var(--rl-blue) 100%) 1;
        border-radius: 16px;
        padding: 40px 20px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(255, 107, 0, 0.2);
    }
    .ope-logo {
        font-size: 4em;
        margin-bottom: 15px;
        animation: bounce 2s infinite;
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    .ope-title {
        background: linear-gradient(90deg, var(--rl-orange) 0%, var(--rl-blue) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5em !important;
        font-weight: 900 !important;
        margin: 10px 0 !important;
        letter-spacing: 2px;
    }
    .ope-subtitle {
        color: #E8EAED;
        font-size: 1.2em;
        margin: 10px 0 0 0 !important;
        font-weight: 500;
        letter-spacing: 1px;
    }
    /* ========================================================
       GRADIENT DIVIDERS
       ======================================================== */
    [data-testid="stHorizontalBlock"] hr {
        border: none;
        height: 3px;
        background: linear-gradient(90deg, var(--rl-orange) 0%, var(--rl-blue) 50%, var(--rl-orange) 100%);
        margin: 20px 0;
        border-radius: 2px;
    }
    /* ========================================================
       FORM STYLING
       ======================================================== */
    [data-testid="stSelectbox"] > div {
        background: linear-gradient(135deg, rgba(30, 50, 80, 0.6) 0%, rgba(15, 20, 40, 0.6) 100%);
        border: 2px solid var(--rl-orange);
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    [data-testid="stSelectbox"] > div:hover {
        border-color: var(--rl-orange);
        box-shadow: 0 4px 12px rgba(255, 107, 0, 0.4);
    }
    [data-testid="stNumberInput"] > div {
        background: linear-gradient(135deg, rgba(30, 50, 80, 0.6) 0%, rgba(15, 20, 40, 0.6) 100%);
        border: 2px solid rgba(100, 100, 100, 0.4);
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    [data-testid="stNumberInput"] > div:hover {
        box-shadow: 0 4px 12px rgba(100, 100, 100, 0.2);
    }
    .form-group {
        background: rgba(15, 20, 40, 0.4);
        border-left: 4px solid var(--rl-orange);
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
    }
    .form-group.blue {
        border-left-color: var(--rl-blue);
    }
    /* ========================================================
       STAT CARDS
       ======================================================== */
    .stat-card {
        background: linear-gradient(135deg, rgba(30, 50, 80, 0.5) 0%, rgba(15, 20, 40, 0.5) 100%);
        border: 2px solid;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(255, 107, 0, 0.3);
    }
    .stat-card.orange {
        border-color: var(--rl-orange);
    }
    .stat-card.orange:hover {
        background: linear-gradient(135deg, rgba(255, 107, 0, 0.2) 0%, rgba(255, 140, 0, 0.1) 100%);
    }
    .stat-card.blue {
        border-color: var(--rl-blue);
    }
    .stat-card.blue:hover {
        background: linear-gradient(135deg, rgba(30, 144, 255, 0.2) 0%, rgba(65, 105, 225, 0.1) 100%);
    }
    .stat-card-title {
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .stat-card-value {
        font-size: 2.5em;
        font-weight: 900;
        background: linear-gradient(90deg, var(--rl-orange) 0%, var(--rl-blue) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 10px 0;
    }
    .stat-card-label {
        font-size: 0.9em;
        color: #A0A0A8;
    }
    /* ========================================================
       SERIES PROGRESS BAR
       ======================================================== */
    .series-progress {
        display: flex;
        gap: 10px;
        justify-content: center;
        margin: 20px 0;
        flex-wrap: wrap;
    }
    .series-game {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.2em;
        border: 3px solid;
        transition: all 0.3s ease;
    }
    .series-game.pending {
        background: rgba(100, 100, 120, 0.3);
        border-color: rgba(200, 200, 200, 0.3);
        color: #808080;
    }
    .series-game.team1 {
        background: linear-gradient(135deg, var(--rl-orange) 0%, #FF8C00 100%);
        border-color: var(--rl-orange);
        color: white;
        box-shadow: 0 4px 15px rgba(255, 107, 0, 0.4);
    }
    .series-game.team2 {
        background: linear-gradient(135deg, var(--rl-blue) 0%, #4169E1 100%);
        border-color: var(--rl-blue);
        color: white;
        box-shadow: 0 4px 15px rgba(30, 144, 255, 0.4);
    }
    .series-game:hover {
        transform: scale(1.1);
    }
    /* ========================================================
       SUCCESS ANIMATION
       ======================================================== */
    @keyframes successPulse {
        0% {
            transform: scale(1);
            opacity: 1;
        }
        50% {
            transform: scale(1.05);
            opacity: 0.8;
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }
    .success-animation {
        animation: successPulse 0.6s ease-in-out;
    }
    .stSuccess {
        animation: successPulse 0.6s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DYNAMIC INPUT COLORING - TEAM 1 ORANGE, TEAM 2 BLUE
# ============================================================
st.markdown("""
<script>
function colorTeamInputs() {
    const gameExpanders = document.querySelectorAll('[data-testid="stExpander"]');
    gameExpanders.forEach((expander) => {
        const text = expander.textContent;
        if (text.includes('Game')) {
            const columns = expander.querySelectorAll('[data-testid="stColumn"]');
            if (columns.length >= 2) {
                // Team 1 = first column = orange
                const team1Col = columns[0];
                const team1Inputs = team1Col.querySelectorAll('[data-testid="stNumberInput"] > div');
                team1Inputs.forEach(input => {
                    input.style.borderColor = '#FF6B00';
                    input.style.boxShadow = '0 0 0 0';
                    input.addEventListener('mouseenter', () => {
                        input.style.boxShadow = '0 4px 12px rgba(255, 107, 0, 0.4)';
                    });
                    input.addEventListener('mouseleave', () => {
                        input.style.boxShadow = '0 0 0 0';
                    });
                });
                
                // Team 2 = second column = blue
                const team2Col = columns[1];
                const team2Inputs = team2Col.querySelectorAll('[data-testid="stNumberInput"] > div');
                team2Inputs.forEach(input => {
                    input.style.borderColor = '#1E90FF';
                    input.style.boxShadow = '0 0 0 0';
                    input.addEventListener('mouseenter', () => {
                        input.style.boxShadow = '0 4px 12px rgba(30, 144, 255, 0.4)';
                    });
                    input.addEventListener('mouseleave', () => {
                        input.style.boxShadow = '0 0 0 0';
                    });
                });
            }
        }
    });
}

// Run on load and watch for changes
setTimeout(colorTeamInputs, 100);
window.addEventListener('load', colorTeamInputs);
const observer = new MutationObserver(() => {
    setTimeout(colorTeamInputs, 50);
});
observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)
def left_aligned_table(df):
    """
    Displays a pandas DataFrame as an HTML table with
    every header and cell left-aligned.
    """
    if df.empty:
        st.info("No data available")
        return
    html = df.to_html(
        index=False,
        escape=False,
        classes="rl-stats-table",
        border=0
    )
    st.markdown(
        f"""
        <div class="rl-table-wrapper">
            {html}
        </div>
        """,
        unsafe_allow_html=True
    )
# ============================================================
# DATABASE SETUP
# ============================================================
def init_db():
    conn = sqlite3.connect("rl_matches.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS matches
        (
            id INTEGER PRIMARY KEY,
            series_number INTEGER,
            match_number INTEGER,
            best_of INTEGER,
            timestamp TEXT,
            team1_players TEXT,
            team2_players TEXT,
            team1_score INTEGER,
            team2_score INTEGER,
            winner INTEGER
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS player_stats
        (
            id INTEGER PRIMARY KEY,
            match_id INTEGER,
            player_name TEXT,
            team INTEGER,
            score INTEGER,
            goals INTEGER,
            assists INTEGER,
            saves INTEGER,
            shots INTEGER,
            excuse_used INTEGER,
            FOREIGN KEY(match_id) REFERENCES matches(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS activity_log
        (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            user_name TEXT,
            action TEXT
        )
    """)
    # Auto migration
    try:
        c.execute("PRAGMA table_info(player_stats)")
        columns = [row[1] for row in c.fetchall()]
        if "shots" not in columns:
            c.execute(
                "ALTER TABLE player_stats ADD COLUMN shots INTEGER DEFAULT 0"
            )
        if "excuse_used" not in columns:
            c.execute(
                "ALTER TABLE player_stats ADD COLUMN excuse_used INTEGER DEFAULT 0"
            )
        conn.commit()
    except Exception as e:
        print(f"Migration error: {e}")
    conn.commit()
    return conn

# ============================================================
# AUTO-RENUMBER SERIES (QUICK FIX FOR DELETED SERIES)
# ============================================================
def renumber_series():
    """Renumber series sequentially if gaps exist from deletions"""
    conn = sqlite3.connect("rl_matches.db")
    c = conn.cursor()
    
    c.execute("""
        SELECT DISTINCT series_number
        FROM matches
        ORDER BY series_number
    """)
    old_series = [row[0] for row in c.fetchall()]
    
    if not old_series:
        conn.close()
        return
    
    # Create mapping from old to new
    old_to_new = {old_num: new_num for new_num, old_num in enumerate(old_series, 1)}
    
    # Update if there are gaps
    if old_to_new != {i: i for i in range(1, len(old_series) + 1)}:
        for old_num, new_num in old_to_new.items():
            if old_num != new_num:
                c.execute("""
                    UPDATE matches
                    SET series_number = ?
                    WHERE series_number = ?
                """, (new_num, old_num))
        conn.commit()
    
    conn.close()
conn = init_db()
renumber_series()
c = conn.cursor()
# ============================================================
# PLAYERS
# ============================================================
PLAYERS = [
    "Killmesmallz",
    "See Me No Mor",
    "Bon Qwee Qwee",
    "CrabLegz19",
    "GunzMcgee73",
    "BucciXman",
    "SirLagz54"
]
# ============================================================
# TITLE
# ============================================================
st.markdown("""
<style>
    .rl-title {
        font-size: clamp(1.5em, 7vw, 2.5em);
        font-weight: bold;
        background: linear-gradient(90deg, #FF6B00 0%, #1E90FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px;
        margin-top: 5px;
        text-align: center;
        white-space: normal;
        line-height: 1.2;
    }
</style>
<div class="rl-title">RL MATCH TRACKER</div>
""", unsafe_allow_html=True)
st.markdown("""
<div style="
    text-align: center;
    font-size: clamp(1.4em, 6vw, 1.8em);
    font-weight: bold;
    background: linear-gradient(90deg, #FF6B00 0%, #FF8C00 50%, #1E90FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 10px 0 15px 0;
    letter-spacing: 1px;
    line-height: 1.3;
">
🎮 OPE GAMING CLAN 🎮
</div>
""", unsafe_allow_html=True)
st.divider()
# ============================================================
# SESSION STATE
# ============================================================
if "confirm_submit" not in st.session_state:
    st.session_state.confirm_submit = False
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False
if "delete_series_num" not in st.session_state:
    st.session_state.delete_series_num = None
if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0
# ============================================================
# PERFORMANCE RATING CALCULATION
# ============================================================
def calculate_performance_rating(avg_goals, avg_assists, avg_saves, avg_shots, 
                                  max_goals, max_assists, max_saves, max_shots):
    """
    Calculate performance rating (0-10) based on normalized stats.
    Weights: Goals 40%, Assists 30%, Saves 20%, Shots 10%
    """
    # Normalize each stat to 0-10 scale
    norm_goals = (avg_goals / max_goals * 10) if max_goals > 0 else 0
    norm_assists = (avg_assists / max_assists * 10) if max_assists > 0 else 0
    norm_saves = (avg_saves / max_saves * 10) if max_saves > 0 else 0
    norm_shots = (avg_shots / max_shots * 10) if max_shots > 0 else 0
    
    # Calculate weighted rating
    rating = (norm_goals * 0.40) + (norm_assists * 0.30) + (norm_saves * 0.20) + (norm_shots * 0.10)
    
    return round(rating, 2)

def display_stat_card(player_name, value, emoji, card_type="orange"):
    """
    Display a record as a colorful stat card instead of a boring message.
    """
    color_class = "orange" if card_type == "orange" else "blue"
    st.markdown(f"""
    <div class="stat-card {color_class}">
        <div class="stat-card-title">{emoji}</div>
        <div class="stat-card-value">{value}</div>
        <div class="stat-card-label">{player_name}</div>
    </div>
    """, unsafe_allow_html=True)

def display_leaderboard(rankings_data):
    """
    Display rankings as a table.
    """
    if not rankings_data:
        st.info("No data available")
        return
    
    df_rankings = pd.DataFrame(rankings_data)
    left_aligned_table(df_rankings)

# ============================================================
# HEADER
# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "🎯 Log Match",
        "📈 History", 
        "🏆 Stats",
        "👥 Matchups",
        "📊 Analysis",
        "🏅 Records"
    ]
)
# ============================================================
# TAB 1 - LOG MATCH
# ============================================================
with tab1:
    if st.button(
        "🔄 Refresh Data",
        use_container_width=True,
        key="refresh_tab1"
    ):
        st.rerun()

    # Button coloring
    st.markdown("""
    <script>
        function colorButtons() {
            let buttons = document.querySelectorAll('button');
            buttons.forEach(btn => {
                if (btn.textContent.includes('Refresh Data')) {
                    btn.style.background =
                        'linear-gradient(90deg, #1E90FF 0%, #4169E1 100%)';
                    btn.style.color = 'white';
                    btn.style.border = 'none';
                    btn.style.borderRadius = '8px';
                    btn.style.fontWeight = 'bold';
                    btn.style.fontSize = '1.6em';
                    btn.style.padding = '20px 40px';
                }
            });
        }
        colorButtons();
        setTimeout(colorButtons, 100);
        setTimeout(colorButtons, 300);
        setTimeout(colorButtons, 600);
        setTimeout(colorButtons, 1000);
        const observer =
            new MutationObserver(colorButtons);
        observer.observe(
            document.body,
            {
                childList: true,
                subtree: true
            }
        );
    </script>
    """, unsafe_allow_html=True)
    st.divider()
    # --------------------------------------------------------
    # FORMAT
    # --------------------------------------------------------
    st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>⚙️ Match Settings</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🏁 Series Format")
        st.caption("How many games to win the series?")
        best_of = st.radio(
            "Choose format",
            ["Best of 3", "Best of 5"],
            horizontal=True,
            label_visibility="collapsed",
            key="best_of_select"
        )
        bo_num = 3 if best_of == "Best of 3" else 5
        max_games = bo_num
    with col2:
        st.markdown("#### 👥 Match Type")
        st.caption("How many players per team?")
        match_type = st.radio(
            "Choose type",
            ["1v1", "2v2", "3v3"],
            horizontal=True,
            label_visibility="collapsed",
            key="match_type_select"
        )
        num_players = int(match_type[0])
    # --------------------------------------------------------
    # CURRENT SERIES
    # --------------------------------------------------------
    c.execute("""
        SELECT series_number, match_number, best_of
        FROM matches
        ORDER BY series_number DESC, match_number DESC
        LIMIT 1
    """)
    last_match = c.fetchone()
    if last_match:
        last_series, last_match_num, last_bo = last_match
        c.execute("""
            SELECT COUNT(*)
            FROM matches
            WHERE series_number = ?
            AND winner IS NOT NULL
        """, (last_series,))
        wins_in_series = c.fetchone()[0]
        wins_needed = 2 if last_bo == 3 else 3
        if wins_in_series >= wins_needed:
            current_series = last_series + 1
        else:
            current_series = last_series
    else:
        current_series = 1
    st.markdown(
        f'<div class="series-header">Series {current_series} - {best_of}</div>',
        unsafe_allow_html=True
    )
    
    # Show series progress
    c.execute("""
        SELECT winner, COUNT(*) as count
        FROM matches
        WHERE series_number = ? AND winner IS NOT NULL
        GROUP BY winner
    """, (current_series,))
    
    wins = {1: 0, 2: 0}
    for winner, count in c.fetchall():
        wins[winner] = count
    
    wins_needed = 2 if best_of == "Best of 3" else 3
    
    # Build progress visualization
    progress_html = '<div class="series-progress">'
    max_games = 5 if best_of == "Best of 5" else 3
    
    for game_num in range(1, max_games + 1):
        if game_num <= wins[1]:
            progress_html += f'<div class="series-game team1">🟠 {game_num}</div>'
        elif game_num <= wins[1] + wins[2]:
            progress_html += f'<div class="series-game team2">🔵 {game_num}</div>'
        else:
            progress_html += f'<div class="series-game pending">{game_num}</div>'
    
    progress_html += '</div>'
    st.markdown(progress_html, unsafe_allow_html=True)
    
    # Show series status
    if wins[1] >= wins_needed:
        st.markdown('<div style="text-align: center; padding: 10px; background: linear-gradient(135deg, rgba(255, 107, 0, 0.2) 0%, rgba(255, 140, 0, 0.1) 100%); border-radius: 8px; border-left: 4px solid #FF6B00; margin: 10px 0;"><strong>🏆 Series Won by Team 1!</strong></div>', unsafe_allow_html=True)
    elif wins[2] >= wins_needed:
        st.markdown('<div style="text-align: center; padding: 10px; background: linear-gradient(135deg, rgba(30, 144, 255, 0.2) 0%, rgba(65, 105, 225, 0.1) 100%); border-radius: 8px; border-left: 4px solid #1E90FF; margin: 10px 0;"><strong>🏆 Series Won by Team 2!</strong></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align: center; padding: 10px; background: rgba(100, 100, 120, 0.2); border-radius: 8px; margin: 10px 0;"><strong>Series: {wins[1]} - {wins[2]} (First to {wins_needed} wins)</strong></div>', unsafe_allow_html=True)
    
    st.markdown('<hr style="border: none; height: 2px; background: linear-gradient(90deg, #FF6B00 0%, #1E90FF 50%, #FF6B00 100%); margin: 20px 0;">', unsafe_allow_html=True)
    
    # --------------------------------------------------------
    # TEAM SESSION STATE
    # --------------------------------------------------------
    if "series_team1" not in st.session_state:
        st.session_state.series_team1 = [
            "Choose Player"
        ] * num_players
    if "series_team2" not in st.session_state:
        st.session_state.series_team2 = [
            "Choose Player"
        ] * num_players
    if len(st.session_state.series_team1) != num_players:
        st.session_state.reset_counter += 1
        st.session_state.series_team1 = [
            "Choose Player"
        ] * num_players
        st.session_state.series_team2 = [
            "Choose Player"
        ] * num_players
    elif len(st.session_state.series_team2) != num_players:
        st.session_state.reset_counter += 1
        st.session_state.series_team1 = [
            "Choose Player"
        ] * num_players
        st.session_state.series_team2 = [
            "Choose Player"
        ] * num_players
    # --------------------------------------------------------
    # SELECT TEAMS
    # --------------------------------------------------------
    st.markdown("## Step 1: Select Your Teams")
    col1, col2 = st.columns(2)
    player_options = ["Choose Player"] + PLAYERS
    with col1:
        st.markdown(
            """
            <div style="
                text-align:center;
                font-size:1.3em;
                color:#FF6B00;
                font-weight:bold;
                margin-bottom:15px;
            ">
            TEAM 1
            </div>
            """,
            unsafe_allow_html=True
        )
        for i in range(num_players):
            try:
                current_index = player_options.index(
                    st.session_state.series_team1[i]
                )
            except (ValueError, IndexError):
                current_index = 0
            st.session_state.series_team1[i] = st.selectbox(
                f"Player {i+1}",
                player_options,
                index=current_index,
                label_visibility="collapsed",
                key=f"team1_p{i}_r{st.session_state.reset_counter}"
            )
    with col2:
        st.markdown(
            """
            <div style="
                text-align:center;
                font-size:1.3em;
                color:#1E90FF;
                font-weight:bold;
                margin-bottom:15px;
            ">
            TEAM 2
            </div>
            """,
            unsafe_allow_html=True
        )
        for i in range(num_players):
            try:
                current_index = player_options.index(
                    st.session_state.series_team2[i]
                )
            except (ValueError, IndexError):
                current_index = 0
            st.session_state.series_team2[i] = st.selectbox(
                f"Player {i+1}",
                player_options,
                index=current_index,
                label_visibility="collapsed",
                key=f"team2_p{i}_r{st.session_state.reset_counter}"
            )
    st.divider()
    # --------------------------------------------------------
    # GAME STATS
    # --------------------------------------------------------
    st.markdown("## Step 2: Add Stats for Each Game")
    series_games = []
    for game_num in range(1, max_games + 1):
        with st.expander(
            f"Game {game_num}",
            expanded=(game_num == 1)
        ):
            col1, col2 = st.columns(2)
            # TEAM 1
            with col1:
                st.markdown(
                    """
                    <div style="
                        text-align:center;
                        font-size:1.2em;
                        color:#FF6B00;
                        font-weight:bold;
                        margin-bottom:10px;
                    ">
                    TEAM 1
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                team1_stats = []
                for i in range(num_players):
                    player_name = st.session_state.series_team1[i]
                    st.markdown(f"**{player_name}**")
                    stat_col1, stat_col2, stat_col3 = st.columns(3)
                    with stat_col1:
                        score = st.number_input(
                            "Score",
                            min_value=0,
                            key=f"g{game_num}_t1_s{i}_r{st.session_state.reset_counter}"
                        )
                        goals = st.number_input(
                            "Goals",
                            min_value=0,
                            key=f"g{game_num}_t1_g{i}_r{st.session_state.reset_counter}"
                        )
                    with stat_col2:
                        assists = st.number_input(
                            "Assists",
                            min_value=0,
                            key=f"g{game_num}_t1_a{i}_r{st.session_state.reset_counter}"
                        )
                        saves = st.number_input(
                            "Saves",
                            min_value=0,
                            key=f"g{game_num}_t1_sv{i}_r{st.session_state.reset_counter}"
                        )
                    with stat_col3:
                        shots = st.number_input(
                            "Shots",
                            min_value=0,
                            key=f"g{game_num}_t1_sh{i}_r{st.session_state.reset_counter}"
                        )
                    excuse_used = st.radio(
                        "Excuse Used?",
                        ["No", "Yes"],
                        horizontal=True,
                        key=f"g{game_num}_t1_ex{i}_r{st.session_state.reset_counter}"
                    )
                    excuse_val = 1 if excuse_used == "Yes" else 0
                    team1_stats.append({
                        "player": player_name,
                        "score": score,
                        "goals": goals,
                        "assists": assists,
                        "saves": saves,
                        "shots": shots,
                        "excuse_used": excuse_val
                    })
                    st.markdown("---")
            # TEAM 2
            with col2:
                st.markdown(
                    """
                    <div style="
                        text-align:center;
                        font-size:1.2em;
                        color:#1E90FF;
                        font-weight:bold;
                        margin-bottom:10px;
                    ">
                    TEAM 2
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                team2_stats = []
                for i in range(num_players):
                    player_name = st.session_state.series_team2[i]
                    st.markdown(f"**{player_name}**")
                    stat_col1, stat_col2, stat_col3 = st.columns(3)
                    with stat_col1:
                        score = st.number_input(
                            "Score",
                            min_value=0,
                            key=f"g{game_num}_t2_s{i}_r{st.session_state.reset_counter}"
                        )
                        goals = st.number_input(
                            "Goals",
                            min_value=0,
                            key=f"g{game_num}_t2_g{i}_r{st.session_state.reset_counter}"
                        )
                    with stat_col2:
                        assists = st.number_input(
                            "Assists",
                            min_value=0,
                            key=f"g{game_num}_t2_a{i}_r{st.session_state.reset_counter}"
                        )
                        saves = st.number_input(
                            "Saves",
                            min_value=0,
                            key=f"g{game_num}_t2_sv{i}_r{st.session_state.reset_counter}"
                        )
                    with stat_col3:
                        shots = st.number_input(
                            "Shots",
                            min_value=0,
                            key=f"g{game_num}_t2_sh{i}_r{st.session_state.reset_counter}"
                        )
                    excuse_used = st.radio(
                        "Excuse Used?",
                        ["No", "Yes"],
                        horizontal=True,
                        key=f"g{game_num}_t2_ex{i}_r{st.session_state.reset_counter}"
                    )
                    excuse_val = 1 if excuse_used == "Yes" else 0
                    team2_stats.append({
                        "player": player_name,
                        "score": score,
                        "goals": goals,
                        "assists": assists,
                        "saves": saves,
                        "shots": shots,
                        "excuse_used": excuse_val
                    })
                    st.markdown("---")
            # WINNER
            team1_display = " + ".join(
                st.session_state.series_team1
            )
            team2_display = " + ".join(
                st.session_state.series_team2
            )
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                st.markdown("**Who won this game?**")
            with col_w2:
                winner = st.radio(
                    "Select winner",
                    [team1_display, team2_display],
                    horizontal=True,
                    key=f"g{game_num}_winner_r{st.session_state.reset_counter}",
                    label_visibility="collapsed"
                )
            winner_num = 1 if winner == team1_display else 2
            series_games.append({
                "game_num": game_num,
                "team1_players": st.session_state.series_team1.copy(),
                "team2_players": st.session_state.series_team2.copy(),
                "team1_stats": team1_stats,
                "team2_stats": team2_stats,
                "winner": winner_num
            })
    st.divider()
    # --------------------------------------------------------
    # SUBMIT
    # --------------------------------------------------------
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        submit_clicked = st.button(
            "🎮 LOG SERIES 🎮",
            key="submit_series",
            use_container_width=True
        )
    if submit_clicked:
        st.session_state.confirm_submit = True
    if st.session_state.get("confirm_submit", False):
        st.divider()
        st.markdown("### 👤 Who is entering this game?")
        confirming_user = st.selectbox(
            "Select your name",
            PLAYERS,
            key="confirm_user_selectbox"
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "✅ Confirm",
                use_container_width=True,
                key="confirm_btn"
            ):
                all_valid = True
                error_msg = ""
                # Check players
                if (
                    "Choose Player" in st.session_state.series_team1
                    or
                    "Choose Player" in st.session_state.series_team2
                ):
                    all_valid = False
                    error_msg = (
                        "Please select all players before logging the series!"
                    )
                # Check duplicates
                for game in series_games:
                    if not all_valid:
                        break
                    all_players_in_game = (
                        game["team1_players"]
                        +
                        game["team2_players"]
                    )
                    if len(all_players_in_game) != len(
                        set(all_players_in_game)
                    ):
                        all_valid = False
                        error_msg = (
                            f"Game {game['game_num']}: "
                            "Each player can only be on one team!"
                        )
                        break
                if not all_valid:
                    st.error(error_msg)
                else:
                    # Determine wins needed and filter out games after series is won
                    wins_needed = 2 if bo_num == 3 else 3
                    games_to_log = []
                    t1_wins = 0
                    t2_wins = 0
                    
                    for game in series_games:
                        # Add game only if series isn't already won
                        if t1_wins < wins_needed and t2_wins < wins_needed:
                            games_to_log.append(game)
                            if game["winner"] == 1:
                                t1_wins += 1
                            else:
                                t2_wins += 1
                    
                    # Warn if user entered games that won't count
                    if len(games_to_log) < len(series_games):
                        st.warning(
                            f"⚠️ Series completed after {len(games_to_log)} games. "
                            f"Game(s) {len(games_to_log)+1}-{len(series_games)} will not be logged."
                        )
                    
                    for game in games_to_log:
                        t1_total = sum(
                            p["score"]
                            for p in game["team1_stats"]
                        )
                        t2_total = sum(
                            p["score"]
                            for p in game["team2_stats"]
                        )
                        c.execute("""
                            INSERT INTO matches
                            (
                                series_number,
                                match_number,
                                best_of,
                                timestamp,
                                team1_players,
                                team2_players,
                                team1_score,
                                team2_score,
                                winner
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            current_series,
                            game["game_num"],
                            bo_num,
                            datetime.now().isoformat(),
                            ",".join(game["team1_players"]),
                            ",".join(game["team2_players"]),
                            t1_total,
                            t2_total,
                            game["winner"]
                        ))
                        match_id = c.lastrowid
                        # Team 1 stats
                        for stat in game["team1_stats"]:
                            c.execute("""
                                INSERT INTO player_stats
                                (
                                    match_id,
                                    player_name,
                                    team,
                                    score,
                                    goals,
                                    assists,
                                    saves,
                                    shots,
                                    excuse_used
                                )
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                match_id,
                                stat["player"],
                                1,
                                int(stat["score"]),
                                int(stat["goals"]),
                                int(stat["assists"]),
                                int(stat["saves"]),
                                int(stat["shots"]),
                                int(stat["excuse_used"])
                            ))
                        # Team 2 stats
                        for stat in game["team2_stats"]:
                            c.execute("""
                                INSERT INTO player_stats
                                (
                                    match_id,
                                    player_name,
                                    team,
                                    score,
                                    goals,
                                    assists,
                                    saves,
                                    shots,
                                    excuse_used
                                )
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                match_id,
                                stat["player"],
                                2,
                                int(stat["score"]),
                                int(stat["goals"]),
                                int(stat["assists"]),
                                int(stat["saves"]),
                                int(stat["shots"]),
                                int(stat["excuse_used"])
                            ))
                    conn.commit()
                    # Activity log
                    c.execute("""
                        INSERT INTO activity_log
                        (
                            timestamp,
                            user_name,
                            action
                        )
                        VALUES (?, ?, ?)
                    """, (
                        datetime.now().isoformat(),
                        confirming_user,
                        "entered a game"
                    ))
                    conn.commit()
                    st.session_state.reset_counter += 1
                    st.session_state.series_team1 = [
                        "Choose Player"
                    ] * num_players
                    st.session_state.series_team2 = [
                        "Choose Player"
                    ] * num_players
                    st.session_state.confirm_submit = False
                    st.balloons()
                    st.success(
                        f"✅ Series {current_series} Logged by "
                        f"{confirming_user}! 🎉"
                    )
                    st.rerun()
        with col2:
            if st.button(
                "❌ Cancel",
                use_container_width=True,
                key="cancel_btn"
            ):
                st.session_state.confirm_submit = False
                st.rerun()
# ============================================================
# TAB 2 - SERIES HISTORY
# ============================================================
with tab2:
    if st.button(
        "🔄 Refresh Data",
        use_container_width=True,
        key="refresh_tab2"
    ):
        st.rerun()
    st.divider()
    c.execute("""
        SELECT series_number, best_of, match_number
        FROM matches
        GROUP BY series_number
        ORDER BY series_number DESC
    """)
    series_list = c.fetchall()
    if not series_list:
        st.info("📭 No matches logged yet")
    else:
        series_by_type = {
            "1v1": [],
            "2v2": [],
            "3v3": []
        }
        for series_num, bo, last_match in series_list:
            c.execute("""
                SELECT team1_players
                FROM matches
                WHERE series_number = ?
                ORDER BY match_number
                LIMIT 1
            """, (series_num,))
            first_match = c.fetchone()
            if first_match:
                t1_players = first_match[0].split(",")
                num_players_in_series = len(t1_players)
                if num_players_in_series == 1:
                    match_type = "1v1"
                elif num_players_in_series == 2:
                    match_type = "2v2"
                else:
                    match_type = "3v3"
                series_by_type[match_type].append(
                    (series_num, bo, last_match)
                )
        
        st.markdown("## 📈 Series History")
        
        for match_type in ["1v1", "2v2", "3v3"]:
            with st.expander(f"{match_type} Series", expanded=True):
                if not series_by_type[match_type]:
                    st.info(f"📭 No {match_type} series yet")
                else:
                    for series_num, bo, last_match in series_by_type[
                        match_type
                    ]:
                        c.execute("""
                            SELECT team1_players, team2_players
                            FROM matches
                            WHERE series_number = ?
                            ORDER BY match_number
                            LIMIT 1
                        """, (series_num,))
                        first_match = c.fetchone()
                        if first_match:
                            t1_players = first_match[0]
                            t2_players = first_match[1]
                            player_info = (
                                f"({t1_players} vs {t2_players})"
                            )
                            t1_list = t1_players.split(",")
                            t2_list = t2_players.split(",")
                        else:
                            player_info = ""
                            t1_list = []
                            t2_list = []
                        c.execute("""
                            SELECT winner, COUNT(*)
                            FROM matches
                            WHERE series_number = ?
                            GROUP BY winner
                        """, (series_num,))
                        wins_data = c.fetchall()
                        t1_wins = 0
                        t2_wins = 0
                        for winner, count in wins_data:
                            if winner == 1:
                                t1_wins = count
                            elif winner == 2:
                                t2_wins = count
                        if t1_wins > t2_wins:
                            series_winner = " + ".join(t1_list)
                            series_record = (
                                f"{t1_wins}-{t2_wins}"
                            )
                        elif t2_wins > t1_wins:
                            series_winner = " + ".join(t2_list)
                            series_record = (
                                f"{t2_wins}-{t1_wins}"
                            )
                        else:
                            series_winner = "Tied"
                            series_record = (
                                f"{t1_wins}-{t2_wins}"
                            )
                        col1, col2 = st.columns([0.95, 0.05])
                        with col1:
                            expander = st.expander(
                                f"📊 Series {series_num} - "
                                f"{series_winner} Won "
                                f"{series_record} "
                                f"{player_info}",
                                expanded=False
                            )
                        with col2:
                            st.write("")
                            if st.button(
                                "🗑️",
                                key=f"delete_series_{series_num}",
                                help="Delete this series",
                                use_container_width=True
                            ):
                                st.session_state.confirm_delete = True
                                st.session_state.delete_series_num = (
                                    series_num
                                )
                        if (
                            st.session_state.get(
                                "confirm_delete",
                                False
                            )
                            and
                            st.session_state.get(
                                "delete_series_num"
                            ) == series_num
                        ):
                            st.divider()
                            st.markdown(
                                f"### 👤 Who is deleting Series {series_num}?"
                            )
                            deleting_user = st.selectbox(
                                "Select your name",
                                PLAYERS,
                                key=f"delete_user_{series_num}"
                            )
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(
                                    "✅ Confirm Delete",
                                    use_container_width=True,
                                    key=f"confirm_delete_{series_num}"
                                ):
                                    c.execute("""
                                        DELETE FROM player_stats
                                        WHERE match_id IN
                                        (
                                            SELECT id
                                            FROM matches
                                            WHERE series_number = ?
                                        )
                                    """, (series_num,))
                                    c.execute("""
                                        DELETE FROM matches
                                        WHERE series_number = ?
                                    """, (series_num,))
                                    c.execute("""
                                        INSERT INTO activity_log
                                        (
                                            timestamp,
                                            user_name,
                                            action
                                        )
                                        VALUES (?, ?, ?)
                                    """, (
                                        datetime.now().isoformat(),
                                        deleting_user,
                                        "deleted a game"
                                    ))
                                    conn.commit()
                                    st.session_state.confirm_delete = False
                                    st.session_state.delete_series_num = None
                                    st.success(
                                        f"Series {series_num} deleted "
                                    f"by {deleting_user}!"
                                )
                                st.rerun()
                        with col2:
                            if st.button(
                                "❌ Cancel",
                                use_container_width=True,
                                key=f"cancel_delete_{series_num}"
                            ):
                                st.session_state.confirm_delete = False
                                st.session_state.delete_series_num = None
                                st.rerun()
                    with expander:
                        c.execute("""
                            SELECT *
                            FROM matches
                            WHERE series_number = ?
                            ORDER BY match_number
                        """, (series_num,))
                        matches = c.fetchall()
                        for match in matches:
                            (
                                match_id,
                                sn,
                                mn,
                                b,
                                ts,
                                t1p,
                                t2p,
                                t1s,
                                t2s,
                                winner
                            ) = match
                            t1_players = t1p.split(",")
                            t2_players = t2p.split(",")
                            if winner == 1:
                                winner_text = (
                                    " + ".join(t1_players)
                                    + " Won"
                                )
                            elif winner == 2:
                                winner_text = (
                                    " + ".join(t2_players)
                                    + " Won"
                                )
                            else:
                                winner_text = "Pending"
                            c.execute("""
                                SELECT SUM(goals)
                                FROM player_stats
                                WHERE match_id = ?
                                AND team = 1
                            """, (match_id,))
                            t1_goals = c.fetchone()[0] or 0
                            c.execute("""
                                SELECT SUM(goals)
                                FROM player_stats
                                WHERE match_id = ?
                                AND team = 2
                            """, (match_id,))
                            t2_goals = c.fetchone()[0] or 0
                            st.markdown(
                                f"**Match {mn}: {winner_text} "
                                f"({t1_goals} - {t2_goals})**"
                            )
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(
                                    """
                                    <div style="
                                        text-align:center;
                                        font-size:1.1em;
                                        color:#FF6B00;
                                        font-weight:bold;
                                    ">
                                    TEAM 1
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                c.execute("""
                                    SELECT
                                        player_name,
                                        score,
                                        goals,
                                        assists,
                                        saves,
                                        shots
                                    FROM player_stats
                                    WHERE match_id = ?
                                    AND team = 1
                                """, (match_id,))
                                for row in c.fetchall():
                                    st.markdown(
                                        f"**{row[0]}** · "
                                        f"Score: {row[1]} "
                                        f"Goals: {row[2]} "
                                        f"Assists: {row[3]} "
                                        f"Saves: {row[4]} "
                                        f"Shots: {row[5]}"
                                    )
                            with col2:
                                st.markdown(
                                    """
                                    <div style="
                                        text-align:center;
                                        font-size:1.1em;
                                        color:#1E90FF;
                                        font-weight:bold;
                                    ">
                                    TEAM 2
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                c.execute("""
                                    SELECT
                                        player_name,
                                        score,
                                        goals,
                                        assists,
                                        saves,
                                        shots
                                    FROM player_stats
                                    WHERE match_id = ?
                                    AND team = 2
                                """, (match_id,))
                                for row in c.fetchall():
                                    st.markdown(
                                        f"**{row[0]}** · "
                                        f"Score: {row[1]} "
                                        f"Goals: {row[2]} "
                                        f"Assists: {row[3]} "
                                        f"Saves: {row[4]} "
                                        f"Shots: {row[5]}"
                                    )
                            st.divider()
                        st.markdown("### Series Totals")
                        c.execute("""
                            SELECT
                                player_name,
                                SUM(score),
                                SUM(goals),
                                SUM(assists),
                                SUM(saves),
                                SUM(shots)
                            FROM player_stats
                            WHERE match_id IN
                            (
                                SELECT id
                                FROM matches
                                WHERE series_number = ?
                            )
                            GROUP BY player_name
                            ORDER BY SUM(score) DESC
                        """, (series_num,))
                        for row in c.fetchall():
                            st.markdown(
                                f"**{row[0]}** · "
                                f"Score: {row[1]} "
                                f"Goals: {row[2]} "
                                f"Assists: {row[3]} "
                                f"Saves: {row[4]} "
                                f"Shots: {row[5]}"
                            )
            st.divider()
    # Activity Log
    st.markdown("## 📋 Activity Log")
    c.execute("""
        SELECT timestamp, user_name, action
        FROM activity_log
        ORDER BY timestamp DESC
        LIMIT 50
    """)
    logs = c.fetchall()
    if not logs:
        st.info("📭 No activity yet")
    else:
        eastern = pytz.timezone("US/Eastern")
        for timestamp, user_name, action in logs:
            ts = datetime.fromisoformat(timestamp)
            ts_utc = (
                pytz.UTC.localize(ts)
                if ts.tzinfo is None
                else ts
            )
            ts_eastern = ts_utc.astimezone(eastern)
            ts_str = ts_eastern.strftime(
                "%m/%d %I:%M %p"
            )
            st.markdown(
                f"**{user_name}** {action} · {ts_str}"
            )
    st.divider()
# ============================================================
# TAB 3 - PLAYER STATS
# ============================================================
with tab3:
    if st.button(
        "🔄 Refresh Data",
        use_container_width=True,
        key="refresh_tab3"
    ):
        st.rerun()
    st.divider()
    c.execute("""
        SELECT DISTINCT player_name
        FROM player_stats
        ORDER BY player_name
    """)
    all_players_list = [
        row[0]
        for row in c.fetchall()
    ]
    if not all_players_list:
        st.info("📭 No player data yet")
    else:
        # Get overall stats for each player
        overall_stats = {}
        for player in all_players_list:
            c.execute("""
                SELECT COUNT(*)
                FROM matches
                WHERE
                    (
                        team1_players LIKE ?
                        AND winner = 1
                    )
                    OR
                    (
                        team2_players LIKE ?
                        AND winner = 2
                    )
            """, (
                f"%{player}%",
                f"%{player}%"
            ))
            wins = c.fetchone()[0]
            c.execute("""
                SELECT COUNT(*)
                FROM matches
                WHERE
                    (
                        team1_players LIKE ?
                        AND winner = 2
                    )
                    OR
                    (
                        team2_players LIKE ?
                        AND winner = 1
                    )
            """, (
                f"%{player}%",
                f"%{player}%"
            ))
            losses = c.fetchone()[0]
            games = wins + losses
            win_pct = (
                (wins / games) * 100
                if games > 0
                else 0
            )
            c.execute("""
                SELECT
                    SUM(score),
                    SUM(goals),
                    SUM(assists),
                    SUM(saves),
                    SUM(shots),
                    SUM(excuse_used)
                FROM player_stats
                WHERE player_name = ?
            """, (player,))
            (
                score,
                goals,
                assists,
                saves,
                shots,
                excuses
            ) = c.fetchone()
            score = score or 0
            goals = goals or 0
            assists = assists or 0
            saves = saves or 0
            shots = shots or 0
            excuses = excuses or 0
            overall_stats[player] = {
                "wins": wins,
                "losses": losses,
                "games": games,
                "win_pct": f"{win_pct:.1f}%",
                "score": score,
                "goals": goals,
                "assists": assists,
                "saves": saves,
                "shots": shots,
                "excuses": excuses,
                "avg_score": score / games if games else 0,
                "avg_goals": goals / games if games else 0,
                "avg_assists": assists / games if games else 0,
                "avg_saves": saves / games if games else 0,
                "avg_shots": shots / games if games else 0,
                "avg_excuses": excuses / games if games else 0
            }
        # ====================================================
        # OVERALL CAREER STATS TABLE
        # ====================================================
        st.markdown("## 🎮 Overall Career Stats")
        wins_data = []
        for player in all_players_list:
            stat = overall_stats[player]
            wins_data.append({
                "🎮 Player": player,
                "🏆 Wins": stat["wins"],
                "💔 Losses": stat["losses"],
                "📊 Games": stat["games"],
                "📈 Win %": stat["win_pct"]
            })
        df_wins = pd.DataFrame(wins_data)
        df_wins = df_wins.sort_values(
            "🏆 Wins",
            ascending=False
        )
        left_aligned_table(df_wins)
        st.divider()
        # ====================================================
        # CAREER TOTALS
        # ====================================================
        st.markdown("### Career Totals (All Matches)")
        totals_data = []
        for player in sorted(
            all_players_list,
            key=lambda p: overall_stats[p]["wins"],
            reverse=True
        ):
            stat = overall_stats[player]
            totals_data.append({
                "🎮 Player": player,
                "🎯 Score": stat["score"],
                "⚽ Goals": stat["goals"],
                "🎁 Assists": stat["assists"],
                "🛡️ Saves": stat["saves"],
                "🔫 Shots": stat["shots"],
                "🤥 Excuses": stat["excuses"]
            })
        df_totals = pd.DataFrame(totals_data)
        left_aligned_table(df_totals)
        st.divider()
        # ====================================================
        # PER GAME AVERAGES
        # ====================================================
        st.markdown("### Per-Game Averages (All Matches)")
        avg_data = []
        for player in sorted(
            all_players_list,
            key=lambda p: overall_stats[p]["wins"],
            reverse=True
        ):
            stat = overall_stats[player]
            avg_data.append({
                "🎮 Player": player,
                "📍 Avg Score": f"{stat['avg_score']:.1f}",
                "⚽ Avg Goals": f"{stat['avg_goals']:.2f}",
                "🎁 Avg Assists": f"{stat['avg_assists']:.2f}",
                "🛡️ Avg Saves": f"{stat['avg_saves']:.2f}",
                "🔫 Avg Shots": f"{stat['avg_shots']:.2f}",
                "🤥 Avg Excuses": f"{stat['avg_excuses']:.2f}"
            })
        df_avg = pd.DataFrame(avg_data)
        left_aligned_table(df_avg)
        st.divider()
        # ====================================================
        # MATCH TYPE CAREER TOTALS
        # ====================================================
        st.markdown("## Match Type Career Totals")
        
        for match_type in ["1v1", "2v2", "3v3"]:
            with st.expander(f"{match_type} Career Totals", expanded=False):
                type_totals = []
                for player in sorted(
                    all_players_list,
                    key=lambda p: overall_stats[p]["wins"],
                    reverse=True
                ):
                    # Get stats for this match type
                    c.execute("""
                        SELECT
                            SUM(score),
                            SUM(goals),
                            SUM(assists),
                            SUM(saves),
                            SUM(shots),
                            SUM(excuse_used),
                            COUNT(DISTINCT match_id)
                        FROM player_stats
                        WHERE player_name = ?
                        AND match_id IN (
                            SELECT id FROM matches
                            WHERE 
                                (LENGTH(team1_players) - LENGTH(REPLACE(team1_players, ',', '')))
                                = ?
                        )
                    """, (
                        player,
                        1 if match_type == "2v2" else (2 if match_type == "3v3" else 0)
                    ))
                    result = c.fetchone()
                    if result and result[6]:  # Has games in this match type
                        score, goals, assists, saves, shots, excuses, games = result
                        type_totals.append({
                            "🎮 Player": player,
                            "🎯 Score": score or 0,
                            "⚽ Goals": goals or 0,
                            "🎁 Assists": assists or 0,
                            "🛡️ Saves": saves or 0,
                            "🔫 Shots": shots or 0,
                            "🤥 Excuses": excuses or 0,
                            "📊 Games": games
                        })
                
                if type_totals:
                    df_type = pd.DataFrame(type_totals)
                    left_aligned_table(df_type)
                else:
                    st.info(f"No {match_type} games yet")
        
        st.divider()
        # ====================================================
        # MATCH TYPE PER-GAME AVERAGES
        # ====================================================
        st.markdown("## Match Type Per-Game Averages")
        
        for match_type in ["1v1", "2v2", "3v3"]:
            with st.expander(f"{match_type} Per-Game Averages", expanded=False):
                type_avgs = []
                for player in sorted(
                    all_players_list,
                    key=lambda p: overall_stats[p]["wins"],
                    reverse=True
                ):
                    # Get stats for this match type
                    c.execute("""
                        SELECT
                            SUM(score),
                            SUM(goals),
                            SUM(assists),
                            SUM(saves),
                            SUM(shots),
                            SUM(excuse_used),
                            COUNT(DISTINCT match_id)
                        FROM player_stats
                        WHERE player_name = ?
                        AND match_id IN (
                            SELECT id FROM matches
                            WHERE 
                                (LENGTH(team1_players) - LENGTH(REPLACE(team1_players, ',', '')))
                                = ?
                        )
                    """, (
                        player,
                        1 if match_type == "2v2" else (2 if match_type == "3v3" else 0)
                    ))
                    result = c.fetchone()
                    if result and result[6]:  # Has games in this match type
                        score, goals, assists, saves, shots, excuses, games = result
                        type_avgs.append({
                            "🎮 Player": player,
                            "📍 Avg Score": f"{(score or 0) / games:.1f}",
                            "⚽ Avg Goals": f"{(goals or 0) / games:.2f}",
                            "🎁 Avg Assists": f"{(assists or 0) / games:.2f}",
                            "🛡️ Avg Saves": f"{(saves or 0) / games:.2f}",
                            "🔫 Avg Shots": f"{(shots or 0) / games:.2f}",
                            "🤥 Avg Excuses": f"{(excuses or 0) / games:.2f}"
                        })
                
                if type_avgs:
                    df_type_avg = pd.DataFrame(type_avgs)
                    left_aligned_table(df_type_avg)
                else:
                    st.info(f"No {match_type} games yet")
        
        st.divider()
# ============================================================
# TAB 4 - TEAMS
# ============================================================
with tab4:
    if st.button(
        "🔄 Refresh Data",
        use_container_width=True,
        key="refresh_tab4"
    ):
        st.rerun()

    # ====================================================
    # BEST TEAMS
    # ====================================================
    st.markdown("## 🤝 Best Teams")
    
    c.execute("""
        SELECT id, team1_players, team2_players, winner
        FROM matches
    """)
    all_match_data = c.fetchall()
    
    if all_match_data:
        partnerships = defaultdict(lambda: {"wins": 0, "losses": 0})
        
        for match_id, t1, t2, winner in all_match_data:
            t1_list = t1.split(",")
            t2_list = t2.split(",")
            
            # Only count 2v2 and 3v3 (skip 1v1)
            if len(t1_list) == 1:
                continue
            
            t1_team = tuple(sorted(t1_list))
            t2_team = tuple(sorted(t2_list))
            
            if winner == 1:
                partnerships[t1_team]["wins"] += 1
            else:
                partnerships[t1_team]["losses"] += 1
            
            if winner == 2:
                partnerships[t2_team]["wins"] += 1
            else:
                partnerships[t2_team]["losses"] += 1
        
        if partnerships:
            partnership_list = []
            for team, record in partnerships.items():
                total = record["wins"] + record["losses"]
                win_pct = (record["wins"] / total * 100) if total > 0 else 0
                team_display = " + ".join(team)
                partnership_list.append({
                    "🏆 Rank": 0,
                    "🤝 Team": team_display,
                    "🏅 Wins": record["wins"],
                    "💔 Losses": record["losses"],
                    "📊 Games": total,
                    "📈 Win %": f"{win_pct:.1f}%"
                })
            
            partnership_list.sort(key=lambda x: x["🏅 Wins"], reverse=True)
            for idx, p in enumerate(partnership_list, 1):
                p["🏆 Rank"] = idx
            
            df_partnerships = pd.DataFrame(partnership_list)
            left_aligned_table(df_partnerships)
        else:
            st.info("No 2v2 or 3v3 teams yet")
    
    st.divider()
    # ====================================================
    # 1V1 HEAD-TO-HEAD
    # ====================================================
    st.markdown("## 1v1 Head-to-Head")
    
    c.execute("""
        SELECT id, team1_players, team2_players, winner
        FROM matches
        WHERE 
            (LENGTH(team1_players) - LENGTH(REPLACE(team1_players, ',', ''))) = 0
    """)
    one_v_one_matches = c.fetchall()
    
    if not one_v_one_matches:
        st.info("📭 No 1v1 matches yet")
    else:
        # Build head-to-head records
        h2h_records = defaultdict(lambda: defaultdict(lambda: {"wins": 0, "losses": 0}))
        
        for match_id, t1, t2, winner in one_v_one_matches:
            p1 = t1.strip()
            p2 = t2.strip()
            
            if winner == 1:
                h2h_records[p1][p2]["wins"] += 1
                h2h_records[p2][p1]["losses"] += 1
            elif winner == 2:
                h2h_records[p2][p1]["wins"] += 1
                h2h_records[p1][p2]["losses"] += 1
        
        # Display for each player
        c.execute("""
            SELECT DISTINCT player_name
            FROM player_stats
            ORDER BY player_name
        """)
        all_players_with_stats = [row[0] for row in c.fetchall()]
        
        for player in all_players_with_stats:
            if player not in h2h_records or not h2h_records[player]:
                continue
                
            with st.expander(f"🎮 {player}", expanded=False):
                h2h_data = []
                for opponent, record in h2h_records[player].items():
                    total = record["wins"] + record["losses"]
                    win_pct = (record["wins"] / total * 100) if total > 0 else 0
                    h2h_data.append({
                        "🎮 Opponent": opponent,
                        "🏆 Wins": record["wins"],
                        "💔 Losses": record["losses"],
                        "📊 Total": total,
                        "📈 Win %": f"{win_pct:.1f}%"
                    })
                
                h2h_data.sort(key=lambda x: x["🏆 Wins"], reverse=True)
                df_h2h = pd.DataFrame(h2h_data)
                left_aligned_table(df_h2h)
    
    st.divider()
    c.execute("""
        SELECT
            id,
            team1_players,
            team2_players,
            winner
        FROM matches
    """)
    all_matches = c.fetchall()
    if not all_matches:
        st.info("📭 No team data yet")
    else:
        partnerships_by_type = {
            "2v2": defaultdict(
                lambda: {
                    "wins": 0,
                    "losses": 0
                }
            ),
            "3v3": defaultdict(
                lambda: {
                    "wins": 0,
                    "losses": 0
                }
            )
        }
        matchups_by_type = {
            "2v2": defaultdict(
                lambda: defaultdict(
                    lambda: {
                        "wins": 0,
                        "losses": 0
                    }
                )
            ),
            "3v3": defaultdict(
                lambda: defaultdict(
                    lambda: {
                        "wins": 0,
                        "losses": 0
                    }
                )
            )
        }
        for match_id, t1, t2, winner in all_matches:
            t1_list = t1.split(",")
            t2_list = t2.split(",")
            if len(t1_list) == 1:
                match_type = "1v1"
            elif len(t1_list) == 2:
                match_type = "2v2"
            else:
                match_type = "3v3"
            if match_type == "1v1":
                continue
            partnerships = partnerships_by_type[
                match_type
            ]
            matchups = matchups_by_type[
                match_type
            ]
            if match_type == "2v2":
                t1_pairs = []
                for i in range(len(t1_list)):
                    for j in range(i + 1, len(t1_list)):
                        pair = tuple(
                            sorted(
                                [
                                    t1_list[i],
                                    t1_list[j]
                                ]
                            )
                        )
                        t1_pairs.append(pair)
                        if winner == 1:
                            partnerships[pair]["wins"] += 1
                        else:
                            partnerships[pair]["losses"] += 1
                t2_pairs = []
                for i in range(len(t2_list)):
                    for j in range(i + 1, len(t2_list)):
                        pair = tuple(
                            sorted(
                                [
                                    t2_list[i],
                                    t2_list[j]
                                ]
                            )
                        )
                        t2_pairs.append(pair)
                        if winner == 2:
                            partnerships[pair]["wins"] += 1
                        else:
                            partnerships[pair]["losses"] += 1
            else:
                t1_team = tuple(
                    sorted(t1_list)
                )
                t2_team = tuple(
                    sorted(t2_list)
                )
                if winner == 1:
                    partnerships[
                        t1_team
                    ]["wins"] += 1
                else:
                    partnerships[
                        t1_team
                    ]["losses"] += 1
                if winner == 2:
                    partnerships[
                        t2_team
                    ]["wins"] += 1
                else:
                    partnerships[
                        t2_team
                    ]["losses"] += 1
                t1_pairs = [t1_team]
                t2_pairs = [t2_team]
            # Matchups
            for t1_pair in t1_pairs:
                for t2_pair in t2_pairs:
                    if winner == 1:
                        matchups[
                            t1_pair
                        ][
                            t2_pair
                        ]["wins"] += 1
                        matchups[
                            t2_pair
                        ][
                            t1_pair
                        ]["losses"] += 1
                    else:
                        matchups[
                            t1_pair
                        ][
                            t2_pair
                        ]["losses"] += 1
                        matchups[
                            t2_pair
                        ][
                            t1_pair
                        ]["wins"] += 1
        # Display teams
        for match_type in ["2v2", "3v3"]:
            partnerships = partnerships_by_type[
                match_type
            ]
            matchups = matchups_by_type[
                match_type
            ]
            st.markdown(
                f"## {match_type} Teams"
            )
            if not partnerships:
                st.info(
                    f"📭 No {match_type} team data yet"
                )
            else:
                part_data = []
                for partnership_tuple, record in partnerships.items():
                    total = (
                        record["wins"]
                        +
                        record["losses"]
                    )
                    win_pct = (
                        record["wins"]
                        / total
                        * 100
                        if total > 0
                        else 0
                    )
                    display = " + ".join(
                        partnership_tuple
                    )
                    part_data.append({
                        "partnership": partnership_tuple,
                        "display": display,
                        "wins": record["wins"],
                        "losses": record["losses"],
                        "total": total,
                        "win_pct": win_pct
                    })
                part_data.sort(
                    key=lambda x: x["wins"],
                    reverse=True
                )
                for partnership_info in part_data:
                    part_tuple = (
                        partnership_info["partnership"]
                    )
                    total = (
                        partnership_info["total"]
                    )
                    win_pct = (
                        partnership_info["win_pct"]
                    )
                    with st.expander(
                        f"🤝 "
                        f"{partnership_info['display']} · "
                        f"{partnership_info['wins']}-"
                        f"{partnership_info['losses']} "
                        f"({win_pct:.1f}%)",
                        expanded=False
                    ):
                        st.markdown(
                            f"**Overall: "
                            f"{partnership_info['wins']} Wins · "
                            f"{partnership_info['losses']} Losses · "
                            f"{win_pct:.1f}% Win Rate**"
                        )
                        st.divider()
                        st.markdown(
                            "**Head-to-Head vs Other Teams:**"
                        )
                        matchup_records = []
                        if part_tuple in matchups:
                            for opponent_tuple, record in matchups[
                                part_tuple
                            ].items():
                                h2h_total = (
                                    record["wins"]
                                    +
                                    record["losses"]
                                )
                                h2h_pct = (
                                    record["wins"]
                                    / h2h_total
                                    * 100
                                    if h2h_total > 0
                                    else 0
                                )
                                opponent_display = (
                                    " + ".join(
                                        opponent_tuple
                                    )
                                )
                                matchup_records.append({
                                    "opponent": opponent_display,
                                    "wins": record["wins"],
                                    "losses": record["losses"],
                                    "total": h2h_total,
                                    "pct": h2h_pct
                                })
                        if matchup_records:
                            matchup_records.sort(
                                key=lambda x: x["wins"],
                                reverse=True
                            )
                            for matchup in matchup_records:
                                st.markdown(
                                    f"vs **{matchup['opponent']}** · "
                                    f"{matchup['wins']}-"
                                    f"{matchup['losses']} "
                                    f"({matchup['pct']:.1f}%)"
                                )
                        else:
                            st.markdown(
                                "*No matchup data yet*"
                            )
                st.divider()
# ============================================================
# TAB 5 - LEADERBOARD
# ============================================================
with tab5:
    if st.button(
        "🔄 Refresh Data",
        use_container_width=True,
        key="refresh_tab5"
    ):
        st.rerun()
    st.divider()
    
    # ====================================================
    # PLAYER COMPARISON
    # ====================================================
    st.markdown("## 🎮 Player Comparison")
    
    c.execute("""
        SELECT DISTINCT player_name
        FROM player_stats
        ORDER BY player_name
    """)
    all_comparison_players = [row[0] for row in c.fetchall()]
    
    if all_comparison_players:
        comparison_options = ["Choose Player"] + all_comparison_players
        
        col1, col2 = st.columns(2)
        with col1:
            player1 = st.selectbox("Player 1", comparison_options, key="comp_p1")
        with col2:
            player2 = st.selectbox("Player 2", comparison_options, key="comp_p2")
        
        if player1 != "Choose Player" and player2 != "Choose Player" and player1 != player2:
            # Build comparison table
            stats_list = []
            stats_names = ["Games", "Wins", "Losses", "Win %", "Avg Goals", "Avg Assists", "Avg Saves", "Avg Shots"]
            
            for stat_name in stats_names:
                row = {"📊 Stat": stat_name}
                for player in [player1, player2]:
                    if stat_name == "Games":
                        c.execute("""
                            SELECT COUNT(DISTINCT match_id) FROM player_stats WHERE player_name = ?
                        """, (player,))
                        games_val = c.fetchone()[0]
                        row[player] = games_val
                    elif stat_name == "Wins":
                        c.execute("""
                            SELECT COUNT(*)
                            FROM matches
                            WHERE
                                (team1_players LIKE ? AND winner = 1)
                                OR (team2_players LIKE ? AND winner = 2)
                        """, (f"%{player}%", f"%{player}%"))
                        row[player] = c.fetchone()[0]
                    elif stat_name == "Losses":
                        c.execute("""
                            SELECT COUNT(*)
                            FROM matches
                            WHERE
                                (team1_players LIKE ? AND winner = 2)
                                OR (team2_players LIKE ? AND winner = 1)
                        """, (f"%{player}%", f"%{player}%"))
                        row[player] = c.fetchone()[0]
                    elif stat_name == "Win %":
                        c.execute("""
                            SELECT COUNT(*)
                            FROM matches
                            WHERE
                                (team1_players LIKE ? AND winner = 1)
                                OR (team2_players LIKE ? AND winner = 2)
                        """, (f"%{player}%", f"%{player}%"))
                        wins = c.fetchone()[0]
                        c.execute("""
                            SELECT COUNT(DISTINCT match_id) FROM player_stats WHERE player_name = ?
                        """, (player,))
                        total = c.fetchone()[0]
                        pct = (wins / total * 100) if total > 0 else 0
                        row[player] = f"{pct:.1f}%"
                    elif stat_name == "Avg Goals":
                        c.execute("""
                            SELECT SUM(goals), COUNT(DISTINCT match_id)
                            FROM player_stats WHERE player_name = ?
                        """, (player,))
                        goals, games = c.fetchone()
                        avg = (goals or 0) / games if games > 0 else 0
                        row[player] = f"{avg:.2f}"
                    elif stat_name == "Avg Assists":
                        c.execute("""
                            SELECT SUM(assists), COUNT(DISTINCT match_id)
                            FROM player_stats WHERE player_name = ?
                        """, (player,))
                        assists, games = c.fetchone()
                        avg = (assists or 0) / games if games > 0 else 0
                        row[player] = f"{avg:.2f}"
                    elif stat_name == "Avg Saves":
                        c.execute("""
                            SELECT SUM(saves), COUNT(DISTINCT match_id)
                            FROM player_stats WHERE player_name = ?
                        """, (player,))
                        saves, games = c.fetchone()
                        avg = (saves or 0) / games if games > 0 else 0
                        row[player] = f"{avg:.2f}"
                    elif stat_name == "Avg Shots":
                        c.execute("""
                            SELECT SUM(shots), COUNT(DISTINCT match_id)
                            FROM player_stats WHERE player_name = ?
                        """, (player,))
                        shots, games = c.fetchone()
                        avg = (shots or 0) / games if games > 0 else 0
                        row[player] = f"{avg:.2f}"
                
                stats_list.append(row)
            
            df_comparison = pd.DataFrame(stats_list)
            left_aligned_table(df_comparison)
        elif player1 != "Choose Player" or player2 != "Choose Player":
            st.info("👈 Select two different players to compare")
    
    st.divider()
    
    # ====================================================
    # LEADERBOARD
    # ====================================================
    st.markdown("## 🏅 Leaderboard")
    
    # Get all players with stats
    c.execute("""
        SELECT DISTINCT player_name
        FROM player_stats
        ORDER BY player_name
    """)
    leaderboard_players = [row[0] for row in c.fetchall()]
    
    if not leaderboard_players:
        st.info("📭 No player data yet")
    else:
        # Calculate averages for all players first
        player_stats_dict = {}
        for player in leaderboard_players:
            c.execute("""
                SELECT
                    COUNT(DISTINCT match_id),
                    SUM(goals),
                    SUM(assists),
                    SUM(saves),
                    SUM(shots)
                FROM player_stats
                WHERE player_name = ?
            """, (player,))
            result = c.fetchone()
            
            if result:
                games, total_goals, total_assists, total_saves, total_shots = result
                if games > 0:
                    avg_goals = (total_goals or 0) / games
                    avg_assists = (total_assists or 0) / games
                    avg_saves = (total_saves or 0) / games
                    avg_shots = (total_shots or 0) / games
                    
                    player_stats_dict[player] = {
                        'games': games,
                        'avg_goals': avg_goals,
                        'avg_assists': avg_assists,
                        'avg_saves': avg_saves,
                        'avg_shots': avg_shots
                    }
        
        # Find max values from calculated stats
        if player_stats_dict:
            max_goals = max(p['avg_goals'] for p in player_stats_dict.values()) or 1
            max_assists = max(p['avg_assists'] for p in player_stats_dict.values()) or 1
            max_saves = max(p['avg_saves'] for p in player_stats_dict.values()) or 1
            max_shots = max(p['avg_shots'] for p in player_stats_dict.values()) or 1
            
            # ====================================================
            # OVERALL PERFORMANCE RATING
            # ====================================================
            st.markdown("## 🏆 Overall Performance Rating")
            
            # Calculate ratings for all players
            overall_ratings = []
            for player in leaderboard_players:
                if player not in player_stats_dict:
                    continue
                
                stats = player_stats_dict[player]
                
                rating = calculate_performance_rating(
                    stats['avg_goals'], stats['avg_assists'], stats['avg_saves'], stats['avg_shots'],
                    max_goals, max_assists, max_saves, max_shots
                )
                
                # Get wins
                c.execute("""
                    SELECT COUNT(*)
                    FROM matches
                    WHERE
                        (
                            team1_players LIKE ?
                            AND winner = 1
                        )
                        OR
                        (
                            team2_players LIKE ?
                            AND winner = 2
                        )
                """, (f"%{player}%", f"%{player}%"))
                wins = c.fetchone()[0]
                
                # Get losses
                c.execute("""
                    SELECT COUNT(*)
                    FROM matches
                    WHERE
                        (
                            team1_players LIKE ?
                            AND winner = 2
                        )
                        OR
                        (
                            team2_players LIKE ?
                            AND winner = 1
                        )
                """, (f"%{player}%", f"%{player}%"))
                losses = c.fetchone()[0]
                
                total_games = wins + losses
                win_pct = (wins / total_games * 100) if total_games > 0 else 0
                
                overall_ratings.append({
                    "🏅 Rank": 0,
                    "🎮 Player": player,
                    "⭐ Rating": rating,
                    "⚽ Avg Goals": f"{stats['avg_goals']:.2f}",
                    "🎁 Avg Assists": f"{stats['avg_assists']:.2f}",
                    "🛡️ Avg Saves": f"{stats['avg_saves']:.2f}",
                    "🔫 Avg Shots": f"{stats['avg_shots']:.2f}",
                    "📊 W-L": f"{wins}-{losses}",
                    "📈 Win %": f"{win_pct:.1f}%"
                })
            
            # Sort by rating
            overall_ratings.sort(key=lambda x: x["⭐ Rating"], reverse=True)
            for idx, rating_data in enumerate(overall_ratings, 1):
                rating_data["🏅 Rank"] = idx
            
            df_overall = pd.DataFrame(overall_ratings)
            left_aligned_table(df_overall)
            
            st.divider()
            # ====================================================
            # MATCH TYPE PERFORMANCE RATINGS
            # ====================================================
            st.markdown("## Match Type Performance Ratings")
            
            for match_type in ["1v1", "2v2", "3v3"]:
                with st.expander(f"{match_type} Performance Rating", expanded=False):
                    # Calculate for this match type
                    type_ratings = []
                    for player in leaderboard_players:
                        c.execute("""
                            SELECT
                                COUNT(DISTINCT match_id),
                                SUM(goals),
                                SUM(assists),
                                SUM(saves),
                                SUM(shots)
                            FROM player_stats
                            WHERE player_name = ?
                            AND match_id IN (
                                SELECT id FROM matches
                                WHERE 
                                    (LENGTH(team1_players) - LENGTH(REPLACE(team1_players, ',', '')))
                                    = ?
                            )
                        """, (
                            player,
                            1 if match_type == "2v2" else (2 if match_type == "3v3" else 0)
                        ))
                        result = c.fetchone()
                        
                        if result and result[0]:  # Has games in this type
                            games, total_goals, total_assists, total_saves, total_shots = result
                            avg_goals = (total_goals or 0) / games
                            avg_assists = (total_assists or 0) / games
                            avg_saves = (total_saves or 0) / games
                            avg_shots = (total_shots or 0) / games
                            
                            # Get max for this type
                            type_max_goals = max([s['avg_goals'] for s in player_stats_dict.values()]) or 1
                            type_max_assists = max([s['avg_assists'] for s in player_stats_dict.values()]) or 1
                            type_max_saves = max([s['avg_saves'] for s in player_stats_dict.values()]) or 1
                            type_max_shots = max([s['avg_shots'] for s in player_stats_dict.values()]) or 1
                            
                            rating = calculate_performance_rating(
                                avg_goals, avg_assists, avg_saves, avg_shots,
                                type_max_goals, type_max_assists, type_max_saves, type_max_shots
                            )
                            
                            type_ratings.append({
                                "🏅 Rank": 0,
                                "🎮 Player": player,
                                "⭐ Rating": rating,
                                "⚽ Avg Goals": f"{avg_goals:.2f}",
                                "🎁 Avg Assists": f"{avg_assists:.2f}",
                                "🛡️ Avg Saves": f"{avg_saves:.2f}",
                                "🔫 Avg Shots": f"{avg_shots:.2f}",
                                "📊 Games": games
                            })
                    
                    if type_ratings:
                        type_ratings.sort(key=lambda x: x["⭐ Rating"], reverse=True)
                        for idx, rating_data in enumerate(type_ratings, 1):
                            rating_data["🏅 Rank"] = idx
                        
                        display_leaderboard(type_ratings)
                    else:
                        st.info(f"No {match_type} games yet")
            
            st.divider()
            st.markdown("### 📊 How Rating is Calculated")
            st.write("""
The **Performance Rating** combines your stats into a single 0-10 score:

**Step 1:** Normalize each stat - Compare your average to the best player's average

**Step 2:** Apply weights to determine importance:
- ⚽ Goals: 40% (most important, wins games)
- 🎁 Assists: 30% (team play)
- 🛡️ Saves: 20% (defense)
- 🔫 Shots: 10% (efficiency)

**Step 3:** Final Rating = (Goals×0.40) + (Assists×0.30) + (Saves×0.20) + (Shots×0.10)

**Example:** If you have the best Goals average (10.0), average Assists (7.5), average Saves (8.0), and average Shots (6.0):
- Rating = (10.0×0.40) + (7.5×0.30) + (8.0×0.20) + (6.0×0.10) = **8.35**

This shows you're better than wins alone, because you're performing well across multiple categories.
            """)

# ============================================================
# TAB 6 - RECORDS
# ============================================================
with tab6:
    if st.button(
        "🔄 Refresh Data",
        use_container_width=True,
        key="refresh_tab6"
    ):
        st.rerun()
    st.divider()
    
    # Get all players
    c.execute("SELECT DISTINCT player_name FROM player_stats ORDER BY player_name")
    all_players = [row[0] for row in c.fetchall()]
    
    if not all_players:
        st.info("📭 No records yet - start logging matches!")
    else:
        # ====================================================
        # INDIVIDUAL RECORDS
        # ====================================================
        st.markdown("## 🎮 Individual Records")
        
        for match_type in ["1v1", "2v2", "3v3"]:
            with st.expander(f"{match_type} Records", expanded=True):
                match_type_num = 1 if match_type == "2v2" else (2 if match_type == "3v3" else 0)
                
                # Determine starting color to alternate between match types
                # 1v1 ends orange, so 2v2/3v3 start blue
                start_color = "orange" if match_type == "1v1" else "blue"
                colors = ["orange", "blue"] if start_color == "orange" else ["blue", "orange"]
                color_idx = 0
                
                col1, col2 = st.columns(2)
                
                # Most Goals in a Game
                with col1:
                    c.execute("""
                        SELECT player_name, MAX(goals) as max_goals
                        FROM player_stats
                        WHERE match_id IN (
                            SELECT id FROM matches
                            WHERE (LENGTH(team1_players) - LENGTH(REPLACE(team1_players, ',', ''))) = ?
                        )
                        GROUP BY player_name
                        ORDER BY max_goals DESC
                        LIMIT 1
                    """, (match_type_num,))
                    result = c.fetchone()
                    if result:
                        display_stat_card(result[0], result[1], "🎯 Most Goals", colors[color_idx % 2])
                        color_idx += 1
                    else:
                        st.info("No data")
                        color_idx += 1
                
                # Most Assists in a Game
                with col2:
                    c.execute("""
                        SELECT player_name, MAX(assists) as max_assists
                        FROM player_stats
                        WHERE match_id IN (
                            SELECT id FROM matches
                            WHERE (LENGTH(team1_players) - LENGTH(REPLACE(team1_players, ',', ''))) = ?
                        )
                        GROUP BY player_name
                        ORDER BY max_assists DESC
                        LIMIT 1
                    """, (match_type_num,))
                    result = c.fetchone()
                    if result:
                        display_stat_card(result[0], result[1], "🎁 Most Assists", colors[color_idx % 2])
                        color_idx += 1
                    else:
                        st.info("No data")
                        color_idx += 1
                
                col1, col2 = st.columns(2)
                
                # Most Saves in a Game
                with col1:
                    c.execute("""
                        SELECT player_name, MAX(saves) as max_saves
                        FROM player_stats
                        WHERE match_id IN (
                            SELECT id FROM matches
                            WHERE (LENGTH(team1_players) - LENGTH(REPLACE(team1_players, ',', ''))) = ?
                        )
                        GROUP BY player_name
                        ORDER BY max_saves DESC
                        LIMIT 1
                    """, (match_type_num,))
                    result = c.fetchone()
                    if result:
                        display_stat_card(result[0], result[1], "🛡️ Most Saves", colors[color_idx % 2])
                        color_idx += 1
                    else:
                        st.info("No data")
                        color_idx += 1
                
                # Most Shots in a Game
                with col2:
                    c.execute("""
                        SELECT player_name, MAX(shots) as max_shots
                        FROM player_stats
                        WHERE match_id IN (
                            SELECT id FROM matches
                            WHERE (LENGTH(team1_players) - LENGTH(REPLACE(team1_players, ',', ''))) = ?
                        )
                        GROUP BY player_name
                        ORDER BY max_shots DESC
                        LIMIT 1
                    """, (match_type_num,))
                    result = c.fetchone()
                    if result:
                        display_stat_card(result[0], result[1], "🔫 Most Shots", colors[color_idx % 2])
                        color_idx += 1
                    else:
                        st.info("No data")
                        color_idx += 1
                
                col1, col2 = st.columns(2)
                
                # Highest Score in a Game
                with col1:
                    c.execute("""
                        SELECT player_name, MAX(score) as max_score
                        FROM player_stats
                        WHERE match_id IN (
                            SELECT id FROM matches
                            WHERE (LENGTH(team1_players) - LENGTH(REPLACE(team1_players, ',', ''))) = ?
                        )
                        GROUP BY player_name
                        ORDER BY max_score DESC
                        LIMIT 1
                    """, (match_type_num,))
                    result = c.fetchone()
                    if result:
                        display_stat_card(result[0], result[1], "⚡ Highest Score", colors[color_idx % 2])
                        color_idx += 1
                    else:
                        st.info("No data")
                        color_idx += 1
                
                # Most Games Played
                with col2:
                    c.execute("""
                        SELECT player_name, COUNT(DISTINCT match_id) as games
                        FROM player_stats
                        WHERE match_id IN (
                            SELECT id FROM matches
                            WHERE (LENGTH(team1_players) - LENGTH(REPLACE(team1_players, ',', ''))) = ?
                        )
                        GROUP BY player_name
                        ORDER BY games DESC
                        LIMIT 1
                    """, (match_type_num,))
                    result = c.fetchone()
                    if result:
                        display_stat_card(result[0], result[1], "📊 Most Games", colors[color_idx % 2])
                        color_idx += 1
                    else:
                        st.info("No data")
                        color_idx += 1
                
                col1, col2 = st.columns(2)
                
                # Best Win %
                with col1:
                    best_win_pct = 0
                    best_player = None
                    for player in all_players:
                        c.execute("""
                            SELECT COUNT(*)
                            FROM matches
                            WHERE
                                (
                                    team1_players LIKE ? AND winner = 1
                                    AND (LENGTH(team1_players) - LENGTH(REPLACE(team1_players, ',', ''))) = ?
                                )
                                OR
                                (
                                    team2_players LIKE ? AND winner = 2
                                    AND (LENGTH(team2_players) - LENGTH(REPLACE(team2_players, ',', ''))) = ?
                                )
                        """, (f"%{player}%", match_type_num, f"%{player}%", match_type_num))
                        wins = c.fetchone()[0]
                        
                        c.execute("""
                            SELECT COUNT(*)
                            FROM matches
                            WHERE
                                (team1_players LIKE ? OR team2_players LIKE ?)
                                AND (LENGTH(team1_players) - LENGTH(REPLACE(team1_players, ',', ''))) = ?
                        """, (f"%{player}%", f"%{player}%", match_type_num))
                        total = c.fetchone()[0]
                        
                        if total >= 5:  # Minimum 5 games
                            pct = (wins / total * 100) if total > 0 else 0
                            if pct > best_win_pct:
                                best_win_pct = pct
                                best_player = player
                    
                    if best_player:
                        display_stat_card(best_player, f"{best_win_pct:.1f}%", "🏆 Best Win %", colors[color_idx % 2])
                        color_idx += 1
                    else:
                        st.info("Need 5+ games")
                        color_idx += 1
                
                # Win Streak
                with col2:
                    best_streak = 0
                    streak_player = None
                    
                    for player in all_players:
                        c.execute("""
                            SELECT id FROM matches
                            WHERE
                                (
                                    team1_players LIKE ? AND winner = 1
                                    AND (LENGTH(team1_players) - LENGTH(REPLACE(team1_players, ',', ''))) = ?
                                )
                                OR
                                (
                                    team2_players LIKE ? AND winner = 2
                                    AND (LENGTH(team2_players) - LENGTH(REPLACE(team2_players, ',', ''))) = ?
                                )
                            ORDER BY id DESC
                        """, (f"%{player}%", match_type_num, f"%{player}%", match_type_num))
                        wins = c.fetchall()
                        
                        if wins:
                            current_streak = 0
                            for i, (win_id,) in enumerate(wins):
                                # Check if next game (before this one) was also a win
                                if i == 0:
                                    current_streak = 1
                                else:
                                    # If there's a gap, streak is broken
                                    c.execute("""
                                        SELECT COUNT(*) FROM matches
                                        WHERE id > ? AND id < ?
                                        AND (
                                            (team1_players LIKE ? AND winner = 2)
                                            OR (team2_players LIKE ? AND winner = 1)
                                        )
                                    """, (wins[i][0], wins[i-1][0], f"%{player}%", f"%{player}%"))
                                    if c.fetchone()[0] > 0:
                                        break
                                    current_streak += 1
                            
                            if current_streak > best_streak:
                                best_streak = current_streak
                                streak_player = player
                    
                    if streak_player:
                        display_stat_card(streak_player, best_streak, "🔥 Win Streak", "orange")
                    else:
                        st.info("No wins yet")

# ============================================================
# CLOSE DATABASE
# ============================================================
conn.close()
