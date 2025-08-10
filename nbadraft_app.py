import streamlit as st
import requests
import random
import time

# 🏀 Get NBA player stats using balldontlie API (free, no auth required)
def get_player_stats():
    try:
        # Get current season players with stats
        url = "https://www.balldontlie.io/api/v1/stats"
        params = {
            'per_page': 100,  # Get top 100 players by usage
            'season': 2024,   # Current season
            'page': 1
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        stats = {}
        
        # Process player stats
        for stat in data.get('data', []):
            player = stat.get('player', {})
            player_name = f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
            
            if player_name and player_name not in stats:
                # Calculate averages
                games_played = stat.get('game', {}).get('id', 0)
                if games_played > 0:
                    ppg = round(stat.get('pts', 0) / games_played, 1)
                    apg = round(stat.get('ast', 0) / games_played, 1)
                    rpg = round(stat.get('reb', 0) / games_played, 1)
                    
                    stats[player_name] = {
                        'PPG': str(ppg),
                        'APG': str(apg), 
                        'RPG': str(rpg)
                    }
        
        if stats:
            return stats
        else:
            st.warning("⚠️ Could not fetch NBA stats. Using sample data instead.")
            return get_sample_player_stats()
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error fetching NBA stats: {e}")
        st.info("📊 Using sample player data instead.")
        return get_sample_player_stats()
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        st.info("📊 Using sample player data instead.")
        return get_sample_player_stats()

# 📊 Sample player data as fallback
def get_sample_player_stats():
    sample_players = {
        "LeBron James": {"PPG": "25.7", "APG": "7.3", "RPG": "7.9"},
        "Stephen Curry": {"PPG": "29.4", "APG": "6.3", "RPG": "6.1"},
        "Kevin Durant": {"PPG": "29.9", "APG": "5.5", "RPG": "7.4"},
        "Giannis Antetokounmpo": {"PPG": "31.1", "APG": "5.7", "RPG": "11.8"},
        "Nikola Jokic": {"PPG": "26.4", "APG": "8.3", "RPG": "12.4"},
        "Luka Doncic": {"PPG": "33.9", "APG": "9.2", "RPG": "9.2"},
        "Joel Embiid": {"PPG": "33.1", "APG": "4.2", "RPG": "10.2"},
        "Jayson Tatum": {"PPG": "30.1", "APG": "4.6", "RPG": "8.8"},
        "Damian Lillard": {"PPG": "25.1", "APG": "6.7", "RPG": "4.3"},
        "Anthony Davis": {"PPG": "24.7", "APG": "3.6", "RPG": "12.3"},
        "Devin Booker": {"PPG": "27.1", "APG": "5.5", "RPG": "4.5"},
        "Jimmy Butler": {"PPG": "22.9", "APG": "5.3", "RPG": "5.9"},
        "Kawhi Leonard": {"PPG": "23.8", "APG": "3.9", "RPG": "6.5"},
        "Paul George": {"PPG": "23.8", "APG": "5.1", "RPG": "6.1"},
        "Bam Adebayo": {"PPG": "20.4", "APG": "3.2", "RPG": "9.2"}
    }
    return sample_players

# 🎮 Sidebar: Game Setup
st.sidebar.header("Game Setup")
num_rounds = st.sidebar.number_input("Number of Rounds", min_value=1, max_value=100, value=6)
num_players = st.sidebar.number_input("Number of Participants", min_value=2, max_value=10, value=4)

# 🧠 Store player names in session state
if 'player_names' not in st.session_state or len(st.session_state.player_names) != num_players:
    st.session_state.player_names = [f"Player {i+1}" for i in range(num_players)]

for i in range(num_players):
    st.session_state.player_names[i] = st.sidebar.text_input(f"Player {i+1} Name", st.session_state.player_names[i])

player_names = st.session_state.player_names

# 📊 Load NBA stats once
if 'player_stats' not in st.session_state:
    st.session_state['player_stats'] = get_player_stats()

# 🧠 Initialize game state safely
if 'game_state' not in st.session_state or set(st.session_state.game_state.get('budgets', {}).keys()) != set(player_names):
    st.session_state.game_state = {
        'round': 1,
        'current_bidder_index': 0,
        'budgets': {name: 1000 for name in player_names},
        'drafts': {name: [] for name in player_names},
        'drafted_players': [],
        'skipped_players': [],
        'available_players': list(st.session_state.get('player_stats', {}).keys())
    }

st.title("🏀 NBA Draft Bidding Game")

# 🚀 Start Draft Button
if 'draft_started' not in st.session_state:
    if st.button("🚀 Start Draft"):
        st.session_state.draft_started = True
        st.rerun()

# 🔁 Reset Game Button
if st.button("🔁 Reset Game"):
    for key in ['game_state', 'draft_started']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# 🔄 Refresh NBA player pool
if st.button("🔄 Refresh NBA Player Pool"):
    st.session_state['player_stats'] = get_player_stats()
    st.session_state.game_state['available_players'] = list(st.session_state['player_stats'].keys())
    st.rerun()

# 🎯 Bidding Interface
if st.session_state.get('draft_started'):
    if st.session_state.game_state['round'] <= num_rounds:
        st.markdown(f"## 🔥 Round {st.session_state.game_state['round']}")

        available = [p for p in st.session_state.game_state['available_players']
                     if p not in st.session_state.game_state['drafted_players']
                     and p not in st.session_state.game_state['skipped_players']]

        if available:
            # Use stored player or pick a new one
            if 'current_nba_player' not in st.session_state or st.session_state.current_nba_player not in available:
                current_nba_player = random.choice(available)
                st.session_state.current_nba_player = current_nba_player
            else:
                current_nba_player = st.session_state.current_nba_player

            stats = st.session_state['player_stats'].get(current_nba_player, {})
            st.markdown(f"### 🏀 NBA Player: **{current_nba_player}**")
            st.write(f"**PPG:** {stats.get('PPG', 'N/A')} | **APG:** {stats.get('APG', 'N/A')} | **RPG:** {stats.get('RPG', 'N/A')}")

            # Get current player's budget for validation
            current_player = player_names[st.session_state.game_state['current_bidder_index']]
            current_budget = st.session_state.game_state['budgets'][current_player]
            
            st.write(f"**Current Bidder:** {current_player} (Budget: ${current_budget})")
            
            final_bid = st.number_input("💸 Final Bid Amount", min_value=0, max_value=current_budget, step=10, value=min(100, current_budget))
            winning_bidder = st.selectbox("🏆 Winning Bidder", player_names + ["Skip"])

            if st.button("✅ Submit Bid"):
                if winning_bidder != "Skip":
                    # Validate budget
                    if st.session_state.game_state['budgets'][winning_bidder] >= final_bid:
                        st.session_state.game_state['budgets'][winning_bidder] -= final_bid
                        st.session_state.game_state['drafts'][winning_bidder].append(current_nba_player)
                        st.session_state.game_state['drafted_players'].append(current_nba_player)
                    else:
                        st.error(f"❌ {winning_bidder} doesn't have enough budget for this bid!")
                        st.stop()
                else:
                    st.session_state.game_state['skipped_players'].append(current_nba_player)

                st.session_state.game_state['round'] += 1
                st.session_state.game_state['current_bidder_index'] = (
                    st.session_state.game_state['current_bidder_index'] + 1
                ) % num_players
                # Clear the current player so a new one is selected next round
                if 'current_nba_player' in st.session_state:
                    del st.session_state.current_nba_player
                st.rerun()
        else:
            st.warning("No more available NBA players.")
    else:
        st.success("🏁 Draft Complete!")

# 📋 Live Draft Board
st.markdown("## 📊 Live Draft Board")

cols = st.columns(num_players)
for i, name in enumerate(player_names):
    with cols[i]:
        st.subheader(name)
        st.write(f"💰 Budget: ${st.session_state.game_state['budgets'][name]}")
        drafted = st.session_state.game_state['drafts'][name]
        if drafted:
            for player in drafted:
                stats = st.session_state['player_stats'].get(player, {})
                st.write(f"- {player} ({stats.get('PPG', 'N/A')} PPG, {stats.get('APG', 'N/A')} APG, {stats.get('RPG', 'N/A')} RPG)")
        else:
            st.write("No players drafted yet.")
