import requests
import dash
import pandas as pd
from dash import html, dash_table
import json


league_name = "FPL CUP SIUUUUUU"
unknown_winner = -1
cup_league_id = 2696403
league_id = 102765
starting_cup_gameweek = 34

API_URL = f"https://fantasy.premierleague.com/api/leagues-h2h-matches/league/{cup_league_id}/?page=1"
LEAGUE_URL = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/?page_new_entries=1&page_standings=1&phase=1"
MONEY_PAID_ICON = "🤑"
MONEY_NOT_PAID_ICON = ""
OVERRIDE_UNPAID_WINNERS = True
USE_TEST_DATA = False
ERROR_MSG = "Error: Unexpected data. Please check the API response."
no_opponent = "BYE"
not_yet_played_points = "?"

USERS = {
    "FcLookingDownOnYou",
    "CF Basilensis",
    "FcRuben",
    "gohan",
    "JK",
    "The Boys",
    "IceManUnited",
    "Stiftung Wadentest",
    "Peaky Blinders",
    "NYC United",
    "Larsenal",
    "ManCity11",
    "Team Balo",
    "Hamchester Honited",
    "Mugiwara no Ichimi",
    "Real Massi",
    "united",
    "SIUUUUUU",
    "Patcha",
    "ManCity11",
    "Handsome Fc",
    "Team Taka",
}

PAID_USERS = {
    "FcLookingDownOnYou",
    "CF Basilensis",
    "FcRuben",
    "gohan",
    "JK",
    "The Boys",
    "IceManUnited",
    "united",
    "Stiftung Wadentest",
    "Peaky Blinders",
    "NYC United",
    "Larsenal",
    "ManCity11",
    "Handsome Fc",
    "Team Balo",
}

user_map = {user: user for user in USERS}
user_ids = {}
user_player_name_map = {user: user for user in USERS}

def get_points(entry_id, gameweek):
    """Fetch current gameweek user data from the API."""
    entry_data_url = f"https://fantasy.premierleague.com/api/entry/{entry_id}/history/"
    response = requests.get(entry_data_url)
    data = response.json()
    events = data["current"]
    event = next((event for event in events if event["event"] == gameweek), None)
    return event["points"] - event["event_transfers_cost"] if event else 0


ok = True

data = {}
if USE_TEST_DATA:
    with open('test_data.json', 'r') as file:
        data = json.load(file)
else:
    response = requests.get(API_URL)
    data = response.json()

if data["has_next"]:
    print(
        "Warning: There are more pages of data available. Application may not work as expected."
    )

# Preporcess the data
matches = data["results"]
df = pd.DataFrame(matches)

rounds = sorted(df["knockout_name"].dropna().unique())

round_match_counts = {
    round_name: len(df[df["knockout_name"] == round_name]) for round_name in rounds
}

reversed_round_names = {v: k for k, v in round_match_counts.items()}

round_gameweek_map = {
    k: starting_cup_gameweek + i
    for i, (k, v) in enumerate(reversed_round_names.items())
}

sorted_rounds = sorted(round_match_counts.values(), reverse=True)

rounds_df = {
    round: df[df["knockout_name"] == reversed_round_names.get(round)]
    for round in sorted_rounds
}

# Process the cup data
match_results = []

for round_name, round_df in rounds_df.items():
    gameweek = round_gameweek_map[round_name]
    print(f"Processing {round_name}")
    points = round_df["entry_1_points"].sum() + round_df["entry_2_points"].sum()
    started = True if points > 0 else False
    match_results_round = []
    for i, match in round_df.iterrows():
        entry_1_name = match["entry_1_name"]
        entry_2_name = match["entry_2_name"]
        
        # if first round, get user ids from the match data
        if round_name == sorted_rounds[0]:
            user_ids[entry_1_name] = (
                int(match["entry_1_entry"])
                if not pd.isna(match["entry_1_entry"])
                else None
            )
            user_ids[entry_2_name] = (
                int(match["entry_2_entry"])
                if not pd.isna(match["entry_2_entry"])
                else None
            )
            user_player_name_map[entry_1_name] = match["entry_1_player_name"]
            user_player_name_map[entry_2_name] = match["entry_2_player_name"]

        entry_1_entry = user_ids[entry_1_name]
        entry_2_entry = user_ids[entry_2_name]
        entry_1_name = user_map.get(entry_1_name)
        entry_2_name = user_map.get(entry_2_name)
        entry_1_player_name = user_player_name_map.get(entry_1_name)
        entry_2_player_name = user_player_name_map.get(entry_2_name)
        if not entry_1_player_name:
            entry_1_player_name = ""
        if not entry_2_player_name:
            entry_2_player_name = ""

        entry_1_points = (
            get_points(entry_1_entry, gameweek)
            if entry_1_entry
            else match["entry_1_points"]
        )

        entry_2_points = (
            get_points(entry_2_entry, gameweek)
            if entry_2_entry
            else match["entry_2_points"]
        )

        if not entry_2_name:
            winner = entry_1_name
        else:
            if entry_1_points == entry_2_points:
                if (entry_1_name in PAID_USERS) == (entry_2_name in PAID_USERS):
                    winner = unknown_winner
                else:
                    winner = (
                        entry_1_name if entry_1_name in PAID_USERS else entry_2_name
                    )
            else:
                winner = (
                    entry_1_name if entry_1_points > entry_2_points else entry_2_name
                )
                loser = entry_2_name if winner == entry_1_name else entry_1_name

                if (
                    OVERRIDE_UNPAID_WINNERS
                    and winner not in PAID_USERS
                    and loser in PAID_USERS
                ):
                    user_map[winner] = loser
                    winner = loser if loser in PAID_USERS else unknown_winner

        if not entry_1_name:
            entry_1_name = no_opponent
        if not entry_2_name:
            entry_2_name = no_opponent
        
        if not started:
            entry_1_points = not_yet_played_points
            entry_2_points = not_yet_played_points

        match_results_round.append(
            {   
                "round": reversed_round_names.get(round_name),
                "team 1": f"{MONEY_PAID_ICON if entry_1_name in PAID_USERS else MONEY_NOT_PAID_ICON} {entry_1_name} {entry_1_player_name} {entry_1_points}",   
                "team 2": f"{entry_2_points} {entry_2_name} {entry_2_player_name} {MONEY_PAID_ICON if entry_2_name in PAID_USERS else MONEY_NOT_PAID_ICON}",
                "winner": (
                    1
                    if winner == entry_1_name
                    else 2 if winner == entry_2_name else unknown_winner
                ),
            }
        )

    match_results.extend(match_results_round[::-1])

# reverse match_results to show the latest matches at the top
match_results = match_results[::-1]

# Initialize Dash app
app = dash.Dash(__name__)

if not ok:
    app.layout = html.Div(
        [
            html.H1(f"{ERROR_MSG}", style={"textAlign": "center"}),
        ]
    )

else:
    app.title = f"{league_name}"
    app.layout = html.Div(
        [
            html.H1(f"{league_name}", style={"textAlign": "center"}),
            dash_table.DataTable(
                id="cup-results-table",
                columns=[
                    {"name": "Round", "id": "round", "presentation": "text"},
                    {"name": "Team 1", "id": "team 1", "presentation": "text"},
                    {"name": "Team 2", "id": "team 2", "presentation": "text"},
                ],
                data=match_results,
                style_table={
                    "width": "100%",
                    "margin": "auto",
                },
                style_cell={"padding": "10px"},
                style_header={
                    "fontWeight": "bold",
                    "backgroundColor": "#d1fffb",
                    "fontWeight": "bold",
                    "textAlign": "center",
                },
                style_data={"border": "1px solid #ddd"},
                style_data_conditional=[
                    {
                        "if": {"column_id": "team 1"},
                        "textAlign": "right",
                    },
                    {
                        "if": {"column_id": "team 2"},
                        "textAlign": "left",
                    },
                    {
                        "if": {"filter_query": "{winner} = 1", "column_id": "team 1"},
                        "backgroundColor": "#d6feed",
                        "color": "black",
                    },
                    {
                        "if": {"filter_query": "{winner} = 1", "column_id": "team 2"},
                        "backgroundColor": "#F8AFD0FF",
                        "color": "black",
                    },
                    {
                        "if": {"filter_query": "{winner} = 2", "column_id": "team 2"},
                        "backgroundColor": "#d6feed",
                        "color": "black",
                    },
                    {
                        "if": {"filter_query": "{winner} = 2", "column_id": "team 1"},
                        "backgroundColor": "#F8AFD0FF",
                        "color": "black",
                    },
                ] 
            ),
        ]
    )

if __name__ == "__main__":
    app.run(debug=False)
