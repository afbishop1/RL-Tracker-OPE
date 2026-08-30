import streamlit as st
import pandas as pd
from datetime import datetime
from collections import defaultdict
import pytz
from supabase import create_client, Client

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
        background: transparent;
        color: #E8EAED;
        font-size: 16px;
        text-align: left !important;
    }
    .rl-stats-table th {
        background: linear-gradient(90deg, rgba(255,107,0,0.2) 0%, rgba(30,144,255,0.2) 100%);
        color: #FFD700;
        font-weight: bold;
        padding: 14px 16px;
        border-top: 2px solid #FF6B00;
        border-bottom: 2px solid #1E90FF;
        text-align: left !important;
        white-space: nowrap;
    }
    .rl-stats-table td {
        padding: 12px 16px;
        border: none;
        border-bottom: 1px solid rgba(255,107,0,0.2);
        text-align: left !important;
        vertical-align: middle;
        white-space: nowrap;
        background: rgba(30, 144, 255, 0.04);
    }
    .rl-stats-table tr:hover td {
        background: rgba(30, 144, 255, 0.12);
    }
    .rl-stats-table tr:last-child td {
        border-bottom: 2px solid rgba(255,107,0,0.3);
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
# SUPABASE SETUP
# ============================================================
@st.cache_resource
def get_supabase() -> Client:
    """Create and cache the Supabase client."""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = get_supabase()

# ============================================================
# AUTO-RENUMBER SERIES (QUICK FIX FOR DELETED SERIES)
# ============================================================
def renumber_series():
    """Renumber series sequentially if gaps exist from deletions"""
    try:
        response = supabase.table("matches").select("series_number").order("series_number").execute()
        if not response.data:
            return
        
        old_series = sorted(list(set(row["series_number"] for row in response.data)))
        
        if not old_series:
            return
        
        # Create mapping from old to new
        old_to_new = {old_num: new_num for new_num, old_num in enumerate(old_series, 1)}
        
        # Update if there are gaps
        expected = {i: i for i in range(1, len(old_series) + 1)}
        if old_to_new != expected:
            for old_num, new_num in old_to_new.items():
                if old_num != new_num:
                    supabase.table("matches").update({"series_number": new_num}).eq("series_number", old_num).execute()
    except Exception as e:
        print(f"Renumber series error: {e}")

# Run renumber on startup
renumber_series()

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
# HELPER: Get match type filter value (comma count)
# ============================================================
def get_comma_count_for_type(match_type: str) -> int:
    """Return the number of commas expected in team1_players for a match type."""
    if match_type == "1v1":
        return 0
    elif match_type == "2v2":
        return 1
    else:  # 3v3
        return 2

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
    try:
        last_match_resp = (
            supabase.table("matches")
            .select("series_number, match_number, best_of")
            .order("series_number", desc=True)
            .order("match_number", desc=True)
            .limit(1)
            .execute()
        )
        last_match = last_match_resp.data[0] if last_match_resp.data else None
    except Exception:
        last_match = None

    if last_match:
        last_series = last_match["series_number"]
        last_bo = last_match["best_of"]
        
        wins_resp = (
            supabase.table("matches")
            .select("id", count="exact")
            .eq("series_number", last_series)
            .not_.is_("winner", "null")
            .execute()
        )
        wins_in_series = wins_resp.count if wins_resp.count is not None else 0
        
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
    try:
        wins_resp = (
            supabase.table("matches")
            .select("winner")
            .eq("series_number", current_series)
            .not_.is_("winner", "null")
            .execute()
        )
        wins = {1: 0, 2: 0}
        for row in wins_resp.data:
            w = row["winner"]
            if w in wins:
                wins[w] += 1
    except Exception:
        wins = {1: 0, 2: 0}
    
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
                        
                        # Insert match
                        match_insert = {
                            "series_number": current_series,
                            "match_number": game["game_num"],
                            "best_of": bo_num,
                            "timestamp": datetime.now().isoformat(),
                            "team1_players": ",".join(game["team1_players"]),
                            "team2_players": ",".join(game["team2_players"]),
                            "team1_score": t1_total,
                            "team2_score": t2_total,
                            "winner": game["winner"]
                        }
                        match_resp = supabase.table("matches").insert(match_insert).execute()
                        match_id = match_resp.data[0]["id"]
                        
                        # Team 1 stats
                        for stat in game["team1_stats"]:
                            supabase.table("player_stats").insert({
                                "match_id": match_id,
                                "player_name": stat["player"],
                                "team": 1,
                                "score": int(stat["score"]),
                                "goals": int(stat["goals"]),
                                "assists": int(stat["assists"]),
                                "saves": int(stat["saves"]),
                                "shots": int(stat["shots"]),
                                "excuse_used": int(stat["excuse_used"])
                            }).execute()
                        
                        # Team 2 stats
                        for stat in game["team2_stats"]:
                            supabase.table("player_stats").insert({
                                "match_id": match_id,
                                "player_name": stat["player"],
                                "team": 2,
                                "score": int(stat["score"]),
                                "goals": int(stat["goals"]),
                                "assists": int(stat["assists"]),
                                "saves": int(stat["saves"]),
                                "shots": int(stat["shots"]),
                                "excuse_used": int(stat["excuse_used"])
                            }).execute()
                    
                    # Activity log
                    supabase.table("activity_log").insert({
                        "timestamp": datetime.now().isoformat(),
                        "user_name": confirming_user,
                        "action": "entered a game"
                    }).execute()
                    
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
    
    try:
        series_resp = (
            supabase.table("matches")
            .select("series_number, best_of, match_number")
            .order("series_number", desc=True)
            .execute()
        )
        # Group by series_number to get unique series
        seen = set()
        series_list = []
        for row in series_resp.data:
            sn = row["series_number"]
            if sn not in seen:
                seen.add(sn)
                series_list.append((sn, row["best_of"], row["match_number"]))
    except Exception:
        series_list = []
    
    if not series_list:
        st.info("📭 No matches logged yet")
    else:
        series_by_type = {
            "1v1": [],
            "2v2": [],
            "3v3": []
        }
        for series_num, bo, last_match in series_list:
            try:
                first_match_resp = (
                    supabase.table("matches")
                    .select("team1_players")
                    .eq("series_number", series_num)
                    .order("match_number")
                    .limit(1)
                    .execute()
                )
                if first_match_resp.data:
                    t1_players = first_match_resp.data[0]["team1_players"].split(",")
                    num_players_in_series = len(t1_players)
                    if num_players_in_series == 1:
                        mt = "1v1"
                    elif num_players_in_series == 2:
                        mt = "2v2"
                    else:
                        mt = "3v3"
                    series_by_type[mt].append((series_num, bo, last_match))
            except Exception:
                pass
        
        for match_type in ["1v1", "2v2", "3v3"]:
            st.markdown(f"## {match_type}")
            if not series_by_type[match_type]:
                st.info(f"📭 No {match_type} series yet")
            else:
                for series_num, bo, last_match in series_by_type[match_type]:
                    try:
                        first_match_resp = (
                            supabase.table("matches")
                            .select("team1_players, team2_players")
                            .eq("series_number", series_num)
                            .order("match_number")
                            .limit(1)
                            .execute()
                        )
                        if first_match_resp.data:
                            t1_players = first_match_resp.data[0]["team1_players"]
                            t2_players = first_match_resp.data[0]["team2_players"]
                            player_info = f"({t1_players} vs {t2_players})"
                            t1_list = t1_players.split(",")
                            t2_list = t2_players.split(",")
                        else:
                            player_info = ""
                            t1_list = []
                            t2_list = []
                        
                        wins_resp = (
                            supabase.table("matches")
                            .select("winner")
                            .eq("series_number", series_num)
                            .execute()
                        )
                        t1_wins = 0
                        t2_wins = 0
                        for row in wins_resp.data:
                            if row["winner"] == 1:
                                t1_wins += 1
                            elif row["winner"] == 2:
                                t2_wins += 1
                        
                        if t1_wins > t2_wins:
                            series_winner = " + ".join(t1_list)
                            series_record = f"{t1_wins}-{t2_wins}"
                        elif t2_wins > t1_wins:
                            series_winner = " + ".join(t2_list)
                            series_record = f"{t2_wins}-{t1_wins}"
                        else:
                            series_winner = "Tied"
                            series_record = f"{t1_wins}-{t2_wins}"
                    except Exception:
                        player_info = ""
                        series_winner = "?"
                        series_record = "?-?"
                        t1_list = []
                        t2_list = []
                    
                    col1, col2 = st.columns([0.95, 0.05])
                    with col1:
                        expander = st.expander(f"📊 Series {series_num} - {series_winner} Won {series_record} {player_info}", expanded=False)
                    with col2:
                        st.write("")
                        if st.button("🗑️", key=f"delete_series_{series_num}", help="Delete this series", use_container_width=True):
                            st.session_state.confirm_delete = True
                            st.session_state.delete_series_num = series_num
                    
                    if st.session_state.get("confirm_delete", False) and st.session_state.get("delete_series_num") == series_num:
                        st.divider()
                        st.markdown(f"### 👤 Who is deleting Series {series_num}?")
                        deleting_user = st.selectbox("Select your name", PLAYERS, key=f"delete_user_{series_num}")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Confirm Delete", use_container_width=True, key=f"confirm_delete_{series_num}"):
                                # Get match IDs for this series
                                matches_resp = (
                                    supabase.table("matches")
                                    .select("id")
                                    .eq("series_number", series_num)
                                    .execute()
                                )
                                match_ids = [m["id"] for m in matches_resp.data]
                                
                                # Delete player_stats first (or rely on cascade)
                                for mid in match_ids:
                                    supabase.table("player_stats").delete().eq("match_id", mid).execute()
                                
                                # Delete matches
                                supabase.table("matches").delete().eq("series_number", series_num).execute()
                                
                                # Activity log
                                supabase.table("activity_log").insert({
                                    "timestamp": datetime.now().isoformat(),
                                    "user_name": deleting_user,
                                    "action": "deleted a game"
                                }).execute()
                                
                                st.session_state.confirm_delete = False
                                st.session_state.delete_series_num = None
                                st.success(f"Series {series_num} deleted by {deleting_user}!")
                                st.rerun()
                    
                    with expander:
                        try:
                            matches_resp = (
                                supabase.table("matches")
                                .select("score, goals, assists, saves, shots, excuse_used")
                                .eq("series_number", series_num)
                                .order("match_number")
                                .execute()
                            )
                            matches = matches_resp.data
                        except Exception:
                            matches = []
                        
                        for match in matches:
                            match_id = match["id"]
                            mn = match["match_number"]
                            t1p = match["team1_players"]
                            t2p = match["team2_players"]
                            winner = match["winner"]
                            
                            if t1p and t2p:
                                t1_players = t1p.split(",")
                                t2_players = t2p.split(",")
                                if winner == 1:
                                    winner_text = " + ".join(t1_players) + " Won"
                                elif winner == 2:
                                    winner_text = " + ".join(t2_players) + " Won"
                                else:
                                    winner_text = "Pending"
                            else:
                                continue
                                winner_text = "Pending"
                            
                            # Goals totals
                            try:
                                t1_goals_resp = (
                                    supabase.table("player_stats")
                                    .select("goals")
                                    .eq("match_id", match_id)
                                    .eq("team", 1)
                                    .execute()
                                )
                                t1_goals = sum(r["goals"] or 0 for r in t1_goals_resp.data)
                                
                                t2_goals_resp = (
                                    supabase.table("player_stats")
                                    .select("goals")
                                    .eq("match_id", match_id)
                                    .eq("team", 2)
                                    .execute()
                                )
                                t2_goals = sum(r["goals"] or 0 for r in t2_goals_resp.data)
                            except Exception:
                                t1_goals = 0
                                t2_goals = 0
                            
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(90deg, rgba(255,107,0,0.15) 0%, rgba(30,144,255,0.15) 100%);
                                border-radius: 8px;
                                padding: 12px 16px;
                                margin-bottom: 12px;
                                border-top: 2px solid #FF6B00;
                                border-bottom: 2px solid #1E90FF;
                            ">
                                <div style="font-size: 1.1em; font-weight: bold; color: #E8EAED;">
                                    🏆 Game {mn} <span style="color: #FFD700;">{winner_text}</span> <span style="color: #87CEEB;">({t1_goals} - {t2_goals})</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
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
                                try:
                                    t1_stats_resp = (
                                        supabase.table("player_stats")
                                        .select("player_name, score, goals, assists, saves, shots")
                                        .eq("match_id", match_id)
                                        .eq("team", 1)
                                        .execute()
                                    )
                                    for row in t1_stats_resp.data:
                                        st.markdown(f"""
                                        <div style="background: rgba(255, 107, 0, 0.1); border-left: 3px solid #FF6B00; padding: 12px; border-radius: 6px; margin-bottom: 8px;">
                                            <div style="font-weight: bold; color: #FFD700; margin-bottom: 6px;">{row['player_name']}</div>
                                            <div style="font-size: 0.9em; color: #E8EAED; display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                                                <span>📍 Score: <b>{row['score']}</b></span>
                                                <span>⚽ Goals: <b>{row['goals']}</b></span>
                                                <span>🎁 Assists: <b>{row['assists']}</b></span>
                                                <span>🛡️ Saves: <b>{row['saves']}</b></span>
                                                <span>🔫 Shots: <b>{row['shots']}</b></span>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                except Exception:
                                    st.info("No stats")
                            
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
                                try:
                                    t2_stats_resp = (
                                        supabase.table("player_stats")
                                        .select("player_name, score, goals, assists, saves, shots")
                                        .eq("match_id", match_id)
                                        .eq("team", 2)
                                        .execute()
                                    )
                                    for row in t2_stats_resp.data:
                                        st.markdown(f"""
                                        <div style="background: rgba(30, 144, 255, 0.1); border-left: 3px solid #1E90FF; padding: 12px; border-radius: 6px; margin-bottom: 8px;">
                                            <div style="font-weight: bold; color: #87CEEB; margin-bottom: 6px;">{row['player_name']}</div>
                                            <div style="font-size: 0.9em; color: #E8EAED; display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                                                <span>📍 Score: <b>{row['score']}</b></span>
                                                <span>⚽ Goals: <b>{row['goals']}</b></span>
                                                <span>🎁 Assists: <b>{row['assists']}</b></span>
                                                <span>🛡️ Saves: <b>{row['saves']}</b></span>
                                                <span>🔫 Shots: <b>{row['shots']}</b></span>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                except Exception:
                                    st.info("No stats")
                            
                            st.divider()
                        
                        st.markdown("### Series Totals")
                        try:
                            # Get all match IDs for series
                            match_ids_resp = (
                                supabase.table("matches")
                                .select("id")
                                .eq("series_number", series_num)
                                .execute()
                            )
                            match_ids = [m["id"] for m in match_ids_resp.data]
                            
                            if match_ids:
                                totals_resp = (
                                    supabase.table("player_stats")
                                    .select("player_name, score, goals, assists, saves, shots")
                                    .in_("match_id", match_ids)
                                    .execute()
                                )
                                
                                # Aggregate in Python
                                player_totals = defaultdict(lambda: {"score": 0, "goals": 0, "assists": 0, "saves": 0, "shots": 0})
                                for row in totals_resp.data:
                                    p = row["player_name"]
                                    player_totals[p]["score"] += row["score"] or 0
                                    player_totals[p]["goals"] += row["goals"] or 0
                                    player_totals[p]["assists"] += row["assists"] or 0
                                    player_totals[p]["saves"] += row["saves"] or 0
                                    player_totals[p]["shots"] += row["shots"] or 0
                                
                                sorted_totals = sorted(player_totals.items(), key=lambda x: x[1]["score"], reverse=True)
                                for pname, totals in sorted_totals:
                                    st.markdown(f"""
                                    <div style="background: rgba(255, 165, 0, 0.08); border: 1px solid rgba(255, 107, 0, 0.3); padding: 10px; border-radius: 6px; margin-bottom: 6px;">
                                        <div style="font-weight: bold; color: #FFD700; margin-bottom: 4px;">{pname}</div>
                                        <div style="font-size: 0.85em; color: #E8EAED; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px;">
                                            <span>📍 {totals['score']}</span>
                                            <span>⚽ {totals['goals']}</span>
                                            <span>🎁 {totals['assists']}</span>
                                            <span>🛡️ {totals['saves']}</span>
                                            <span>🔫 {totals['shots']}</span>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                        except Exception as e:
                            st.info(f"Could not load series totals: {e}")
            
            st.divider()
    
    # Activity Log
    st.markdown("## 📋 Activity Log")
    try:
        logs_resp = (
            supabase.table("activity_log")
            .select("timestamp, user_name, action")
            .order("timestamp", desc=True)
            .limit(50)
            .execute()
        )
        logs = logs_resp.data
    except Exception:
        logs = []
    
    if not logs:
        st.info("📭 No activity yet")
    else:
        eastern = pytz.timezone("US/Eastern")
        for log in logs:
            timestamp = log["timestamp"]
            user_name = log["user_name"]
            action = log["action"]
            try:
                # Handle both with and without timezone
                if "Z" in timestamp or "+" in timestamp or timestamp.endswith("00"):
                    ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                else:
                    ts = datetime.fromisoformat(timestamp)
                
                ts_utc = pytz.UTC.localize(ts) if ts.tzinfo is None else ts
                ts_eastern = ts_utc.astimezone(eastern)
                ts_str = ts_eastern.strftime("%m/%d %I:%M %p")
            except Exception:
                ts_str = timestamp
            st.markdown(f"**{user_name}** {action} · {ts_str}")
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
    
    # Fetch all player_stats once and cache it
    try:
        all_stats_resp = supabase.table("player_stats").select("player_name, score, goals, assists, saves, shots, excuse_used").execute()
        all_player_stats = all_stats_resp.data if all_stats_resp.data else []
    except Exception:
        all_player_stats = []
    
    try:
        players_resp = (
            supabase.table("player_stats")
            .select("player_name")
            .execute()
        )
        all_players_list = sorted(list(set(row["player_name"] for row in players_resp.data)))
    except Exception:
        all_players_list = []
    
    if not all_players_list:
        st.info("📭 No player data yet")
    else:
        # Get overall stats for each player
        overall_stats = {}
        for player in all_players_list:
            # Wins - simplified without .or_()
            try:
                all_m = supabase.table("matches").select("team1_players, team2_players, winner").execute()
                wins = sum(
                    1 for m in all_m.data
                    if m.get("team1_players") and m.get("team2_players") and (
                        (player in [p.strip() for p in m["team1_players"].split(",")] and m["winner"] == 1) or
                        (player in [p.strip() for p in m["team2_players"].split(",")] and m["winner"] == 2)
                    )
                )
            except Exception:
                wins = 0
            
            # Losses - simplified without .or_()
            try:
                all_m = supabase.table("matches").select("team1_players, team2_players, winner").execute()
                losses = sum(
                    1 for m in all_m.data
                    if m.get("team1_players") and m.get("team2_players") and (
                        (player in [p.strip() for p in m["team1_players"].split(",")] and m["winner"] == 2) or
                        (player in [p.strip() for p in m["team2_players"].split(",")] and m["winner"] == 1)
                    )
                )
            except Exception:
                losses = 0
            
            games = wins + losses
            win_pct = (wins / games) * 100 if games > 0 else 0
            
            # Aggregated stats - use cached all_player_stats with proper local filtering
            player_stats = [r for r in all_player_stats if r.get("player_name") and r["player_name"].strip() == player.strip()]
            score = sum(int(r.get("score") or 0) for r in player_stats)
            goals = sum(int(r.get("goals") or 0) for r in player_stats)
            assists = sum(int(r.get("assists") or 0) for r in player_stats)
            saves = sum(int(r.get("saves") or 0) for r in player_stats)
            shots = sum(int(r.get("shots") or 0) for r in player_stats)
            excuses = sum(int(r.get("excuse_used") or 0) for r in player_stats)
            
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
        df_wins = df_wins.sort_values("🏆 Wins", ascending=False)
        left_aligned_table(df_wins)
        st.divider()
        
        # ====================================================
        # CAREER TOTALS
        # ====================================================
        st.markdown("### Career Totals (All Matches)")
        totals_data = []
        for player in sorted(all_players_list, key=lambda p: overall_stats[p]["wins"], reverse=True):
            stat = overall_stats[player]
            totals_data.append({
                "🎮 Player": player,
                "📊 Games": stat["games"],
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
        for player in sorted(all_players_list, key=lambda p: overall_stats[p]["wins"], reverse=True):
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
                comma_count = get_comma_count_for_type(match_type)
                
                # Get all matches of this type once
                try:
                    all_matches = supabase.table("matches").select("id, team1_players").execute()
                    type_match_ids = set(
                        m["id"] for m in all_matches.data
                        if m.get("team1_players") and (m["team1_players"].count(",") == comma_count)
                    )
                except Exception:
                    type_match_ids = set()
                
                if not type_match_ids:
                    st.info(f"No {match_type} games yet")
                    continue
                
                for player in sorted(all_players_list, key=lambda p: overall_stats[p]["wins"], reverse=True):
                    try:
                        # Filter cached stats by player name and match type
                        player_stats = [
                            r for r in all_player_stats 
                            if r.get("player_name") and r["player_name"].strip() == player.strip() 
                            and r.get("match_id") in type_match_ids
                        ]
                        
                        if player_stats:
                            score = sum(int(r.get("score") or 0) for r in player_stats)
                            goals = sum(int(r.get("goals") or 0) for r in player_stats)
                            assists = sum(int(r.get("assists") or 0) for r in player_stats)
                            saves = sum(int(r.get("saves") or 0) for r in player_stats)
                            shots = sum(int(r.get("shots") or 0) for r in player_stats)
                            excuses = sum(int(r.get("excuse_used") or 0) for r in player_stats)
                            games = len(set(r["match_id"] for r in player_stats))
                            
                            type_totals.append({
                                "🎮 Player": player,
                                "📊 Games": games,
                                "🎯 Score": score,
                                "⚽ Goals": goals,
                                "🎁 Assists": assists,
                                "🛡️ Saves": saves,
                                "🔫 Shots": shots,
                                "🤥 Excuses": excuses
                            })
                    except Exception:
                        pass
                
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
                comma_count = get_comma_count_for_type(match_type)
                
                # Get all matches of this type once
                try:
                    all_matches = supabase.table("matches").select("id, team1_players").execute()
                    type_match_ids = set(
                        m["id"] for m in all_matches.data
                        if m.get("team1_players") and (m["team1_players"].count(",") == comma_count)
                    )
                except Exception:
                    type_match_ids = set()
                
                if not type_match_ids:
                    st.info(f"No {match_type} games yet")
                    continue
                
                for player in sorted(all_players_list, key=lambda p: overall_stats[p]["wins"], reverse=True):
                    try:
                        # Filter cached stats by player name and match type
                        player_stats = [
                            r for r in all_player_stats 
                            if r.get("player_name") and r["player_name"].strip() == player.strip() 
                            and r.get("match_id") in type_match_ids
                        ]
                        
                        if player_stats:
                            score = sum(int(r.get("score") or 0) for r in player_stats)
                            goals = sum(int(r.get("goals") or 0) for r in player_stats)
                            assists = sum(int(r.get("assists") or 0) for r in player_stats)
                            saves = sum(int(r.get("saves") or 0) for r in player_stats)
                            shots = sum(int(r.get("shots") or 0) for r in player_stats)
                            excuses = sum(int(r.get("excuse_used") or 0) for r in player_stats)
                            games = len(set(r["match_id"] for r in player_stats))
                            
                            type_avgs.append({
                                "🎮 Player": player,
                                "📍 Avg Score": f"{score / games:.1f}",
                                "⚽ Avg Goals": f"{goals / games:.2f}",
                                "🎁 Avg Assists": f"{assists / games:.2f}",
                                "🛡️ Avg Saves": f"{saves / games:.2f}",
                                "🔫 Avg Shots": f"{shots / games:.2f}",
                                "🤥 Avg Excuses": f"{excuses / games:.2f}"
                            })
                    except Exception:
                        pass
                
                if type_avgs:
                    df_type_avg = pd.DataFrame(type_avgs)
                    left_aligned_table(df_type_avg)
                else:
                    st.info(f"No {match_type} games yet")
        
        st.divider()

# ============================================================
# TAB 4 - TEAMS / MATCHUPS
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
    
    try:
        all_match_data = supabase.table("matches").select("id, team1_players, team2_players, winner").execute().data
    except Exception:
        all_match_data = []
    
    if all_match_data:
        partnerships = defaultdict(lambda: {"wins": 0, "losses": 0})
        
        for match in all_match_data:
            t1 = match["team1_players"]
            t2 = match["team2_players"]
            winner = match["winner"]
            
            if not t1 or not t2:
                continue
            
            t1_list = t1.split(",")
            t2_list = t2.split(",")
            
            # Only count 2v2 and 3v3 (skip 1v1)
            if len(t1_list) == 1:
                continue
            
            t1_team = tuple(sorted(t1_list))
            t2_team = tuple(sorted(t2_list))
            
            if winner == 1:
                partnerships[t1_team]["wins"] += 1
                partnerships[t2_team]["losses"] += 1
            else:
                partnerships[t2_team]["wins"] += 1
                partnerships[t1_team]["losses"] += 1
        
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
    
    try:
        one_v_one_matches = [
            m for m in all_match_data
            if m["team1_players"].count(",") == 0
        ]
    except Exception:
        one_v_one_matches = []
    
    if not one_v_one_matches:
        st.info("📭 No 1v1 matches yet")
    else:
        # Build head-to-head records
        h2h_records = defaultdict(lambda: defaultdict(lambda: {"wins": 0, "losses": 0}))
        
        for match in one_v_one_matches:
            p1 = match["team1_players"].strip()
            p2 = match["team2_players"].strip()
            winner = match["winner"]
            
            if winner == 1:
                h2h_records[p1][p2]["wins"] += 1
                h2h_records[p2][p1]["losses"] += 1
            elif winner == 2:
                h2h_records[p2][p1]["wins"] += 1
                h2h_records[p1][p2]["losses"] += 1
        
        # Display for each player
        try:
            all_players_with_stats = sorted(list(set(
                row["player_name"] for row in 
                supabase.table("player_stats").select("player_name").execute().data
            )))
        except Exception:
            all_players_with_stats = []
        
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
    
    # Detailed 2v2 / 3v3 teams + matchups (kept from original logic)
    if all_match_data:
        partnerships_by_type = {
            "2v2": defaultdict(lambda: {"wins": 0, "losses": 0}),
            "3v3": defaultdict(lambda: {"wins": 0, "losses": 0})
        }
        matchups_by_type = {
            "2v2": defaultdict(lambda: defaultdict(lambda: {"wins": 0, "losses": 0})),
            "3v3": defaultdict(lambda: defaultdict(lambda: {"wins": 0, "losses": 0}))
        }
        
        for match in all_match_data:
            t1 = match.get("team1_players")
            t2 = match.get("team2_players")
            if not t1 or not t2:
                continue
            
            t1_list = t1.split(",")
            t2_list = t2.split(",")
            winner = match["winner"]
            
            if len(t1_list) == 1:
                continue
            elif len(t1_list) == 2:
                mt = "2v2"
            else:
                mt = "3v3"
            
            partnerships = partnerships_by_type[mt]
            matchups = matchups_by_type[mt]
            
            if mt == "2v2":
                t1_pairs = []
                for i in range(len(t1_list)):
                    for j in range(i + 1, len(t1_list)):
                        pair = tuple(sorted([t1_list[i], t1_list[j]]))
                        t1_pairs.append(pair)
                        if winner == 1:
                            partnerships[pair]["wins"] += 1
                        else:
                            partnerships[pair]["losses"] += 1
                
                t2_pairs = []
                for i in range(len(t2_list)):
                    for j in range(i + 1, len(t2_list)):
                        pair = tuple(sorted([t2_list[i], t2_list[j]]))
                        t2_pairs.append(pair)
                        if winner == 2:
                            partnerships[pair]["wins"] += 1
                        else:
                            partnerships[pair]["losses"] += 1
            else:
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
                t1_pairs = [t1_team]
                t2_pairs = [t2_team]
            
            # Matchups
            for t1_pair in t1_pairs:
                for t2_pair in t2_pairs:
                    if winner == 1:
                        matchups[t1_pair][t2_pair]["wins"] += 1
                        matchups[t2_pair][t1_pair]["losses"] += 1
                    else:
                        matchups[t1_pair][t2_pair]["losses"] += 1
                        matchups[t2_pair][t1_pair]["wins"] += 1
        
        # Display teams
        for mt in ["2v2", "3v3"]:
            partnerships = partnerships_by_type[mt]
            matchups = matchups_by_type[mt]
            st.markdown(f"## {mt} Teams")
            if not partnerships:
                st.info(f"📭 No {mt} team data yet")
            else:
                part_data = []
                for partnership_tuple, record in partnerships.items():
                    total = record["wins"] + record["losses"]
                    win_pct = (record["wins"] / total * 100) if total > 0 else 0
                    display = " + ".join(partnership_tuple)
                    part_data.append({
                        "partnership": partnership_tuple,
                        "display": display,
                        "wins": record["wins"],
                        "losses": record["losses"],
                        "total": total,
                        "win_pct": win_pct
                    })
                part_data.sort(key=lambda x: x["wins"], reverse=True)
                
                for partnership_info in part_data:
                    part_tuple = partnership_info["partnership"]
                    total = partnership_info["total"]
                    win_pct = partnership_info["win_pct"]
                    with st.expander(
                        f"🤝 {partnership_info['display']} · "
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
                        st.markdown("**Head-to-Head vs Other Teams:**")
                        matchup_records = []
                        if part_tuple in matchups:
                            for opponent_tuple, record in matchups[part_tuple].items():
                                h2h_total = record["wins"] + record["losses"]
                                h2h_pct = (record["wins"] / h2h_total * 100) if h2h_total > 0 else 0
                                opponent_display = " + ".join(opponent_tuple)
                                matchup_records.append({
                                    "opponent": opponent_display,
                                    "wins": record["wins"],
                                    "losses": record["losses"],
                                    "total": h2h_total,
                                    "pct": h2h_pct
                                })
                        if matchup_records:
                            matchup_records.sort(key=lambda x: x["wins"], reverse=True)
                            for matchup in matchup_records:
                                st.markdown(
                                    f"vs **{matchup['opponent']}** · "
                                    f"{matchup['wins']}-"
                                    f"{matchup['losses']} "
                                    f"({matchup['pct']:.1f}%)"
                                )
                        else:
                            st.markdown("*No matchup data yet*")
                st.divider()

# ============================================================
# TAB 5 - ANALYSIS / LEADERBOARD
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
    
    try:
        all_comparison_players = sorted(list(set(
            row["player_name"] for row in
            supabase.table("player_stats").select("player_name").execute().data
        )))
    except Exception:
        all_comparison_players = []
    
    if all_comparison_players:
        comparison_options = ["Choose Player"] + all_comparison_players
        
        col1, col_vs, col2 = st.columns([2, 0.5, 2])
        
        with col1:
            st.markdown("<p style='text-align: center; color: #FF6B00; font-weight: bold;'>👤 Player 1</p>", unsafe_allow_html=True)
            player1 = st.selectbox("Player 1", comparison_options, key="comp_p1")
        
        with col_vs:
            st.write("")
            st.write("")
            st.markdown("<p style='text-align: center; font-size: 1.2em; font-weight: bold;'>VS</p>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<p style='text-align: center; color: #1E90FF; font-weight: bold;'>👤 Player 2</p>", unsafe_allow_html=True)
            player2 = st.selectbox("Player 2", comparison_options, key="comp_p2")
        
        st.divider()
        
        if player1 != "Choose Player" and player2 != "Choose Player" and player1 != player2:
            # Build comparison table
            stats_list = []
            stats_names = ["Games", "Wins", "Losses", "Win %", "Avg Goals", "Avg Assists", "Avg Saves", "Avg Shots"]
            
            for stat_name in stats_names:
                row = {"📊 Stat": stat_name}
                for player in [player1, player2]:
                    if stat_name == "Games":
                        try:
                            g_resp = (
                                supabase.table("player_stats")
                                .select("match_id")
                                .eq("player_name", player.strip())
                                .execute()
                            )
                            row[player] = len(set(r["match_id"] for r in g_resp.data))
                        except Exception:
                            row[player] = 0
                    elif stat_name == "Wins":
                        try:
                            all_m = supabase.table("matches").select("team1_players, team2_players, winner").execute().data
                            row[player] = sum(
                                1 for m in all_m
                                if (player in m["team1_players"] and m["winner"] == 1) or
                                   (player in m["team2_players"] and m["winner"] == 2)
                            )
                        except Exception:
                            row[player] = 0
                    elif stat_name == "Losses":
                        try:
                            all_m = supabase.table("matches").select("team1_players, team2_players, winner").execute().data
                            row[player] = sum(
                                1 for m in all_m
                                if (player in m["team1_players"] and m["winner"] == 2) or
                                   (player in m["team2_players"] and m["winner"] == 1)
                            )
                        except Exception:
                            row[player] = 0
                    elif stat_name == "Win %":
                        try:
                            all_m = supabase.table("matches").select("team1_players, team2_players, winner").execute().data
                            wins = sum(
                                1 for m in all_m
                                if (player in m["team1_players"] and m["winner"] == 1) or
                                   (player in m["team2_players"] and m["winner"] == 2)
                            )
                            g_resp = (
                                supabase.table("player_stats")
                                .select("match_id")
                                .eq("player_name", player.strip())
                                .execute()
                            )
                            total = len(set(r["match_id"] for r in g_resp.data))
                            pct = (wins / total * 100) if total > 0 else 0
                            row[player] = f"{pct:.1f}%"
                        except Exception:
                            row[player] = "0.0%"
                    elif stat_name == "Avg Goals":
                        try:
                            s_resp = (
                                supabase.table("player_stats")
                                .select("goals, match_id")
                                .eq("player_name", player.strip())
                                .execute()
                            )
                            goals = sum(r["goals"] or 0 for r in s_resp.data)
                            games = len(set(r["match_id"] for r in s_resp.data))
                            avg = goals / games if games > 0 else 0
                            row[player] = f"{avg:.2f}"
                        except Exception:
                            row[player] = "0.00"
                    elif stat_name == "Avg Assists":
                        try:
                            s_resp = (
                                supabase.table("player_stats")
                                .select("assists, match_id")
                                .eq("player_name", player.strip())
                                .execute()
                            )
                            assists = sum(r["assists"] or 0 for r in s_resp.data)
                            games = len(set(r["match_id"] for r in s_resp.data))
                            avg = assists / games if games > 0 else 0
                            row[player] = f"{avg:.2f}"
                        except Exception:
                            row[player] = "0.00"
                    elif stat_name == "Avg Saves":
                        try:
                            s_resp = (
                                supabase.table("player_stats")
                                .select("saves, match_id")
                                .eq("player_name", player.strip())
                                .execute()
                            )
                            saves = sum(r["saves"] or 0 for r in s_resp.data)
                            games = len(set(r["match_id"] for r in s_resp.data))
                            avg = saves / games if games > 0 else 0
                            row[player] = f"{avg:.2f}"
                        except Exception:
                            row[player] = "0.00"
                    elif stat_name == "Avg Shots":
                        try:
                            s_resp = (
                                supabase.table("player_stats")
                                .select("shots, match_id")
                                .eq("player_name", player.strip())
                                .execute()
                            )
                            shots = sum(r["shots"] or 0 for r in s_resp.data)
                            games = len(set(r["match_id"] for r in s_resp.data))
                            avg = shots / games if games > 0 else 0
                            row[player] = f"{avg:.2f}"
                        except Exception:
                            row[player] = "0.00"
                
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
    
    try:
        leaderboard_players = sorted(list(set(
            row["player_name"] for row in
            supabase.table("player_stats").select("player_name").execute().data
        )))
    except Exception:
        leaderboard_players = []
    
    if not leaderboard_players:
        st.info("📭 No player data yet")
    else:
        # Calculate averages for all players first
        player_stats_dict = {}
        for player in leaderboard_players:
            try:
                s_resp = (
                    supabase.table("player_stats")
                    .select("goals, assists, saves, shots, match_id")
                    .eq("player_name", player.strip())
                    .execute()
                )
                if s_resp.data:
                    games = len(set(r["match_id"] for r in s_resp.data))
                    if games > 0:
                        avg_goals = sum(r["goals"] or 0 for r in s_resp.data) / games
                        avg_assists = sum(r["assists"] or 0 for r in s_resp.data) / games
                        avg_saves = sum(r["saves"] or 0 for r in s_resp.data) / games
                        avg_shots = sum(r["shots"] or 0 for r in s_resp.data) / games
                        
                        player_stats_dict[player] = {
                            'games': games,
                            'avg_goals': avg_goals,
                            'avg_assists': avg_assists,
                            'avg_saves': avg_saves,
                            'avg_shots': avg_shots
                        }
            except Exception:
                pass
        
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
                
                # Get wins / losses
                try:
                    all_m = supabase.table("matches").select("team1_players, team2_players, winner").execute().data
                    wins = sum(
                        1 for m in all_m
                        if (player in m["team1_players"] and m["winner"] == 1) or
                           (player in m["team2_players"] and m["winner"] == 2)
                    )
                    losses = sum(
                        1 for m in all_m
                        if (player in m["team1_players"] and m["winner"] == 2) or
                           (player in m["team2_players"] and m["winner"] == 1)
                    )
                except Exception:
                    wins = losses = 0
                
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
                    type_ratings = []
                    comma_count = get_comma_count_for_type(match_type)
                    
                    for player in leaderboard_players:
                        try:
                            all_matches = supabase.table("matches").select("id, team1_players").execute().data
                            type_match_ids = [
                                m["id"] for m in all_matches
                                if m["team1_players"].count(",") == comma_count
                            ]
                            
                            if not type_match_ids:
                                continue
                            
                            s_resp = (
                                supabase.table("player_stats")
                                .select("goals, assists, saves, shots, match_id")
                                .eq("player_name", player.strip())
                                .in_("match_id", type_match_ids)
                                .execute()
                            )
                            
                            if s_resp.data:
                                games = len(set(r["match_id"] for r in s_resp.data))
                                if games > 0:
                                    avg_goals = sum(r["goals"] or 0 for r in s_resp.data) / games
                                    avg_assists = sum(r["assists"] or 0 for r in s_resp.data) / games
                                    avg_saves = sum(r["saves"] or 0 for r in s_resp.data) / games
                                    avg_shots = sum(r["shots"] or 0 for r in s_resp.data) / games
                                    
                                    # Use overall max for consistency (or recalculate per type if preferred)
                                    type_max_goals = max_goals
                                    type_max_assists = max_assists
                                    type_max_saves = max_saves
                                    type_max_shots = max_shots
                                    
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
                        except Exception:
                            pass
                    
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
    
    try:
        all_players = sorted(list(set(
            row["player_name"] for row in
            supabase.table("player_stats").select("player_name").execute().data
        )))
    except Exception:
        all_players = []
    
    if not all_players:
        st.info("📭 No records yet - start logging matches!")
    else:
        # ====================================================
        # INDIVIDUAL RECORDS
        # ====================================================
        st.markdown("## 🎮 Individual Records")
        
        for match_type in ["1v1", "2v2", "3v3"]:
            with st.expander(f"{match_type} Records", expanded=True):
                comma_count = get_comma_count_for_type(match_type)
                
                # Determine starting color to alternate between match types
                start_color = "orange" if match_type == "1v1" else "blue"
                colors = ["orange", "blue"] if start_color == "orange" else ["blue", "orange"]
                color_idx = 0
                
                # Get match IDs of this type once
                try:
                    all_matches = supabase.table("matches").select("id, team1_players").execute().data
                    type_match_ids = [
                        m["id"] for m in all_matches
                        if m.get("team1_players") and (m["team1_players"].count(",") == comma_count)
                    ]
                    st.write(f"DEBUG {match_type}: Found {len(type_match_ids)} matches of this type")
                except Exception as e:
                    st.write(f"DEBUG ERROR: {e}")
                    type_match_ids = []
                
                col1, col2 = st.columns(2)
                
                # Most Goals in a Game
                with col1:
                    if type_match_ids:
                        try:
                            stats = (
                                supabase.table("player_stats")
                                .select("player_name, goals")
                                .in_("match_id", type_match_ids)
                                .order("goals", desc=True)
                                .limit(1)
                                .execute()
                            )
                            st.write(f"DEBUG Goals Query: type_match_ids={type_match_ids[:3]}..., returned: {stats.data}")
                            if stats.data:
                                display_stat_card(stats.data[0]["player_name"], stats.data[0]["goals"], "⚽ Most Goals", colors[color_idx % 2])
                            else:
                                st.info("No data")
                        except Exception as e:
                            st.write(f"DEBUG ERROR: {e}")
                            st.info("No data")
                    else:
                        st.info("No data")
                    color_idx += 1
                
                # Most Assists in a Game
                with col2:
                    if type_match_ids:
                        try:
                            stats = (
                                supabase.table("player_stats")
                                .select("player_name, assists")
                                .in_("match_id", type_match_ids)
                                .order("assists", desc=True)
                                .limit(1)
                                .execute()
                            )
                            if stats.data:
                                display_stat_card(stats.data[0]["player_name"], stats.data[0]["assists"], "🎁 Most Assists", colors[color_idx % 2])
                            else:
                                st.info("No data")
                        except Exception:
                            st.info("No data")
                    else:
                        st.info("No data")
                    color_idx += 1
                
                col1, col2 = st.columns(2)
                
                # Most Saves in a Game
                with col1:
                    if type_match_ids:
                        try:
                            stats = (
                                supabase.table("player_stats")
                                .select("player_name, saves")
                                .in_("match_id", type_match_ids)
                                .order("saves", desc=True)
                                .limit(1)
                                .execute()
                            )
                            if stats.data:
                                display_stat_card(stats.data[0]["player_name"], stats.data[0]["saves"], "🛡️ Most Saves", colors[color_idx % 2])
                            else:
                                st.info("No data")
                        except Exception:
                            st.info("No data")
                    else:
                        st.info("No data")
                    color_idx += 1
                
                # Most Shots in a Game
                with col2:
                    if type_match_ids:
                        try:
                            stats = (
                                supabase.table("player_stats")
                                .select("player_name, shots")
                                .in_("match_id", type_match_ids)
                                .order("shots", desc=True)
                                .limit(1)
                                .execute()
                            )
                            if stats.data:
                                display_stat_card(stats.data[0]["player_name"], stats.data[0]["shots"], "🔫 Most Shots", colors[color_idx % 2])
                            else:
                                st.info("No data")
                        except Exception:
                            st.info("No data")
                    else:
                        st.info("No data")
                    color_idx += 1
                
                col1, col2 = st.columns(2)
                
                # Highest Score in a Game
                with col1:
                    if type_match_ids:
                        try:
                            stats = (
                                supabase.table("player_stats")
                                .select("player_name, score")
                                .in_("match_id", type_match_ids)
                                .order("score", desc=True)
                                .limit(1)
                                .execute()
                            )
                            if stats.data:
                                display_stat_card(stats.data[0]["player_name"], stats.data[0]["score"], "⚡ Highest Score", colors[color_idx % 2])
                            else:
                                st.info("No data")
                        except Exception:
                            st.info("No data")
                    else:
                        st.info("No data")
                    color_idx += 1
                
                # Most Games Played
                with col2:
                    if type_match_ids:
                        try:
                            stats = (
                                supabase.table("player_stats")
                                .select("player_name, match_id")
                                .in_("match_id", type_match_ids)
                                .execute()
                            )
                            if stats.data:
                                from collections import Counter
                                counts = Counter(r["player_name"] for r in stats.data)
                                top = counts.most_common(1)[0]
                                display_stat_card(top[0], top[1], "📊 Most Games", colors[color_idx % 2])
                            else:
                                st.info("No data")
                        except Exception:
                            st.info("No data")
                    else:
                        st.info("No data")
                    color_idx += 1
                
                col1, col2 = st.columns(2)
                
                # Best Win %
                with col1:
                    best_win_pct = 0
                    best_player = None
                    for player in all_players:
                        try:
                            all_m = supabase.table("matches").select("id, team1_players, team2_players, winner").execute().data
                            type_matches = [
                                m for m in all_m
                                if m["team1_players"].count(",") == comma_count
                            ]
                            wins = sum(
                                1 for m in type_matches
                                if (player in m["team1_players"] and m["winner"] == 1) or
                                   (player in m["team2_players"] and m["winner"] == 2)
                            )
                            total = sum(
                                1 for m in type_matches
                                if player in m["team1_players"] or player in m["team2_players"]
                            )
                            if total >= 5:
                                pct = (wins / total * 100) if total > 0 else 0
                                if pct > best_win_pct:
                                    best_win_pct = pct
                                    best_player = player
                        except Exception:
                            pass
                    
                    if best_player:
                        display_stat_card(best_player, f"{best_win_pct:.1f}%", "🏆 Best Win %", colors[color_idx % 2])
                    else:
                        st.info("Need 5+ games")
                    color_idx += 1
                
                # Win Streak (simplified - current consecutive wins from most recent)
                with col2:
                    best_streak = 0
                    streak_player = None
                    
                    for player in all_players:
                        try:
                            # Get matches involving player of this type, ordered by id desc
                            all_m = (
                                supabase.table("matches")
                                .select("id, team1_players, team2_players, winner")
                                .order("id", desc=True)
                                .execute()
                            ).data
                            
                            type_matches = [
                                m for m in all_m
                                if m["team1_players"].count(",") == comma_count and
                                   (player in m["team1_players"] or player in m["team2_players"])
                            ]
                            
                            current_streak = 0
                            for m in type_matches:
                                won = (player in m["team1_players"] and m["winner"] == 1) or \
                                      (player in m["team2_players"] and m["winner"] == 2)
                                if won:
                                    current_streak += 1
                                else:
                                    break
                            
                            if current_streak > best_streak:
                                best_streak = current_streak
                                streak_player = player
                        except Exception:
                            pass
                    
                    if streak_player and best_streak > 0:
                        display_stat_card(streak_player, best_streak, "🔥 Win Streak", "orange")
                    else:
                        st.info("No wins yet")
