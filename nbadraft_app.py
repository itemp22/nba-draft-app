import streamlit as st
import os
import random
import pandas as pd
import copy

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
# Helpers
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

def advance_turn():
    total_players = len(player_names)
    for _ in range(total_players):
        st.session_state.game_state['current_first_bidder_index'] = (
            st.session_state.game_state['current_first_bidder_index'] + 1
        ) % total_players
        next_bidder = player_names[st.session_state.game_state['current_first_bidder_index']]
        if manager_has_open_spot(st.session_state.game_state['rosters'], next_bidder):
            break
    if 'current_nba_player' in st.session_state:
        del st.session_state.current_nba_player

# =========================
# Sidebar: Setup
# =========================
st.sidebar.header("Game Setup")
num_players = st.sidebar.number_input("Number of Participants", min_value=2, max_value=10, value=4)
skips_per_player = st.sidebar.number_input("Skips per Player", min_value=0, max_value=10, value=1)

if 'player_names' not in st.session_state or len(st.session_state.player_names) != num_players:
    st.session_state.player_names = [f"Player {i+1}" for i in range(num_players)]

for i in range(num_players):
    st.session_state.player_names[i] = st.sidebar.text_input(f"Player {i+1} Name", st.session_state.player_names[i])

player_names = st.session_state.player_names

# Load stats
if 'player_stats' not in st.session_state:
    st.session_state['player_stats'] = get_player_stats()

# Initialize game state
need_new_state = (
    'game_state' not in st.session_state or
    set(st.session_state.game_state.get('budgets', {}).keys()) != set(player_names)
)

if need_new_state:
    st.session_state.game_state = {
        'current_first_bidder_index': 0,
        'budgets': {name: 1000 for name in player_names},
        'rosters': {name: copy.deepcopy(ROSTER_TEMPLATE) for name in player_names},
        'drafted_players': [],
        'available_players': list(st.session_state.get('player_stats', {}).keys()),
        'skips_left': {name: skips_per_player for name in player_names}
    }
    if not manager_has_open_spot(st.session_state.game_state['rosters'], player_names[0]):
        advance_turn()

st.title("🏀 NBA Draft Bidding Game")

# Start / Reset / Refresh controls
if 'draft_started' not in st.session_state:
    if st.button("🚀 Start Draft"):
        st.session_state.draft_started = True
        st.rerun()

if st.button("🔁 Reset Game"):
    for key in ['game_state', 'draft_started', 'current_nba_player',
                'temp_drafted_player', 'temp_winning_bidder', 'show_roster_assignment']:
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
            st.error("No more available NBA players, but some roster spots are still empty.")
            st.stop()

        if 'current_nba_player' not in st.session_state or st.session_state.current_nba_player not in available:
            st.session_state.current_nba_player = random.choice(available)

        current_nba_player = st.session_state.current_nba_player
        stats = st.session_state['player_stats'].get(current_nba_player, {})
        st.markdown(f"### 🏀 NBA Player: **{current_nba_player}**")
        st.write(f"**PPG:** {stats.get('PPG', 'N/A')} | **APG:** {stats.get('APG', 'N/A')} | **RPG:** {stats.get('RPG', 'N/A')}")

        # Current first bidder
        first_bidder_index = st.session_state.game_state['current_first_bidder_index']
        first_bidder = player_names[first_bidder_index]
        skips_left = st.session_state.game_state['skips_left'][first_bidder]
        budget = st.session_state.game_state['budgets'][first_bidder]
        st.write(f"**Current First Bidder:** {first_bidder} | Budget: ${budget} | Skips left: {skips_left}")

        # Eligible winners
        eligible_winners = [name for name in player_names if manager_has_open_spot(rosters, name)]
        skip_option = ["Skip"] if skips_left > 0 else []
        winning_bidder_options = eligible_winners + skip_option

        with st.form("bid_form"):
            final_bid = st.number_input("💸 Final Bid Amount", min_value=0, max_value=10000, step=10, value=100)

            # Winning bidder dropdown
            winning_bidder = st.selectbox("🏆 Winning Bidder", winning_bidder_options, key="winning_bidder_select")

            # Roster spot dropdown dynamically tied to winning bidder
            selected_spot = None
            if winning_bidder != "Skip":
                winner_roster = rosters[winning_bidder]
                available_spots = [spot for spot, player in winner_roster.items() if player is None]
                spot_options = ["-- Choose a roster spot --"] + available_spots
                selected_spot = st.selectbox(
                    "📌 Assign to Roster Spot",
                    spot_options,
                    key=f"assign_spot_{winning_bidder}"
                )

            submit_clicked = st.form_submit_button("✅ Submit Bid")

        # Process submission
        if submit_clicked:
            if winning_bidder == "Skip":
                st.session_state.game_state['skips_left'][first_bidder] -= 1
            elif selected_spot is None or selected_spot.startswith("--"):
                st.error("❗ You must choose a roster spot for the winning bidder before submitting the bid.")
            else:
                # Assign player immediately
                st.session_state.game_state['budgets'][winning_bidder] -= final_bid
                st.session_state.game_state['drafted_players'].append(current_nba_player)
                st.session_state.game_state['rosters'][winning_bidder][selected_spot] = current_nba_player

            # Advance to next bidder with open spots
            advance_turn()
            # Remove current NBA player to pick a new one next round
            if 'current_nba_player' in st.session_state:
                del st.session_state['current_nba_player']
            st.rerun()
    else:
        st.success("🏁 All rosters are full — Draft Complete!")

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
