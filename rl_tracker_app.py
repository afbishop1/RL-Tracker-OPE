import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from collections import defaultdict

# Page config
st.set_page_config(
    page_title="RL Match Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Rocket League theme
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
    
    /* Style radio buttons - alternating orange and blue */
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
        background: linear-gradient(135deg, rgba(30, 144, 255, 0.1), rgba(255, 107, 0, 0.1));
        border: 1px solid var(--rl-orange);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        text-align: center;
    }
    
    [data-testid="stMetricValue"] {
        color: var(--rl-orange);
    }
    

</style>
""", unsafe_allow_html=True)

# Database setup
def init_db():
    conn = sqlite3.connect("rl_matches.db")
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS matches
                 (id INTEGER PRIMARY KEY,
                  series_number INTEGER,
                  match_number INTEGER,
                  best_of INTEGER,
                  timestamp TEXT,
                  team1_players TEXT,
                  team2_players TEXT,
                  team1_score INTEGER,
                  team2_score INTEGER,
                  winner INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS player_stats
                 (id INTEGER PRIMARY KEY,
                  match_id INTEGER,
                  player_name TEXT,
                  team INTEGER,
                  score INTEGER,
                  goals INTEGER,
                  assists INTEGER,
                  saves INTEGER,
                  shots INTEGER,
                  FOREIGN KEY(match_id) REFERENCES matches(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS activity_log
                 (id INTEGER PRIMARY KEY,
                  timestamp TEXT,
                  user_name TEXT,
                  action TEXT)''')
    
    # Auto-migration: Add shots column if it doesn't exist
    try:
        c.execute("PRAGMA table_info(player_stats)")
        columns = [row[1] for row in c.fetchall()]
        if 'shots' not in columns:
            c.execute("ALTER TABLE player_stats ADD COLUMN shots INTEGER DEFAULT 0")
            conn.commit()
    except Exception as e:
        print(f"Migration error: {e}")
    
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

PLAYERS = ["Killmesmallz", "See Me No Mor", "Bon Qwee Qwee", "CrabLegz19", "GunzMcgee73", "BucciXman", "SirLagz54"]

# Title
st.markdown('<div class="title-main">⚡ RL MATCH TRACKER ⚡</div>', unsafe_allow_html=True)
st.markdown("OPE Gaming", unsafe_allow_html=True)
st.divider()

# Initialize session state for confirmations
if 'confirm_submit' not in st.session_state:
    st.session_state.confirm_submit = False
if 'confirm_delete' not in st.session_state:
    st.session_state.confirm_delete = False
if 'delete_series_num' not in st.session_state:
    st.session_state.delete_series_num = None

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Log Match", "📊 Series History", "🏆 Player Stats", "👥 Teams"])

# ============ TAB 1: LOG MATCH ============
with tab1:
    # Refresh Data and Clear Players/Scores buttons (side by side)
    refresh_col, clear_col = st.columns(2)
    
    with refresh_col:
        if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_tab1"):
            st.rerun()
    
    with clear_col:
        if st.button("🔄 Clear Players/Scores", use_container_width=True, key="clear_main"):
            st.session_state.reset_counter = st.session_state.get('reset_counter', 0) + 1
            st.rerun()
    
    # JavaScript to color both buttons
    st.markdown("""
<script>
    function colorButtons() {
        let buttons = document.querySelectorAll('button');
        let refreshFound = false;
        let clearFound = false;
        
        buttons.forEach(btn => {
            if (btn.textContent.includes('Refresh Data')) {
                btn.style.background = 'linear-gradient(90deg, #1E90FF 0%, #4169E1 100%)';
                btn.style.color = 'white';
                btn.style.border = 'none';
                btn.style.borderRadius = '8px';
                btn.style.fontWeight = 'bold';
                btn.style.fontSize = '1.6em';
                btn.style.padding = '20px 40px';
                btn.style.transition = 'transform 0.2s';
                refreshFound = true;
            }
            if (btn.textContent.includes('Clear Players/Scores')) {
                btn.style.background = 'linear-gradient(90deg, #FF6B00 0%, #FF8C00 100%)';
                btn.style.color = 'white';
                btn.style.border = 'none';
                btn.style.borderRadius = '8px';
                btn.style.fontWeight = 'bold';
                btn.style.fontSize = '1.6em';
                btn.style.padding = '20px 40px';
                btn.style.transition = 'transform 0.2s';
                clearFound = true;
            }
        });
        
        return refreshFound && clearFound;
    }
    
    // Try immediately
    colorButtons();
    
    // Retry after short delay
    setTimeout(colorButtons, 100);
    setTimeout(colorButtons, 300);
    setTimeout(colorButtons, 600);
    setTimeout(colorButtons, 1000);
    setTimeout(colorButtons, 2000);
    
    // Set up observer for future changes
    const observer = new MutationObserver(() => {
        colorButtons();
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)
    
    st.divider()
    
    # Format and Match Type Selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏁 Series Format**")
        best_of = st.radio("Choose format", ["Best of 3", "Best of 5"], horizontal=True, label_visibility="collapsed")
        bo_num = 3 if best_of == "Best of 3" else 5
        max_games = bo_num
    
    with col2:
        st.markdown("**👥 Match Type**")
        match_type = st.radio("Choose type", ["1v1", "2v2", "3v3"], horizontal=True, label_visibility="collapsed")
        num_players = int(match_type[0])
    
    # Initialize reset counter
    if 'reset_counter' not in st.session_state:
        st.session_state.reset_counter = 0
    
    # Get current series
    c.execute("SELECT series_number, match_number, best_of FROM matches ORDER BY series_number DESC, match_number DESC LIMIT 1")
    last_match = c.fetchone()
    
    if last_match:
        last_series, last_match_num, last_bo = last_match
        c.execute(f"SELECT COUNT(*) FROM matches WHERE series_number = ? AND winner IS NOT NULL", (last_series,))
        wins_in_series = c.fetchone()[0]
        
        if last_bo == 3:
            wins_needed = 2
        else:
            wins_needed = 3
        
        if wins_in_series >= wins_needed:
            current_series = last_series + 1
        else:
            current_series = last_series
    else:
        current_series = 1
    
    # Series header
    st.markdown(f'<div class="series-header">Series {current_series} - {best_of}</div>', unsafe_allow_html=True)
    
    # Initialize session state for player selections - always use defaults
    if 'series_team1' not in st.session_state:
        st.session_state.series_team1 = ["Choose Player"] * num_players
    
    if 'series_team2' not in st.session_state:
        st.session_state.series_team2 = ["Choose Player"] * num_players
    
    # Check if we need to reset due to match type change
    if len(st.session_state.series_team1) != num_players:
        st.session_state.reset_counter += 1
        st.session_state.series_team1 = ["Choose Player"] * num_players
        st.session_state.series_team2 = ["Choose Player"] * num_players
    
    elif len(st.session_state.series_team2) != num_players:
        st.session_state.reset_counter += 1
        st.session_state.series_team1 = ["Choose Player"] * num_players
        st.session_state.series_team2 = ["Choose Player"] * num_players
    
    # STEP 1: SELECT TEAMS
    st.markdown("## Step 1: Select Your Teams")
    
    col1, col2 = st.columns(2)
    
    player_options = ["Choose Player"] + PLAYERS
    
    with col1:
        st.markdown('<div style="text-align: center; font-size: 1.3em; color: #FF6B00; font-weight: bold; margin-bottom: 15px;">TEAM 1</div>', unsafe_allow_html=True)
        for i in range(num_players):
            try:
                current_index = player_options.index(st.session_state.series_team1[i])
            except (ValueError, IndexError):
                current_index = 0
            st.session_state.series_team1[i] = st.selectbox(f"Player {i+1}", player_options, index=current_index, key=f"team1_p{i}_r{st.session_state.reset_counter}")
    
    with col2:
        st.markdown('<div style="text-align: center; font-size: 1.3em; color: #1E90FF; font-weight: bold; margin-bottom: 15px;">TEAM 2</div>', unsafe_allow_html=True)
        for i in range(num_players):
            try:
                current_index = player_options.index(st.session_state.series_team2[i])
            except (ValueError, IndexError):
                current_index = 0
            st.session_state.series_team2[i] = st.selectbox(f"Player {i+1}", player_options, index=current_index, key=f"team2_p{i}_r{st.session_state.reset_counter}")
    
    st.divider()
    
    # STEP 2: ADD STATS FOR EACH GAME
    st.markdown("## Step 2: Add Stats for Each Game")
    
    series_games = []
    
    for game_num in range(1, max_games + 1):
        with st.expander(f"Game {game_num}", expanded=(game_num==1)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div style="text-align: center; font-size: 1.2em; color: #FF6B00; font-weight: bold; margin-bottom: 10px;">TEAM 1</div>', unsafe_allow_html=True)
                team1_stats = []
                
                for i in range(num_players):
                    player_name = st.session_state.series_team1[i]
                    st.markdown(f"**{player_name}**")
                    
                    stat_col1, stat_col2, stat_col3 = st.columns(3)
                    with stat_col1:
                        score = st.number_input(f"Score", min_value=0, key=f"g{game_num}_t1_s{i}_r{st.session_state.reset_counter}")
                        goals = st.number_input(f"Goals", min_value=0, key=f"g{game_num}_t1_g{i}_r{st.session_state.reset_counter}")
                    with stat_col2:
                        assists = st.number_input(f"Assists", min_value=0, key=f"g{game_num}_t1_a{i}_r{st.session_state.reset_counter}")
                        saves = st.number_input(f"Saves", min_value=0, key=f"g{game_num}_t1_sv{i}_r{st.session_state.reset_counter}")
                    with stat_col3:
                        shots = st.number_input(f"Shots", min_value=0, key=f"g{game_num}_t1_sh{i}_r{st.session_state.reset_counter}")
                    
                    team1_stats.append({"player": player_name, "score": score, "goals": goals, "assists": assists, "saves": saves, "shots": shots})
                    st.markdown("---")
            
            with col2:
                st.markdown('<div style="text-align: center; font-size: 1.2em; color: #1E90FF; font-weight: bold; margin-bottom: 10px;">TEAM 2</div>', unsafe_allow_html=True)
                team2_stats = []
                
                for i in range(num_players):
                    player_name = st.session_state.series_team2[i]
                    st.markdown(f"**{player_name}**")
                    
                    stat_col1, stat_col2, stat_col3 = st.columns(3)
                    with stat_col1:
                        score = st.number_input(f"Score", min_value=0, key=f"g{game_num}_t2_s{i}_r{st.session_state.reset_counter}")
                        goals = st.number_input(f"Goals", min_value=0, key=f"g{game_num}_t2_g{i}_r{st.session_state.reset_counter}")
                    with stat_col2:
                        assists = st.number_input(f"Assists", min_value=0, key=f"g{game_num}_t2_a{i}_r{st.session_state.reset_counter}")
                        saves = st.number_input(f"Saves", min_value=0, key=f"g{game_num}_t2_sv{i}_r{st.session_state.reset_counter}")
                    with stat_col3:
                        shots = st.number_input(f"Shots", min_value=0, key=f"g{game_num}_t2_sh{i}_r{st.session_state.reset_counter}")
                    
                    team2_stats.append({"player": player_name, "score": score, "goals": goals, "assists": assists, "saves": saves, "shots": shots})
                    st.markdown("---")
            
            # Winner selection - show actual player names
            team1_display = " + ".join(st.session_state.series_team1)
            team2_display = " + ".join(st.session_state.series_team2)
            
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                st.markdown("**Who won this game?**")
            with col_w2:
                winner = st.radio("Select winner", [team1_display, team2_display], horizontal=True, key=f"g{game_num}_winner_r{st.session_state.reset_counter}", label_visibility="collapsed")
            winner_num = 1 if winner == team1_display else 2
            
            series_games.append({
                "game_num": game_num,
                "team1_players": st.session_state.series_team1,
                "team2_players": st.session_state.series_team2,
                "team1_stats": team1_stats,
                "team2_stats": team2_stats,
                "winner": winner_num
            })
    
    st.divider()
    
    # Submit button
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        submit_clicked = st.button("🎮 LOG SERIES 🎮", key="submit_series", use_container_width=True)
    
    # If submit clicked, ask for user
    if submit_clicked:
        st.session_state.confirm_submit = True
    
    if st.session_state.get("confirm_submit", False):
        st.divider()
        st.markdown("### 👤 Who is entering this game?")
        confirming_user = st.selectbox("Select your name", PLAYERS, key="confirm_user_selectbox")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirm", use_container_width=True, key="confirm_btn"):
                # Validate games
                all_valid = True
                error_msg = ""
                
                # Check if all players are selected (not "Choose Player")
                if "Choose Player" in st.session_state.series_team1 or "Choose Player" in st.session_state.series_team2:
                    all_valid = False
                    error_msg = "Please select all players before logging the series!"
                
                for game in series_games:
                    if not all_valid:
                        break
                    # Check for duplicate players
                    all_players_in_game = game["team1_players"] + game["team2_players"]
                    if len(all_players_in_game) != len(set(all_players_in_game)):
                        all_valid = False
                        error_msg = f"Game {game['game_num']}: Each player can only be on one team!"
                        break
                
                if not all_valid:
                    st.error(error_msg)
                else:
                    # Insert all games
                    for game in series_games:
                        t1_total = sum(p["score"] for p in game["team1_stats"])
                        t2_total = sum(p["score"] for p in game["team2_stats"])
                        
                        c.execute("""INSERT INTO matches 
                                    (series_number, match_number, best_of, timestamp, team1_players, team2_players, team1_score, team2_score, winner)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                 (current_series, game["game_num"], bo_num, datetime.now().isoformat(), 
                                  ",".join(game["team1_players"]), ",".join(game["team2_players"]), 
                                  t1_total, t2_total, game["winner"]))
                        
                        match_id = c.lastrowid
                        
                        # Insert player stats for team 1
                        for i, stat in enumerate(game["team1_stats"]):
                            c.execute("""INSERT INTO player_stats (match_id, player_name, team, score, goals, assists, saves, shots)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                     (match_id, stat["player"], 1, int(stat["score"]), int(stat["goals"]), int(stat["assists"]), int(stat["saves"]), int(stat["shots"])))
                        
                        # Insert player stats for team 2
                        for i, stat in enumerate(game["team2_stats"]):
                            c.execute("""INSERT INTO player_stats (match_id, player_name, team, score, goals, assists, saves, shots)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                     (match_id, stat["player"], 2, int(stat["score"]), int(stat["goals"]), int(stat["assists"]), int(stat["saves"]), int(stat["shots"])))
                    
                    conn.commit()
                    
                    # Log the action
                    c.execute("""INSERT INTO activity_log (timestamp, user_name, action)
                                VALUES (?, ?, ?)""",
                             (datetime.now().isoformat(), confirming_user, f"entered a game"))
                    conn.commit()
                    
                    # Reset by incrementing counter - forces all widgets to get new keys
                    st.session_state.reset_counter += 1
                    st.session_state.series_team1 = ["Choose Player"] * num_players
                    st.session_state.series_team2 = ["Choose Player"] * num_players
                    st.session_state.confirm_submit = False
                    
                    st.balloons()
                    st.success(f"✅ Series {current_series} Logged by {confirming_user}! 🎉")
                    st.rerun()
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True, key="cancel_btn"):
                st.session_state.confirm_submit = False
                st.rerun()

# ============ TAB 2: SERIES HISTORY ============
with tab2:
    if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_tab2"):
        st.rerun()
    
    # JavaScript to color refresh button blue
    st.markdown("""
<script>
    function colorRefreshButton() {
        let buttons = document.querySelectorAll('button');
        buttons.forEach(btn => {
            if (btn.textContent.includes('Refresh Data')) {
                btn.style.background = 'linear-gradient(90deg, #1E90FF 0%, #4169E1 100%)';
                btn.style.color = 'white';
                btn.style.border = 'none';
                btn.style.borderRadius = '8px';
                btn.style.fontWeight = 'bold';
                btn.style.fontSize = '1.6em';
                btn.style.padding = '20px 40px';
                btn.style.transition = 'transform 0.2s';
            }
        });
    }
    
    colorRefreshButton();
    setTimeout(colorRefreshButton, 100);
    setTimeout(colorRefreshButton, 300);
    setTimeout(colorRefreshButton, 600);
    
    const observer = new MutationObserver(colorRefreshButton);
    observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)
    
    st.divider()
    c.execute("""SELECT series_number, best_of, match_number FROM matches 
                 GROUP BY series_number ORDER BY series_number DESC""")
    series_list = c.fetchall()
    
    if not series_list:
        st.info("📭 No matches logged yet")
    else:
        # Organize series by match type
        series_by_type = {"1v1": [], "2v2": [], "3v3": []}
        
        for series_num, bo, last_match in series_list:
            # Get first match to determine match type
            c.execute("""SELECT team1_players FROM matches 
                         WHERE series_number = ? ORDER BY match_number LIMIT 1""", (series_num,))
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
                
                series_by_type[match_type].append((series_num, bo, last_match))
        
        # Display by match type
        for match_type in ["1v1", "2v2", "3v3"]:
            st.markdown(f"## {match_type}")
            
            if not series_by_type[match_type]:
                st.info(f"📭 No {match_type} series yet")
            else:
                for series_num, bo, last_match in series_by_type[match_type]:
                    # Get player info
                    c.execute("""SELECT team1_players, team2_players FROM matches 
                                 WHERE series_number = ? ORDER BY match_number LIMIT 1""", (series_num,))
                    first_match = c.fetchone()
                    
                    if first_match:
                        t1_players = first_match[0]
                        t2_players = first_match[1]
                        player_info = f"({t1_players} vs {t2_players})"
                    else:
                        player_info = ""
                    
                    col1, col2 = st.columns([0.9, 0.1])
                    with col1:
                        expander = st.expander(f"📊 Series {series_num} - Best of {bo} {player_info}", expanded=False)
                    with col2:
                        if st.button("🗑️", key=f"delete_series_{series_num}", help="Delete this series"):
                            st.session_state.confirm_delete = True
                            st.session_state.delete_series_num = series_num
                    
                    # Show delete confirmation dialog
                    if st.session_state.get("confirm_delete", False) and st.session_state.get("delete_series_num") == series_num:
                        st.divider()
                        st.markdown(f"### 👤 Who is deleting Series {series_num}?")
                        deleting_user = st.selectbox("Select your name", PLAYERS, key=f"delete_user_{series_num}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Confirm Delete", use_container_width=True, key=f"confirm_delete_{series_num}"):
                                c.execute("DELETE FROM player_stats WHERE match_id IN (SELECT id FROM matches WHERE series_number = ?)", (series_num,))
                                c.execute("DELETE FROM matches WHERE series_number = ?", (series_num,))
                                
                                # Log the deletion
                                c.execute("""INSERT INTO activity_log (timestamp, user_name, action)
                                            VALUES (?, ?, ?)""",
                                         (datetime.now().isoformat(), deleting_user, f"deleted a game"))
                                
                                conn.commit()
                                st.session_state.confirm_delete = False
                                st.session_state.delete_series_num = None
                                st.success(f"Series {series_num} deleted by {deleting_user}!")
                                st.rerun()
                        
                        with col2:
                            if st.button("❌ Cancel", use_container_width=True, key=f"cancel_delete_{series_num}"):
                                st.session_state.confirm_delete = False
                                st.session_state.delete_series_num = None
                                st.rerun()
                    
                    with expander:
                        c.execute("""SELECT * FROM matches WHERE series_number = ? ORDER BY match_number""", (series_num,))
                        matches = c.fetchall()
                        
                        for match in matches:
                            match_id, sn, mn, b, ts, t1p, t2p, t1s, t2s, winner = match
                            winner_text = "Team 1 Won" if winner == 1 else "Team 2 Won" if winner == 2 else "Pending"
                            
                            st.markdown(f"**Match {mn}: {winner_text} ({t1s} - {t2s})**")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown('<div style="text-align: center; font-size: 1.1em; color: #FF6B00; font-weight: bold;">TEAM 1</div>', unsafe_allow_html=True)
                                c.execute("""SELECT player_name, score, goals, assists, saves, shots FROM player_stats 
                                             WHERE match_id = ? AND team = 1""", (match_id,))
                                for row in c.fetchall():
                                    st.markdown(f"**{row[0]}** · Score: {row[1]} Goals: {row[2]} Assists: {row[3]} Saves: {row[4]} Shots: {row[5]}")
                            
                            with col2:
                                st.markdown('<div style="text-align: center; font-size: 1.1em; color: #1E90FF; font-weight: bold;">TEAM 2</div>', unsafe_allow_html=True)
                                c.execute("""SELECT player_name, score, goals, assists, saves, shots FROM player_stats 
                                             WHERE match_id = ? AND team = 2""", (match_id,))
                                for row in c.fetchall():
                                    st.markdown(f"**{row[0]}** · Score: {row[1]} Goals: {row[2]} Assists: {row[3]} Saves: {row[4]} Shots: {row[5]}")
                            
                            st.divider()
                        
                        st.divider()
                        
                        # Series totals
                        st.markdown("### Series Totals")
                        c.execute("""SELECT player_name, SUM(score), SUM(goals), SUM(assists), SUM(saves), SUM(shots) 
                                     FROM player_stats 
                                     WHERE match_id IN (SELECT id FROM matches WHERE series_number = ?)
                                     GROUP BY player_name
                                     ORDER BY SUM(score) DESC""", (series_num,))
                        
                        for row in c.fetchall():
                            st.markdown(f"**{row[0]}** · Score: {row[1]} Goals: {row[2]} Assists: {row[3]} Saves: {row[4]} Shots: {row[5]}")
            
            st.divider()
    
    # Activity Log
    st.markdown("## 📋 Activity Log")
    c.execute("""SELECT timestamp, user_name, action FROM activity_log ORDER BY timestamp DESC LIMIT 50""")
    logs = c.fetchall()
    
    if not logs:
        st.info("📭 No activity yet")
    else:
        for timestamp, user_name, action in logs:
            # Format timestamp to be more readable
            ts = datetime.fromisoformat(timestamp)
            ts_str = ts.strftime("%m/%d %I:%M %p")
            st.markdown(f"**{user_name}** {action} · {ts_str}")
    
    st.divider()

# ============ TAB 3: PLAYER STATS ============
with tab3:
    if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_tab3"):
        st.rerun()
    
    # JavaScript to color refresh button blue
    st.markdown("""
<script>
    function colorRefreshButton() {
        let buttons = document.querySelectorAll('button');
        buttons.forEach(btn => {
            if (btn.textContent.includes('Refresh Data')) {
                btn.style.background = 'linear-gradient(90deg, #1E90FF 0%, #4169E1 100%)';
                btn.style.color = 'white';
                btn.style.border = 'none';
                btn.style.borderRadius = '8px';
                btn.style.fontWeight = 'bold';
                btn.style.fontSize = '1.6em';
                btn.style.padding = '20px 40px';
                btn.style.transition = 'transform 0.2s';
            }
        });
    }
    
    colorRefreshButton();
    setTimeout(colorRefreshButton, 100);
    setTimeout(colorRefreshButton, 300);
    setTimeout(colorRefreshButton, 600);
    
    const observer = new MutationObserver(colorRefreshButton);
    observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)
    
    st.divider()
    c.execute("""SELECT DISTINCT player_name FROM player_stats ORDER BY player_name""")
    all_players = [row[0] for row in c.fetchall()]
    
    if not all_players:
        st.info("📭 No player data yet")
    else:
        stats_data = []
        
        for player in all_players:
            # Count wins
            c.execute("""SELECT COUNT(*) FROM matches WHERE 
                         (team1_players LIKE ? AND winner = 1) OR
                         (team2_players LIKE ? AND winner = 2)""", 
                     (f"%{player}%", f"%{player}%"))
            wins = c.fetchone()[0]
            
            c.execute("""SELECT COUNT(*) FROM matches WHERE 
                         (team1_players LIKE ? AND winner = 2) OR
                         (team2_players LIKE ? AND winner = 1)""", 
                     (f"%{player}%", f"%{player}%"))
            losses = c.fetchone()[0]
            
            games = wins + losses
            
            if games > 0:
                win_pct = (wins / games) * 100
            else:
                win_pct = 0
            
            # Get totals
            c.execute("""SELECT SUM(score), SUM(goals), SUM(assists), SUM(saves), SUM(shots) FROM player_stats 
                         WHERE player_name = ?""", (player,))
            score, goals, assists, saves, shots = c.fetchone()
            score = score or 0
            goals = goals or 0
            assists = assists or 0
            saves = saves or 0
            shots = shots or 0
            
            # Calculate averages
            avg_score = score / games if games > 0 else 0
            avg_goals = goals / games if games > 0 else 0
            avg_assists = assists / games if games > 0 else 0
            avg_saves = saves / games if games > 0 else 0
            avg_shots = shots / games if games > 0 else 0
            
            stats_data.append({
                "player": player,
                "wins": wins,
                "losses": losses,
                "games": games,
                "win_pct": f"{win_pct:.1f}%",
                "score": score,
                "goals": goals,
                "assists": assists,
                "saves": saves,
                "shots": shots,
                "avg_score": avg_score,
                "avg_goals": avg_goals,
                "avg_assists": avg_assists,
                "avg_saves": avg_saves,
                "avg_shots": avg_shots
            })
        
        # Display wins/losses table
        wins_data = []
        for stat in stats_data:
            wins_data.append({
                "🎮 Player": stat["player"],
                "🏆 Wins": stat["wins"],
                "💔 Losses": stat["losses"],
                "📊 Games": stat["games"],
                "📈 Win %": stat["win_pct"]
            })
        
        df_wins = pd.DataFrame(wins_data)
        df_wins = df_wins.sort_values("🏆 Wins", ascending=False)
        st.dataframe(df_wins, use_container_width=True, hide_index=True)
        
        st.divider()
        st.markdown("## Career Totals")
        
        # Display career totals
        totals_data = []
        for stat in sorted(stats_data, key=lambda x: x["wins"], reverse=True):
            totals_data.append({
                "🎮 Player": stat["player"],
                "🎯 Score": stat["score"],
                "⚽ Goals": stat["goals"],
                "🎁 Assists": stat["assists"],
                "🛡️ Saves": stat["saves"],
                "🔫 Shots": stat["shots"]
            })
        
        df_totals = pd.DataFrame(totals_data)
        st.dataframe(df_totals, use_container_width=True, hide_index=True)
        
        st.divider()
        st.markdown("## Per-Game Averages")
        
        # Display averages
        avg_data = []
        for stat in sorted(stats_data, key=lambda x: x["wins"], reverse=True):
            avg_data.append({
                "🎮 Player": stat["player"],
                "📍 Avg Score": f"{stat['avg_score']:.1f}",
                "⚽ Avg Goals": f"{stat['avg_goals']:.2f}",
                "🎁 Avg Assists": f"{stat['avg_assists']:.2f}",
                "🛡️ Avg Saves": f"{stat['avg_saves']:.2f}",
                "🔫 Avg Shots": f"{stat['avg_shots']:.2f}"
            })
        
        df_avg = pd.DataFrame(avg_data)
        st.dataframe(df_avg, use_container_width=True, hide_index=True)

# ============ TAB 4: TEAMS ============
with tab4:
    if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_tab4"):
        st.rerun()
    
    # JavaScript to color refresh button blue
    st.markdown("""
<script>
    function colorRefreshButton() {
        let buttons = document.querySelectorAll('button');
        buttons.forEach(btn => {
            if (btn.textContent.includes('Refresh Data')) {
                btn.style.background = 'linear-gradient(90deg, #1E90FF 0%, #4169E1 100%)';
                btn.style.color = 'white';
                btn.style.border = 'none';
                btn.style.borderRadius = '8px';
                btn.style.fontWeight = 'bold';
                btn.style.fontSize = '1.6em';
                btn.style.padding = '20px 40px';
                btn.style.transition = 'transform 0.2s';
            }
        });
    }
    
    colorRefreshButton();
    setTimeout(colorRefreshButton, 100);
    setTimeout(colorRefreshButton, 300);
    setTimeout(colorRefreshButton, 600);
    
    const observer = new MutationObserver(colorRefreshButton);
    observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)
    
    st.divider()
    c.execute("""SELECT id, team1_players, team2_players, winner FROM matches""")
    all_matches = c.fetchall()
    
    if not all_matches:
        st.info("📭 No partnership data yet")
    else:
        # Organize by match type
        partnerships_by_type = {
            "2v2": defaultdict(lambda: {"wins": 0, "losses": 0}),
            "3v3": defaultdict(lambda: {"wins": 0, "losses": 0})
        }
        matchups_by_type = {
            "2v2": defaultdict(lambda: defaultdict(lambda: {"wins": 0, "losses": 0})),
            "3v3": defaultdict(lambda: defaultdict(lambda: {"wins": 0, "losses": 0}))
        }
        
        for match_id, t1, t2, winner in all_matches:
            t1_list = t1.split(",")
            t2_list = t2.split(",")
            
            # Determine match type
            if len(t1_list) == 1:
                match_type = "1v1"
            elif len(t1_list) == 2:
                match_type = "2v2"
            else:
                match_type = "3v3"
            
            # Only track partnerships for 2v2 and 3v3
            if match_type == "1v1":
                continue
            
            partnerships = partnerships_by_type[match_type]
            matchups = matchups_by_type[match_type]
            
            # Get all partnerships for team 1 and team 2
            if match_type == "2v2":
                # For 2v2: track 2-player pairs
                t1_pairs = []
                for i in range(len(t1_list)):
                    for j in range(i+1, len(t1_list)):
                        pair = tuple(sorted([t1_list[i], t1_list[j]]))
                        t1_pairs.append(pair)
                        if winner == 1:
                            partnerships[pair]["wins"] += 1
                        else:
                            partnerships[pair]["losses"] += 1
                
                t2_pairs = []
                for i in range(len(t2_list)):
                    for j in range(i+1, len(t2_list)):
                        pair = tuple(sorted([t2_list[i], t2_list[j]]))
                        t2_pairs.append(pair)
                        if winner == 2:
                            partnerships[pair]["wins"] += 1
                        else:
                            partnerships[pair]["losses"] += 1
            
            elif match_type == "3v3":
                # For 3v3: track full 3-player teams
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
            
            # Track matchups between partnerships from each partnership's perspective
            for t1_pair in t1_pairs:
                for t2_pair in t2_pairs:
                    if winner == 1:
                        matchups[t1_pair][t2_pair]["wins"] += 1
                        matchups[t2_pair][t1_pair]["losses"] += 1
                    else:
                        matchups[t1_pair][t2_pair]["losses"] += 1
                        matchups[t2_pair][t1_pair]["wins"] += 1
        
        # Display by match type
        for match_type in ["2v2", "3v3"]:
            partnerships = partnerships_by_type[match_type]
            matchups = matchups_by_type[match_type]
            
            st.markdown(f"## {match_type} Teams")
            
            if not partnerships:
                st.info(f"📭 No {match_type} team data yet")
            else:
                part_data = []
                for partnership_tuple, record in partnerships.items():
                    total = record["wins"] + record["losses"]
                    win_pct = (record["wins"] / total) * 100 if total > 0 else 0
                    # Format display string based on number of players
                    display = " + ".join(partnership_tuple)
                    part_data.append({
                        "partnership": partnership_tuple,
                        "display": display,
                        "wins": record["wins"],
                        "losses": record["losses"],
                        "total": total,
                        "win_pct": win_pct
                    })
                
                # Sort by wins descending
                part_data.sort(key=lambda x: x["wins"], reverse=True)
                
                # Display partnerships with matchup records
                for partnership_info in part_data:
                    part_tuple = partnership_info["partnership"]
                    total = partnership_info["total"]
                    win_pct = partnership_info["win_pct"]
                    
                    # Create expander for this partnership
                    with st.expander(f"🤝 {partnership_info['display']} · {partnership_info['wins']}-{partnership_info['losses']} ({win_pct:.1f}%)", expanded=False):
                        st.markdown(f"**Overall: {partnership_info['wins']} Wins · {partnership_info['losses']} Losses · {win_pct:.1f}% Win Rate**")
                        st.divider()
                        st.markdown("**Head-to-Head vs Other Partnerships:**")
                        
                        # Get all matchups for this partnership
                        matchup_records = []
                        if part_tuple in matchups:
                            for opponent_tuple, record in matchups[part_tuple].items():
                                h2h_total = record["wins"] + record["losses"]
                                h2h_pct = (record["wins"] / h2h_total) * 100 if h2h_total > 0 else 0
                                opponent_display = " + ".join(opponent_tuple)
                                matchup_records.append({
                                    "opponent": opponent_display,
                                    "wins": record["wins"],
                                    "losses": record["losses"],
                                    "total": h2h_total,
                                    "pct": h2h_pct
                                })
                        
                        if matchup_records:
                            # Sort by wins descending
                            matchup_records.sort(key=lambda x: x["wins"], reverse=True)
                            
                            for matchup in matchup_records:
                                st.markdown(f"vs **{matchup['opponent']}** · {matchup['wins']}-{matchup['losses']} ({matchup['pct']:.1f}%)")
                        else:
                            st.markdown("*No matchup data yet*")
                
                st.divider()

conn.close()
