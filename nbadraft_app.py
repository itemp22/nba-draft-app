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
            st.error("❌ No Excel file found! Add an Excel file with NBA stats in this folder.")
            st.stop()

        excel_file = excel_files[0]
        st.info(f"📊 Reading from: {excel_file}")

        df = pd.read_excel(excel_file)
        st.write("**Preview of your Excel data:**")
        st.dataframe(df.head())

        # Auto-detect columns
        col_map = {"player": None, "pts": None, "ast": None, "reb": None}
        for col in df.columns:
            cl = str(col).lower()
            if 'player' in cl and col_map["player"] is None:
                col_map["player"] = col
            if 'pts' in cl and col_map["pts"] is None:
                col_map["pts"] = col
            if 'ast' in cl and col_map["ast"] is None:
                col_map["ast"] = col
            if 'reb' in cl and col_map["reb"] is None:
                col_map["reb"] = col

        stats = {}
        for _, row in df.iterrows():
            try:
                player_name = str(row[col_map["player"]]).strip()
                if pd.isna(player_name) or player_name.lower() == 'nan' or player_name == '':
                    continue

                def _coerce(x):
                    if pd.isna(x) or str(x).lower() == 'nan' or str(x).strip() == '':
                        return "0.0"
                    return str(float(x))

                stats[player_name] = {
                    'PPG': _coerce(row[col_map["pts"]]),
                    'APG': _coerce(row[col_map["ast"]]),
                    'RPG': _coerce(row[col_map["reb"]])
                }
            except:
                continue

        if stats:
            st.success(f"✅ Loaded {len(stats)} NBA players from Excel!")
            return stats
        else:
            st.error("❌ No valid player data found.")
            st.stop()

    except Exception as e:
        st.error(f"❌ Error reading Excel file: {e}")
        st.stop()

# =========================
# Helpers
# =========================
ROSTER_TEMPLATE = {
    'PG': None, 'SG': None, 'SF': None, 'PF': None, 'C': None, '6th Man': None
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
default_skips = st.sidebar.number_input("⏭️ Skips Per Player", min_value=0, max_value=10, value=1)
# Sync skips if default_skips changes

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
        'skips_remaining': {name: default_skips for name in player_names},
        'drafted_players': [],
        'available_players': list(st.session_state.get('player_stats', {}).keys())
    }
for name in player_names:
    current_skips = st.session_state.game_state['skips_remaining'].get(name, None)
    if current_skips is not None and current_skips != default_skips:
        st.session_state.game_state['skips_remaining'][name] = default_skips
st.title("🏀 NBA Draft Bidding Game")

# Start / Reset / Refresh
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

    current_index = st.session_state.game_state['current_first_bidder_index']
    if not manager_has_open_spot(rosters, player_names[current_index]):
        advance_turn()

    if not all_rosters_full(rosters):
        spots_left = empty_spots_count(rosters)
        st.markdown(f"## 🔥 Spots Remaining Across All Teams: **{spots_left}**")

        available = [p for p in st.session_state.game_state['available_players']
                     if p not in st.session_state.game_state['drafted_players']]
        if not available:
            st.error("No more available NBA players, but some roster spots are empty.")
            st.stop()

        if 'current_nba_player' not in st.session_state or st.session_state.current_nba_player not in available:
            st.session_state.current_nba_player = random.choice(available)

        current_nba_player = st.session_state.current_nba_player
        stats = st.session_state['player_stats'].get(current_nba_player, {})
        st.markdown(f"### 🏀 NBA Player: **{current_nba_player}**")
        st.write(f"**PPG:** {stats.get('PPG','N/A')} | **APG:** {stats.get('APG','N/A')} | **RPG:** {stats.get('RPG','N/A')}")

        first_bidder_index = st.session_state.game_state['current_first_bidder_index']
        first_bidder = player_names[first_bidder_index]
        budget = st.session_state.game_state['budgets'][first_bidder]
        skips_left = st.session_state.game_state['skips_remaining'][first_bidder]
        st.write(f"**Current First Bidder:** {first_bidder} | Budget: ${budget} | Skips Left: {skips_left}")

        eligible_winners = [name for name in player_names if manager_has_open_spot(rosters, name)]
        # Ensure selected_bidder is initialized and valid
        if 'selected_bidder' not in st.session_state or st.session_state.selected_bidder not in eligible_winners:
            st.session_state.selected_bidder = eligible_winners[0]

        selected_bidder = st.selectbox(
            "🏆 Winning Bidder",
            eligible_winners,
            index=eligible_winners.index(st.session_state.get("selected_bidder", eligible_winners[0])),
            key="selected_bidder"
        )

        winner_roster = rosters[selected_bidder]
        available_spots = [spot for spot, pl in winner_roster.items() if pl is None]

        if 'selected_spot' not in st.session_state:
            st.session_state.selected_spot = "-- Choose --"

        spot_choices = ["-- Choose --"] + available_spots
        if 'selected_spot' not in st.session_state or st.session_state.selected_spot not in spot_choices:
            st.session_state.selected_spot = "-- Choose --"

        st.session_state.selected_spot = st.selectbox(
            "📌 Assign to Roster Spot",
            spot_choices,
            index=spot_choices.index(st.session_state.selected_spot)
        )

        with st.form("bid_form"):
            final_bid = st.number_input("💸 Final Bid Amount", min_value=0, max_value=10000, step=10, value=100)
            submit_clicked = st.form_submit_button("✅ Submit Bid")

        if submit_clicked:
            if st.session_state.selected_spot.startswith("--"):
                st.error("❗ You must choose a roster spot.")
            else:
                winning_bidder = st.session_state.selected_bidder
                st.session_state.game_state['budgets'][winning_bidder] -= final_bid
                st.session_state.game_state['drafted_players'].append(current_nba_player)
                st.session_state.game_state['rosters'][winning_bidder][st.session_state.selected_spot] = current_nba_player
                advance_turn()
                st.rerun()
        if st.button("⏭️ Skip This Player"):
            if st.session_state.game_state['skips_remaining'][first_bidder] > 0:
                st.session_state.game_state['skips_remaining'][first_bidder] -= 1
                st.session_state.current_nba_player = random.choice([
                    p for p in st.session_state.game_state['available_players']
                    if p not in st.session_state.game_state['drafted_players']
                ])
                advance_turn()
                st.rerun()
            else:
                st.error(f"{first_bidder} has no skips remaining.")
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
        st.write(f"⏭️ Skips Left: {st.session_state.game_state['skips_remaining'][name]}")
        roster = st.session_state.game_state['rosters'][name]
        st.write("**Roster:**")
        for spot, player in roster.items():
            if player:
                stats = st.session_state['player_stats'].get(player, {})
                st.write(f"**{spot}:** {player} ({stats.get('PPG','N/A')} PPG, {stats.get('APG','N/A')} APG, {stats.get('RPG','N/A')} RPG)")
            else:
                st.write(f"**{spot}:** Empty")
# =========================
# Edit Rosters
# =========================
st.markdown("## ✏️ Edit Rosters")
for name in player_names:
    roster = st.session_state.game_state['rosters'][name]
    drafted_players = [p for p in roster.values() if p is not None]
    if drafted_players:
        st.subheader(f"Edit Roster for {name}")
        player_to_move = st.selectbox(f"Select player to move for {name}", drafted_players, key=f"edit_player_{name}")
        available_positions = list(roster.keys())
        current_position = [pos for pos, p in roster.items() if p == player_to_move][0]
        new_position = st.selectbox(f"Select new position for {player_to_move}", available_positions, index=available_positions.index(current_position), key=f"edit_position_{name}")
        if st.button(f"Update position for {player_to_move}", key=f"update_{name}"):
            roster[current_position] = None
            if roster[new_position] is not None:
                swap_player = roster[new_position]
                roster[current_position] = swap_player
            roster[new_position] = player_to_move
            st.success(f"{player_to_move} moved to {new_position}")
            st.rerun()

# =========================
# Trades
# =========================
st.markdown("## 🔄 Trade Players and Cash")
trade_from = st.selectbox("Select player initiating trade", player_names, key="trade_from")
trade_to = st.selectbox("Select player to trade with", [p for p in player_names if p != trade_from], key="trade_to")
from_roster = st.session_state.game_state['rosters'][trade_from]
to_roster = st.session_state.game_state['rosters'][trade_to]
from_budget = st.session_state.game_state['budgets'][trade_from]
to_budget = st.session_state.game_state['budgets'][trade_to]
from_players = [p for p in from_roster.values() if p]
to_players = [p for p in to_roster.values() if p]

st.write(f"### Offer from {trade_from}:")
offer_from_players = st.multiselect("Players to trade away", from_players, key="offer_from_players")
offer_from_cash = st.number_input(f"Cash to trade away from {trade_from} (max ${from_budget})", min_value=0, max_value=from_budget, value=0, step=10, key="offer_from_cash")

st.write(f"### Offer from {trade_to}:")
offer_to_players = st.multiselect("Players to trade away", to_players, key="offer_to_players")
offer_to_cash = st.number_input(f"Cash to trade away from {trade_to} (max ${to_budget})", min_value=0, max_value=to_budget, value=0, step=10, key="offer_to_cash")

if st.button("Execute Trade"):
    if offer_from_cash > from_budget:
        st.error(f"{trade_from} does not have enough cash!")
    elif offer_to_cash > to_budget:
        st.error(f"{trade_to} does not have enough cash!")
    else:
        for p in offer_from_players:
            for pos, pl in from_roster.items():
                if pl == p: from_roster[pos] = None; break
        for p in offer_to_players:
            for pos, pl in to_roster.items():
                if pl == p: to_roster[pos] = None; break

        def add_players(roster, players):
            empty_spots = [pos for pos, pl in roster.items() if pl is None]
            if len(players) > len(empty_spots):
                st.error("Not enough roster spots for trade!")
                return False
            for pos, pl in zip(empty_spots, players):
                roster[pos] = pl
            return True

        if not add_players(from_roster, offer_to_players): st.stop()
        if not add_players(to_roster, offer_from_players): st.stop()

        st.session_state.game_state['budgets'][trade_from] -= offer_from_cash
        st.session_state.game_state['budgets'][trade_from] += offer_to_cash
        st.session_state.game_state['budgets'][trade_to] -= offer_to_cash
        st.session_state.game_state['budgets'][trade_to] += offer_from_cash

        st.success(f"Trade executed between {trade_from} and {trade_to}!")
        st.rerun()
