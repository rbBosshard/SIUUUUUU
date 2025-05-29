import requests
import json
import time

LEAGUE_ID = 102765
BASE_URL = f"https://fantasy.premierleague.com/api/leagues-classic/{LEAGUE_ID}/standings/"

data = {}

r = requests.get(BASE_URL)
if r.status_code == 200:
    league_json = r.json()
    data = league_json['standings']['results']

with open("fpl_data.json", "w") as f:
    json.dump(data, f, indent=2)

# --- New code to fetch each manager's gameweek history ---

managers_history = {}

for manager in data:
    entry_id = manager.get('entry')
    team_name = manager.get('entry_name')
    player_name = manager.get('player_name')
    if not entry_id:
        continue
    url = f"https://fantasy.premierleague.com/api/entry/{entry_id}/history/"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            history = resp.json()
            managers_history[entry_id] = {
                'team_name': team_name,
                'player_name': player_name,
                'history': history
            }
        else:
            managers_history[entry_id] = {
                'team_name': team_name,
                'player_name': player_name,
                'history': None,
                'error': f"Status code {resp.status_code}"
            }
    except Exception as e:
        managers_history[entry_id] = {
            'team_name': team_name,
            'player_name': player_name,
            'history': None,
            'error': str(e)
        }
    time.sleep(1)  # Be polite to the server

with open("fpl_managers_history.json", "w") as f:
    json.dump(managers_history, f, indent=2)