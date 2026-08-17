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
    
    .player-input-card {
        background: #151b2f;
        border: 1px solid rgba(255, 107, 0, 0.3);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
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
        background: linear-gradient(90deg, var(--rl-orange) 0%, #FF8C00 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        padding: 12px 30px;
        transition: transform 0.2s;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(255, 107, 0, 0.6);
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
                  FOREIGN KEY(match_id) REFERENCES matches(id))''')
    
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

PLAYERS = ["Anthony A", "Anthony B", "Nicholas", "Jesse S", "Jesse B", "Vince", "Bucci"]

# Title
st.markdown('<div class="title-main">⚡ RL MATCH TRACKER ⚡</div>', unsafe_allow_html=True)
st.markdown("🎮 Shared · Real-time updates · OPE Gaming", unsafe_allow_html=True)
st.divider()

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Log Match", "📊 Series History", "🏆 Player Stats", "🤝 Partnerships"])

# ============ TAB 1: LOG MATCH ============
with tab1:
    # Format and Match Type Selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏁 Series Format**")
        best_of = st.radio("Choose format", ["Best of 3", "Best of 5"], horizontal=True, label_visibility="collapsed")
        bo_num = 3 if best_of == "Best of 3" else 5
    
    with col2:
        st.markdown("**👥 Match Type**")
        match_type = st.radio("Choose type", ["1v1", "2v2", "3v3"], horizontal=True, label_visibility="collapsed")
        num_players = int(match_type[0])
    
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
            current_match = 1
        else:
            current_series = last_series
            current_match = last_match_num + 1
    else:
        current_series = 1
        current_match = 1
    
    # Series header
    st.markdown(f'<div class="series-header">🔥 Series {current_series} - {best_of} - Match {current_match} 🔥</div>', unsafe_allow_html=True)
    
    # Team columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div style="text-align: center; font-size: 1.5em; color: #FF6B00; font-weight: bold; margin-bottom: 15px;">🟠 TEAM 1 🟠</div>', unsafe_allow_html=True)
        team1_players = []
        team1_stats = []
        
        for i in range(num_players):
            st.markdown(f'<div class="player-input-card">', unsafe_allow_html=True)
            player = st.selectbox(f"Player {i+1}", PLAYERS, key=f"t1_p{i}", label_visibility="collapsed")
            team1_players.append(player)
            
            # Stats in columns
            stat_col1, stat_col2 = st.columns(2)
            with stat_col1:
                score = st.number_input(f"Score", min_value=0, key=f"t1_s{i}", label_visibility="collapsed")
                goals = st.number_input(f"Goals", min_value=0, key=f"t1_g{i}", label_visibility="collapsed")
            with stat_col2:
                assists = st.number_input(f"Assists", min_value=0, key=f"t1_a{i}", label_visibility="collapsed")
                saves = st.number_input(f"Saves", min_value=0, key=f"t1_sv{i}", label_visibility="collapsed")
            
            st.markdown('</div>', unsafe_allow_html=True)
            team1_stats.append({"player": player, "score": score, "goals": goals, "assists": assists, "saves": saves})
    
    with col2:
        st.markdown('<div style="text-align: center; font-size: 1.5em; color: #1E90FF; font-weight: bold; margin-bottom: 15px;">🔵 TEAM 2 🔵</div>', unsafe_allow_html=True)
        team2_players = []
        team2_stats = []
        
        for i in range(num_players):
            st.markdown(f'<div class="player-input-card">', unsafe_allow_html=True)
            player = st.selectbox(f"Player {i+1}", PLAYERS, key=f"t2_p{i}", label_visibility="collapsed")
            team2_players.append(player)
            
            # Stats in columns
            stat_col1, stat_col2 = st.columns(2)
            with stat_col1:
                score =
