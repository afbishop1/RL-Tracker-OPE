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
        max_games = bo_num
    
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
        else:
            current_series = last_series
    else:
        current_series = 1
    
    # Series header
    st.markdown(f'<div style="background: linear-gradient(135deg, #CC5500 0%, #DD6600 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; font-size: 1.6em; font-weight: bold; margin: 20px 0;">Series {current_series} - {best_of}</div>', unsafe_allow_html=True)
    
    # Initialize session state for player selections
    if 'series_team1' not in st.session_state:
        st.session_state.series_team1 = [PLAYERS[0]] * num_players
    if 'series_team2' not in st.session_state:
        st.session_state.series_team2 = [PLAYERS[0]] * num_players
    
    # STEP 1: SELECT TEAMS
    st.markdown("## Step 1: Select Your Teams")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div style="text-align: center; font-size: 1.3em; color: #FF6B00; font-weight: bold; margin-bottom: 15px;">🟠 TEAM 1 🟠</div>', unsafe_allow_html=True)
        for i in range(num_players):
            st.session_state.series_team1[i] = st.selectbox(f"Player {i+1}", PLAYERS, index=PLAYERS.index(st.session_state.series_team1[i]), key=f"team1_p{i}")
    
    with col2:
        st.markdown('<div style="text-align: center; font-size: 1.3em; color: #1E90FF; font-weight: bold; margin-bottom: 15px;">🔵 TEAM 2 🔵</div>', unsafe_allow_html=True)
        for i in range(num_players):
            st.session_state.series_team2[i] = st.selectbox(f"Player {i+1}", PLAYERS, index=PLAYERS.index(st.session_state.series_team2[i]), key=f"team2_p{i}")
    
    st.divider()
    
    # STEP 2: ADD STATS FOR EACH GAME
    st.markdown("## Step 2: Add Stats for Each Game")
    
    series_games = []
    
    for game_num in range(1, max_games + 1):
        with st.expander(f"Game {game_num}", expanded=(game_num==1)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div style="text-align: center; font-size: 1.2em; color: #FF6B00; font-weight: bold; margin-bottom: 10px;">🟠 TEAM 1</div>', unsafe_allow_html=True)
                team1_stats = []
                
                for i in range(num_players):
                    player_name = st.session_state.series_team1[i]
                    st.markdown(f"**{player_name}**")
                    
                    stat_col1, stat_col2 = st.columns(2)
                    with stat_col1:
                        score = st.number_input(f"Score", min_value=0, key=f"g{game_num}_t1_s{i}")
                        goals = st.number_input(f"Goals", min_value=0, key=f"g{game_num}_t1_g{i}")
                    with stat_col2:
                        assists = st.number_input(f"Assists", min_value=0, key=f"g{game_num}_t1_a{i}")
                        saves = st.number_input(f"Saves", min_value=0, key=f"g{game_num}_t1_sv{i}")
                    
                    team1_stats.append({"player": player_name, "score": score, "goals": goals, "assists": assists, "saves": saves})
                    st.markdown("---")
            
            with col2:
                st.markdown('<div style="text-align: center; font-size: 1.2em; color: #1E90FF; font-weight: bold; margin-bottom: 10px;">🔵 TEAM 2</div>', unsafe_allow_html=True)
                team2_stats = []
                
                for i in range(num_players):
                    player_name = st.session_state.series_team2[i]
                    st.markdown(f"**{player_name}**")
                    
                    stat_col1, stat_col2 = st.columns(2)
                    with stat_col1:
                        score = st.number_input(f"Score", min_value=0, key=f"g{game_num}_t2_s{i}")
                        goals = st.number_input(f"Goals", min_value=0, key=f"g{game_num}_t2_g{i}")
                    with stat_col2:
                        assists = st.number_input(f"Assists", min_value=0, key=f"g{game_num}_t2_a{i}")
                        saves = st.number_input(f"Saves", min_value=0, key=f"g{game_num}_t2_sv{i}")
                    
                    team2_stats.append({"player": player_name, "score": score, "goals": goals, "assists": assists, "saves": saves})
                    st.markdown("---")
            
            # Winner selection
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                st.markdown("**Who won this game?**")
            with col_w2:
                winner = st.radio("Select winner", ["Team 1", "Team 2"], horizontal=True, key=f"g{game_num}_winner", label_visibility="collapsed")
            winner_num = 1 if winner == "Team 1" else 2
            
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
    if st.button("🎮 LOG SERIES 🎮", key="submit_series", use_container_width=True):
        # Validate games
        all_valid = True
        error_msg = ""
        
        for game in series_games:
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
                    c.execute("""INSERT INTO player_stats (match_id, player_name, team, score, goals, assists, saves)
                                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                             (match_id, stat["player"], 1, stat["score"], stat["goals"], stat["assists"], stat["saves"]))
                
                # Insert player stats for team 2
                for i, stat in enumerate(game["team2_stats"]):
                    c.execute("""INSERT INTO player_stats (match_id, player_name, team, score, goals, assists, saves)
                                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                             (match_id, stat["player"], 2, stat["score"], stat["goals"], stat["assists"], stat["saves"]))
            
            conn.commit()
            st.balloons()
            st.success(f"✅ Series {current_series} Logged! 🎉")
            # Clear session state for next series
            st.session_state.series_team1 = None
            st.session_state.series_team2 = None
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
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                expander = st.expander(f"📊 Series {series_num} - Best of {bo}", expanded=False)
            with col2:
                if st.button("🗑️", key=f"delete_series_{series_num}", help="Delete this series"):
                    c.execute("DELETE FROM player_stats WHERE match_id IN (SELECT id FROM matches WHERE series_number = ?)", (series_num,))
                    c.execute("DELETE FROM matches WHERE series_number = ?", (series_num,))
                    conn.commit()
                    st.success(f"Series {series_num} deleted!")
                    st.rerun()
            
            with expander:
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
