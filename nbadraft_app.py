import streamlit as st
import random
import time
import pandas as pd
import os

# 🏀 Get NBA player stats from Excel file (primary data source)
def get_player_stats():
    try:
        # Look for Excel file in the same directory
        excel_files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xls'))]
        
        if not excel_files:
            st.error("❌ No Excel file found! Please add an Excel file with NBA player stats to this folder.")
            st.stop()
        
        # Use the first Excel file found
        excel_file = excel_files[0]
        st.info(f"📊 Reading from: {excel_file}")
        
        # Read the Excel file
        df = pd.read_excel(excel_file)
        
        # Display the first few rows to help with column mapping
        st.write("**Preview of your Excel data:**")
        st.dataframe(df.head())
        
        # Try to identify columns automatically
        player_col = None
        ppg_col = None
        apg_col = None
        rpg_col = None
        
        # Look for common column names
        for col in df.columns:
            col_lower = col.lower()
            if 'player' in col_lower or 'name' in col_lower:
                player_col = col
            elif 'ppg' in col_lower or 'points' in col_lower or 'pts' in col_lower:
                ppg_col = col
            elif 'apg' in col_lower or 'assists' in col_lower or 'ast' in col_lower:
                apg_col = col
            elif 'rpg' in col_lower or 'rebounds' in col_lower or 'reb' in col_lower:
                rpg_col = col
        
        # If columns weren't found automatically, let user select them
        if not all([player_col, ppg_col, apg_col, rpg_col]):
            st.write("**Please select the correct columns:**")
            col1, col2 = st.columns(2)
            with col1:
                player_col = st.selectbox("Player Name Column", df.columns, index=0 if player_col is None else list(df.columns).index(player_col))
                ppg_col = st.selectbox("PPG Column", df.columns, index=0 if ppg_col is None else list(df.columns).index(ppg_col))
            with col2:
                apg_col = st.selectbox("APG Column", df.columns, index=0 if apg_col is None else list(df.columns).index(apg_col))
                rpg_col = st.selectbox("RPG Column", df.columns, index=0 if rpg_col is None else list(df.columns).index(rpg_col))
        
        # Convert data to the required format
        stats = {}
        for _, row in df.iterrows():
            try:
                player_name = str(row[player_col]).strip()
                ppg = str(row[ppg_col]).strip()
                apg = str(row[apg_col]).strip()
                rpg = str(row[rpg_col]).strip()
                
                # Skip if player name is empty or NaN
                if pd.isna(player_name) or player_name == 'nan' or player_name == '':
                    continue
                
                # Convert stats to string format
                if pd.isna(ppg) or ppg == 'nan':
                    ppg = "0.0"
                if pd.isna(apg) or apg == 'nan':
                    apg = "0.0"
                if pd.isna(rpg) or rpg == 'nan':
                    rpg = "0.0"
                
                stats[player_name] = {
                    'PPG': str(float(ppg)),
                    'APG': str(float(apg)),
                    'RPG': str(float(rpg))
                }
            except Exception as e:
                st.warning(f"⚠️ Error processing row: {e}")
                continue
        
        if stats:
            st.success(f"✅ Successfully loaded {len(stats)} NBA players from your Excel file!")
            return stats
        else:
            st.error("❌ No valid player data found in Excel file. Please check your data format.")
            st.stop()
            
    except Exception as e:
        st.error(f"❌ Error reading Excel file: {e}")
        st.error("Please make sure your Excel file is not open in another program and try again.")
        st.stop()

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
    # Initialize roster spots for each player
    roster_spots = {
        'PG': None,
        'SG': None,
        'SF': None,
        'PF': None,
        'C': None,
        '6th Man': None
    }
    
    st.session_state.game_state = {
        'round': 1,
        'current_bidder_index': 0,
        'budgets': {name: 1000 for name in player_names},
        'rosters': {name: roster_spots.copy() for name in player_names},
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
                        st.session_state.game_state['drafted_players'].append(current_nba_player)
                        
                        # Store the drafted player temporarily for roster assignment
                        st.session_state['temp_drafted_player'] = current_nba_player
                        st.session_state['temp_winning_bidder'] = winning_bidder
                        st.session_state['show_roster_assignment'] = True
                        st.rerun()
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

# 🏀 Roster Assignment Interface
if st.session_state.get('show_roster_assignment', False):
    st.markdown("## 🏀 Assign Player to Roster Spot")
    
    winning_bidder = st.session_state.get('temp_winning_bidder')
    drafted_player = st.session_state.get('temp_drafted_player')
    
    if winning_bidder and drafted_player:
        st.write(f"**{winning_bidder}** drafted **{drafted_player}**")
        
        # Get available roster spots
        roster = st.session_state.game_state['rosters'][winning_bidder]
        available_spots = [spot for spot, player in roster.items() if player is None]
        
        if available_spots:
            selected_spot = st.selectbox("Choose roster spot to fill:", available_spots)
            
            if st.button("✅ Assign to Roster"):
                # Assign player to selected spot
                st.session_state.game_state['rosters'][winning_bidder][selected_spot] = drafted_player
                
                # Clear temporary variables
                del st.session_state['temp_drafted_player']
                del st.session_state['temp_winning_bidder']
                st.session_state['show_roster_assignment'] = False
                st.rerun()
        else:
            st.error("No available roster spots!")
            # Clear temporary variables
            del st.session_state['temp_drafted_player']
            del st.session_state['temp_winning_bidder']
            st.session_state['show_roster_assignment'] = False
            st.rerun()

# 📋 Live Draft Board
st.markdown("## 📊 Live Draft Board")

cols = st.columns(num_players)
for i, name in enumerate(player_names):
    with cols[i]:
        st.subheader(name)
        st.write(f"💰 Budget: ${st.session_state.game_state['budgets'][name]}")
        
        # Display roster
        roster = st.session_state.game_state['rosters'][name]
        st.write("**Roster:**")
        for spot, player in roster.items():
            if player:
                stats = st.session_state['player_stats'].get(player, {})
                st.write(f"**{spot}:** {player} ({stats.get('PPG', 'N/A')} PPG, {stats.get('APG', 'N/A')} APG, {stats.get('RPG', 'N/A')} RPG)")
            else:
                st.write(f"**{spot}:** Empty")
# ✏️ Edit Rosters Section
st.markdown("## ✏️ Edit Rosters")

for name in player_names:
    roster = st.session_state.game_state['rosters'][name]
    drafted_players = [p for p in roster.values() if p is not None]

    if drafted_players:
        st.subheader(f"Edit Roster for {name}")
        
        # Player to move
        player_to_move = st.selectbox(
            f"Select player to move for {name}",
            drafted_players,
            key=f"edit_player_{name}"
        )

        # All positions available (including current one)
        available_positions = list(roster.keys())
        current_position = [pos for pos, p in roster.items() if p == player_to_move][0]
        new_position = st.selectbox(
            f"Select new position for {player_to_move}",
            available_positions,
            index=available_positions.index(current_position),
            key=f"edit_position_{name}"
        )

        if st.button(f"Update position for {player_to_move}", key=f"update_{name}"):
            # Remove from current position
            roster[current_position] = None
            
            # If the new position already has a player, swap
            if roster[new_position] is not None:
                swap_player = roster[new_position]
                roster[current_position] = swap_player
            
            # Assign player to new position
            roster[new_position] = player_to_move

            st.success(f"{player_to_move} moved to {new_position}")
            st.rerun()

