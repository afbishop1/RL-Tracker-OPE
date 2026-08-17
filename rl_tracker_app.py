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
                score = st.number_input(f"Score", min_value=0, key=f"t2_s{i}", label_visibility="collapsed")
                goals = st.number_input(f"Goals", min_value=0, key=f"t2_g{i}", label_visibility="collapsed")
            with stat_col2:
                assists = st.number_input(f"Assists", min_value=0, key=f"t2_a{i}", label_visibility="collapsed")
                saves = st.number_input(f"Saves", min_value=0, key=f"t2_sv{i}", label_visibility="collapsed")
            
            st.markdown('</div>', unsafe_allow_html=True)
            team2_stats.append({"player": player, "score": score, "goals": goals, "assists": assists, "saves": saves})
    
    st.divider()
    
    # Submit button
    if st.button("🎮 LOG MATCH 🎮", key="submit_match", use_container_width=True):
        # Calculate team scores
        team1_total = sum(p["score"] for p in team1_stats)
        team2_total = sum(p["score"] for p in team2_stats)
        
        if team1_total == team2_total:
            st.error("Match cannot be a tie!")
        elif len(set(team1_players + team2_players)) != num_players * 2:
            st.error("Each player can only be on one team!")
        else:
            winner = 1 if team1_total > team2_total else 2
            
            # Insert match
            c.execute("""INSERT INTO matches 
                        (series_number, match_number, best_of, timestamp, team1_players, team2_players, team1_score, team2_score, winner)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     (current_series, current_match, bo_num, datetime.now().isoformat(), 
                      ",".join(team1_players), ",".join(team2_players), 
                      team1_total, team2_total, winner))
            
            match_id = c.lastrowid
            
            # Insert player stats
            for i, stat in enumerate(team1_stats):
                c.execute("""INSERT INTO player_stats (match_id, player_name, team, score, goals, assists, saves)
                            VALUES (?, ?, ?, ?, ?, ?, ?)""",
                         (match_id, stat["player"], 1, stat["score"], stat["goals"], stat["assists"], stat["saves"]))
            
            for i, stat in enumerate(team2_stats):
                c.execute("""INSERT INTO player_stats (match_id, player_name, team, score, goals, assists, saves)
                            VALUES (?, ?, ?, ?, ?, ?, ?)""",
                         (match_id, stat["player"], 2, stat["score"], stat["goals"], stat["assists"], stat["saves"]))
            
            conn.commit()
            st.balloons()
            winner_text = "🟠 TEAM 1 🟠" if winner == 1 else "🔵 TEAM 2 🔵"
            st.success(f"✅ Match Logged! {winner_text} WINS! 🎉")
            st.rerun()

# ============ TAB 2: SERIES HISTORY ============
with tab2:
    c.execute("""SELECT series_number, best_of, match_number FROM matches 
                 GROUP BY series_number ORDER BY series_number DESC""")
    series_list = c.fetchall()
    
    if not series_list:
        st.info("📭 No matches logged yet")
    else:
        for series_num, bo, last_match in series_list:
            with st.expander(f"📊 Series {series_num} - Best of {bo}", expanded=False):
                c.execute("""SELECT * FROM matches WHERE series_number = ? ORDER BY match_number""", (series_num,))
                matches = c.fetchall()
                
                for match in matches:
                    match_id, sn, mn, b, ts, t1p, t2p, t1s, t2s, winner = match
                    winner_icon = "🟠" if winner == 1 else "🔵" if winner == 2 else "⏳"
                    
                    st.markdown(f'<div class="match-card">', unsafe_allow_html=True)
                    st.markdown(f"**{winner_icon} Match {mn}: {t1s} vs {t2s}**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="team-card">', unsafe_allow_html=True)
                        st.markdown("**🟠 Team 1**")
                        c.execute("""SELECT player_name, score, goals, assists, saves FROM player_stats 
                                     WHERE match_id = ? AND team = 1""", (match_id,))
                        for row in c.fetchall():
                            st.markdown(f"  **{row[0]}** · {row[1]}🎯 {row[2]}⚽ {row[3]}🎁 {row[4]}🛡️")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="team-card team-2">', unsafe_allow_html=True)
                        st.markdown("**🔵 Team 2**")
                        c.execute("""SELECT player_name, score, goals, assists, saves FROM player_stats 
                                     WHERE match_id = ? AND team = 2""", (match_id,))
                        for row in c.fetchall():
                            st.markdown(f"  **{row[0]}** · {row[1]}🎯 {row[2]}⚽ {row[3]}🎁 {row[4]}🛡️")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.divider()
                
                # Series totals
                st.markdown("### 📈 Series Totals")
                c.execute("""SELECT player_name, SUM(score), SUM(goals), SUM(assists), SUM(saves) 
                             FROM player_stats 
                             WHERE match_id IN (SELECT id FROM matches WHERE series_number = ?)
                             GROUP BY player_name
                             ORDER BY SUM(score) DESC""", (series_num,))
                
                for row in c.fetchall():
                    st.markdown(f"**{row[0]}** → {row[1]}🎯 {row[2]}⚽ {row[3]}🎁 {row[4]}🛡️")

# ============ TAB 3: PLAYER STATS ============
with tab3:
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
            c.execute("""SELECT SUM(score), SUM(goals), SUM(assists), SUM(saves) FROM player_stats 
                         WHERE player_name = ?""", (player,))
            score, goals, assists, saves = c.fetchone()
            
            stats_data.append({
                "🎮 Player": player,
                "🏆 Wins": wins,
                "💔 Losses": losses,
                "📊 Games": games,
                "📈 Win %": f"{win_pct:.1f}%",
                "🎯 Score": score or 0,
                "⚽ Goals": goals or 0,
                "🎁 Assists": assists or 0,
                "🛡️ Saves": saves or 0
            })
        
        df = pd.DataFrame(stats_data)
        df = df.sort_values("🏆 Wins", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)

# ============ TAB 4: PARTNERSHIPS ============
with tab4:
    c.execute("""SELECT id, team1_players, team2_players, winner FROM matches""")
    all_matches = c.fetchall()
    
    if not all_matches:
        st.info("📭 No partnership data yet")
    else:
        partnerships = defaultdict(lambda: {"wins": 0, "losses": 0})
        
        for match_id, t1, t2, winner in all_matches:
            t1_list = t1.split(",")
            t2_list = t2.split(",")
            
            # Track team 1 partnerships
            for i in range(len(t1_list)):
                for j in range(i+1, len(t1_list)):
                    pair = tuple(sorted([t1_list[i], t1_list[j]]))
                    if winner == 1:
                        partnerships[pair]["wins"] += 1
                    else:
                        partnerships[pair]["losses"] += 1
            
            # Track team 2 partnerships
            for i in range(len(t2_list)):
                for j in range(i+1, len(t2_list)):
                    pair = tuple(sorted([t2_list[i], t2_list[j]]))
                    if winner == 2:
                        partnerships[pair]["wins"] += 1
                    else:
                        partnerships[pair]["losses"] += 1
        
        part_data = []
        for (p1, p2), record in partnerships.items():
            total = record["wins"] + record["losses"]
            win_pct = (record["wins"] / total) * 100 if total > 0 else 0
            part_data.append({
                "🤝 Partnership": f"{p1} + {p2}",
                "🏆 Wins": record["wins"],
                "💔 Losses": record["losses"],
                "📊 Games": total,
                "📈 Win %": f"{win_pct:.1f}%"
            })
        
        df = pd.DataFrame(part_data)
        df = df.sort_values("🏆 Wins", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)

conn.close()
