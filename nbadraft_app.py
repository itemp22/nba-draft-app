import streamlit as st
import os
import random
import pandas as pd

# =========================
# Data loading
# =========================
def get_player_stats():
    try:
        excel_files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xls'))]
        if not excel_files:
            st.error("❌ No Excel file found! Please add an Excel file with NBA player stats to this folder.")
            st.stop()

        excel_file = excel_files[0]
        st.info(f"📊 Reading from: {excel_file}")

        df = pd.read_excel(excel_file)
        st.write("**Preview of your Excel data:**")
        st.dataframe(df.head())

        # Try to detect columns
        player_col = None
        ppg_col = None
        apg_col = None
        rpg_col = None

        for col in df.columns:
            cl = str(col).lower()
            if ('player' in cl or 'name' in cl) and player_col is None:
                player_col = col
            if (('ppg' in cl) or ('points' in cl) or ('pts' in cl)) and ppg_col is None:
                ppg_col = col
            if (('apg' in cl) or ('assists' in cl) or ('ast' in cl)) and apg_col is None:
                apg_col = col
            if (('rpg' in cl) or ('rebounds' in cl) or ('reb' in cl)) and rpg_col is None:
                rpg_col = col

        if not all([player_col, ppg_col, apg_col, rpg_col]):
            st.write("**Please select the correct columns:**")
            col1, col2 = st.columns(2)
            with col1:
                player_col = st.selectbox("Player Name Column", df.columns, index=0 if player_col is None else list(df.columns).index(player_col))
                ppg_col = st.selectbox("PPG Column", df.columns, index=0 if ppg_col is None else list(df.columns).index(ppg_col))
            with col2:
                apg_col = st.selectbox("APG Column", df.columns, index=0 if apg_col is None else list(df.columns).index(apg_col))
                rpg_col = st.selectbox("RPG Column", df.columns, index=0 if rpg_col is None else list(df.columns).index(rpg_col))

        stats = {}
        for _, row in df.iterrows():
            try:
                player_name = str(row[player_col]).strip()
                if pd.isna(player_name) or player_name.lower() == 'nan' or player_name == '':
                    continue

                def _coerce(x):
                    if pd.isna(x) or str(x).lower() == 'nan' or str(x).strip() == '':
                        return "0.0"
                    return str(float(x))

                ppg = _coerce(row[ppg_col])
                apg = _coerce(row[apg_col])
                rpg = _coerce(row[rpg_col])

                stats[player_name] = {'PPG': ppg, 'APG': apg, 'RPG': rpg}
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

# =========================
# Helpers / Game logic
# =========================
ROSTER_TEMPLATE = {
    'PG': None,
    'SG': None,
    'SF': None,
    'PF': None,
    'C': None,
    '6th Man': None
}

def all_rosters_full(rosters: dict) -> bool:
    return all(all(player is not None for player in spots.values()) for spots in rosters.values())

def empty_spots_count(rosters: dict) -> int:
    return sum(sum(1 for p in r.values() if p is None) for r in rosters.values())

def manager_has_open_spot(rosters: dict, manager: str) -> bool:
    return any(v is None for v in rosters[manager].values())

# =========================
# Sidebar: Setup
# =========================
st.sidebar.header("Game Setup")
num_players = st.sidebar.number_input("Number of Participants", min_value=2, max_value=10, value=4)

# Player names persist & resize with num_players
if 'player_names' not in st.session_state or len(st.session_state.player_names) != num_players:
    st.session_state.player_names = [f"Player {i+1}" for i in range(num_players)]

for i in range(num_players):
    st.session_state.player_names[i] = st.sidebar.text_input(f"Player {i+1} Name", st.session_state.player_names[i])

player_names = st.session_state.player_names

# Load stats once
if 'player_stats' not in st.session_state:
    st.session_state['player_stats'] = get_player_stats()

# Initialize game state
need_new_state = (
    'game_state' not in st.session_state or
    set(st.session_state.game_state.get('budgets', {}).keys()) != set(player_names)
)

if need_new_state:
    st.session_state.game_state = {
        'current_bidder_index': 0,
        'budgets': {name: 1000 for name in player_names},
        'rosters': {name: ROSTER_TEMPLATE.copy() for name in player_names},
        'drafted_players': [],
        'available_players': list(st.session_state.get('player_stats', {}).keys()),
        'turns_taken': 0
    }

st.title("🏀 NBA Draft Bidding Game (Fill All Roster Spots)")

# Start / Reset / Refresh controls
if 'draft_started' not in st.session_state:
    if st.button("🚀 Start Draft"):
        st.session_state.draft_started = True
        st.rerun()

if st.button("🔁 Reset Game"):
    for key in ['game_state', 'draft_started', 'current_nba_player', 'show_roster_assignment',
                'temp_drafted_player', 'temp_winning_bidder']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

if st.button("🔄 Refresh NBA Player Pool"):
    st.session_state['player_stats'] = get_player_stats()
    st.session_state.game_state['available_players'] = list(st.session_state['player_stats'].keys())
    st.rerun()

# =========================
# Draft interface
# =========================
if st.session_state.get('draft_started'):
    rosters = st.session_state.game_state['rosters']

    if not all_rosters_full(rosters):
        spots_left = empty_spots_count(rosters)
        st.markdown(f"## 🔥 Spots Remaining Across All Teams: **{spots_left}**")

        available = [p for p in st.session_state.game_state['available_players']
                     if p not in st.session_state.game_state['drafted_players']]

        if not available:
            st.error("No more available NBA players, but some roster spots are still empty. Add more players or refresh Excel.")
            st.stop()

        if 'current_nba_player' not in st.session_state or st.session_state.current_nba_player not in available:
            st.session_state.current_nba_player = random.choice(available)

        current_nba_player = st.session_state.current_nba_player
        stats = st.session_state['player_stats'].get(current_nba_player, {})
        st.markdown(f"### 🏀 NBA Player: **{current_nba_player}**")
        st.write(f"**PPG:** {stats.get('PPG', 'N/A')} | **APG:** {stats.get('APG', 'N/A')} | **RPG:** {stats.get('RPG', 'N/A')}")

        current_player_name = player_names[st.session_state.game_state['current_bidder_index']]
        current_budget = st.session_state.game_state['budgets'][current_player_name]
        st.write(f"**Current Bidder:** {current_player_name} (Budget: ${current_budget})")

        max_any_budget = max(st.session_state.game_state['budgets'].values()) if st.session_state.game_state['budgets'] else 0
        default_bid = min(100, current_budget)
        final_bid = st.number_input("💸 Final Bid Amount", min_value=0, max_value=max_any_budget, step=10, value=default_bid)
        winning_bidder = st.selectbox("🏆 Winning Bidder", player_names + ["Skip"])

        if st.button("✅ Submit Bid"):
            def advance_turn():
                st.session_state.game_state['turns_taken'] += 1
                st.session_state.game_state['current_bidder_index'] = (
                    st.session_state.game_state['current_bidder_index'] + 1
                ) % len(player_names)
                if 'current_nba_player' in st.session_state:
                    del st.session_state.current_nba_player

            if winning_bidder == "Skip":
                advance_turn()
                st.rerun()

            if st.session_state.game_state['budgets'][winning_bidder] < final_bid:
                st.error(f"❌ {winning_bidder} doesn't have enough budget for this bid!")
                st.stop()

            if not manager_has_open_spot(rosters, winning_bidder):
                st.error(f"❌ {winning_bidder} has no open roster spots! Choose a different winner or 'Skip'.")
                st.stop()

            st.session_state.game_state['budgets'][winning_bidder] -= final_bid
            st.session_state.game_state['drafted_players'].append(current_nba_player)
            st.session_state['temp_drafted_player'] = current_nba_player
            st.session_state['temp_winning_bidder'] = winning_bidder
            st.session_state['show_roster_assignment'] = True

            advance_turn()
            st.rerun()
    else:
        st.success("🏁 All rosters are full — Draft Complete!")

# =========================
# Roster assignment (post-win)
# =========================
if st.session_state.get('show_roster_assignment', False):
    st.markdown("## 🏀 Assign Player to Roster Spot")

    winning_bidder = st.session_state.get('temp_winning_bidder')
    drafted_player = st.session_state.get('temp_drafted_player')

    if winning_bidder and drafted_player:
        st.write(f"**{winning_bidder}** drafted **{drafted_player}**")

        roster = st.session_state.game_state['rosters'][winning_bidder]
        available_spots = [spot for spot, player in roster.items() if player is None]

        if available_spots:
            selected_spot = st.selectbox("Choose roster spot to fill:", available_spots)

            if st.button("✅ Assign to Roster"):
                st.session_state.game_state['rosters'][winning_bidder][selected_spot] = drafted_player
                for k in ['temp_drafted_player', 'temp_winning_bidder']:
                    if k in st.session_state:
                        del st.session_state[k]
                st.session_state['show_roster_assignment'] = False
                st.rerun()
        else:
            st.error("No available roster spots!")
            for k in ['temp_drafted_player', 'temp_winning_bidder']:
                if k in st.session_state:
                    del st.session_state[k]
            st.session_state['show_roster_assignment'] = False
            st.rerun()

# =========================
# Live Draft Board
# =========================
st.markdown("## 📊 Live Draft Board")
cols = st.columns(len(player_names))
for i, name in enumerate(player_names):
    with cols[i]:
        st.subheader(name)
        st.write(f"💰 Budget: ${st.session_state.game_state['budgets'][name]}")
        roster = st.session_state.game_state['rosters'][name]
        st.write("**Roster:**")
        for spot, player in roster.items():
            if player:
                stats = st.session_state['player_stats'].get(player, {})
                st.write(f"**{spot}:** {player} ({stats.get('PPG', 'N/A')} PPG, {stats.get('APG', 'N/A')} APG, {stats.get('RPG', 'N/A')} RPG)")
            else:
                st.write(f"**{spot}:** Empty")
