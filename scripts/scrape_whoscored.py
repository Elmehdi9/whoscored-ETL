import json
import pandas as pd
from sqlalchemy import create_engine
import scrapedata as sd
from pandas import Timestamp

def get_latest_match_date(league_name, db_conn_str):
    try:
        engine = create_engine(db_conn_str)
        query = (
            f"SELECT MAX(date) as latest_date "
            f"FROM mapping_table mt "
            f"LEFT JOIN match m ON mt.league_id = m.league_id "
            f"WHERE mt.league_name = '{league_name}' "
            f"GROUP BY mt.league_id"
        )
        latest_date = pd.read_sql_query(query, engine)
        
        if not latest_date.empty:
            return latest_date.iloc[0]['latest_date']
        else:
            return None

    except Exception as e:
        print(f"Error fetching latest match date: {e}")
        return None

def main():
    leagues = [
        "ENG-Premier League", 
        "ESP-La Liga",
        "ITA-Serie A", 
        "GER-Bundesliga",
        "FRA-Ligue 1",
        "NET-Eredevisie"
    ]
    season = '2023'
    db_conn_str = 'XXX'
    data_to_save = []

    for league_name in leagues:
        latest_match_date = get_latest_match_date(league_name, db_conn_str)
        scraper = sd.WhoScored(leagues=league_name, seasons=season)
        league_schedule = scraper.read_schedule()
    
        league_data = {'league_name': league_name, 'matches': []}
        if latest_match_date:
            league_schedule = league_schedule[league_schedule['date'] > latest_match_date]
            match_ids = league_schedule.game_id.values.tolist()

            for index, match_id in enumerate(match_ids):
                events = scraper.read_events(match_id=match_id, output_fmt="raw")
                date = league_schedule['date'].iloc[index]  
                home_team = league_schedule['home_team'].iloc[index]
                away_team = league_schedule['away_team'].iloc[index]
                
                game_info = {
                    'date': date,
                    'home_team': home_team,
                    'away_team': away_team,
                    'game_id': match_id,
                    'events': events[match_id]
                }
                league_data['matches'].append(game_info)
            
            data_to_save.append(league_data)

    def convert_timestamps(obj):
        if isinstance(obj, Timestamp):
            return str(obj)
        return obj

    with open('scraped_data.json', 'w') as json_file:
        json.dump(data_to_save, json_file, default=convert_timestamps, indent=2)

if __name__ == "__main__":
    main()
