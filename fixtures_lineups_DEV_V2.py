#%%
import pandas as pd
import http.client
import json
import urllib.parse
from dotenv import load_dotenv
import os
from IPython.display import display
from utils import fetch_data, save_to_csv, load_from_csv, save_if_not_empty
import time
import logging
from datetime import datetime

#%%
logging.basicConfig(filename="api_fetch_log.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

#%%
def configure():
    load_dotenv()
    return {
        "API_HOST": os.getenv("API_HOST"),
        "API_KEY": os.getenv("API_KEY"),
        "BATCH_SIZE": int(os.getenv("BATCH_SIZE", 9)),
        "INTERVAL": int(os.getenv("INTERVAL", 70))
    }

#%%
def fetch_fixture_lineups(api_host, api_key, fixture_id):
    try:
        conn = http.client.HTTPSConnection(api_host)
        headers = {
            'x-rapidapi-host': api_host,
            'x-rapidapi-key': api_key
        }

        endpoint = f"/fixtures/lineups?fixture={fixture_id}"
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        data_dict = json.loads(data.decode("utf-8"))

        if 'errors' in data_dict and isinstance(data_dict['errors'], dict) and data_dict['errors'].get('requests'):
            logging.error(f"🚫 Limite diário atingido ao consultar fixture {fixture_id}: {res.status} - {data_dict}.")
            return None, "limit"

        if 'response' in data_dict and not data_dict['response']:
            logging.warning(f"⚠️ API retornou resposta vazia para fixture {fixture_id}: {res.status} - {data_dict}.")
            return None, "empty"

        if 'response' in data_dict and len(data_dict['response']) > 0:
            df_lineups = pd.DataFrame(data_dict['response'])
            df_lineups['fixture.id'] = fixture_id
            logging.info(f"Fixture {fixture_id} carregada com sucesso.")
            return df_lineups, "success"

        logging.warning(f"⚠️ Resposta inesperada para fixture {fixture_id}: {res.status} - {data_dict}.")
        return None, "unknown"

    except Exception as e:
        logging.error(f"❌ Erro ao buscar fixture {fixture_id}: {type(e).__name__}: {str(e)}")
        return None, "exception"

#%%
def transform_lineup(df_lineup):
    all_rows = []
    for _, row in df_lineup.iterrows():
        team_name = row.get("team", {}).get("name") if isinstance(row.get("team"), dict) else None
        formation = row.get("formation", None)
        fixture_id = row.get("fixture.id", None)

        if isinstance(row.get("coach"), dict):
            all_rows.append({
                "player.id": row["coach"].get("id"),
                "player.name": row["coach"].get("name"),
                "player.pos": "coach",
                "player.grid": None,
                "player.type": "coach",
                "team": team_name,
                "formation": formation,
                "fixture.id": fixture_id
            })

        for role, role_type in [("startXI", "holder"), ("substitutes", "substitute")]:
            if isinstance(row.get(role), list):
                for player_info in row[role]:
                    pl = player_info.get("player", {})
                    all_rows.append({
                        "player.id": pl.get("id"),
                        "player.name": pl.get("name"),
                        "player.pos": pl.get("pos"),
                        "player.grid": pl.get("grid"),
                        "player.type": role_type,
                        "team": team_name,
                        "formation": formation,
                        "fixture.id": fixture_id
                    })

    return pd.DataFrame(all_rows)

#%%
def filter_fixtures(df_fixture_load, df_status):
    ignore_ids = df_status[df_status['status'].isin(['data_loaded', 'empty_response'])]['fixture.id'].astype(str)
    return df_fixture_load[~df_fixture_load['fixture.id'].astype(str).isin(ignore_ids)][['fixture.id']].reset_index(drop=True)

#%%
def process_fixtures(df_fixture_load, consulted_fixtures_list, config):
    fixture_lineups = pd.DataFrame()
    final_status_list = []
    limit_reached = False

    for i in range(0, len(df_fixture_load), config['BATCH_SIZE']):
        if limit_reached:
            break

        batch = df_fixture_load.iloc[i:i+config['BATCH_SIZE']]
        for fixture_id in batch['fixture.id']:
            df_fixture_lineups, status = fetch_fixture_lineups(config['API_HOST'], config['API_KEY'], fixture_id)

            final_status_list.append({'fixture.id': fixture_id, 'status': status})

            if status == "success":
                fixture_lineups = pd.concat([fixture_lineups, df_fixture_lineups], ignore_index=True)
            elif status == "limit":
                limit_reached = True
                print("⚠️ Limite diário atingido. Interrompendo todas as consultas.")
                break

        if limit_reached:
            break

        logging.info(f"⏳ Aguardando {config['INTERVAL']} segundos...")
        time.sleep(config['INTERVAL'])

    # Junta os novos status com os anteriores
    df_final_status = pd.concat([consulted_fixtures_list, pd.DataFrame(final_status_list)], ignore_index=True)
    df_final_status.drop_duplicates(subset="fixture.id", keep="last", inplace=True)

    return fixture_lineups, df_final_status

#%%
config = configure()
timestamp = datetime.now().strftime("%Y%m%d_%H_%M_%S")
BASE_DIR = os.path.join(os.getcwd(), "data")
#%%
# Carregar arquivos
fixtures_path = os.path.join(BASE_DIR, "fixture_list/fixtures_2_2023.csv")
status_path = os.path.join(BASE_DIR, "status/fixture_status_lineup.csv")
df_fixture_load = load_from_csv(fixtures_path)
consulted_fixtures_list = load_from_csv(status_path)
display(df_fixture_load)
#%%
df_fixture_load = filter_fixtures(df_fixture_load, consulted_fixtures_list)
display(consulted_fixtures_list)
#%%
fixture_lineups, df_final_status = process_fixtures(df_fixture_load, consulted_fixtures_list, config)
display(df_final_status)
#%%
df_lineup_flat = transform_lineup(fixture_lineups) if not fixture_lineups.empty else pd.DataFrame()

save_if_not_empty(df_final_status, "status", f"fixture_status_lineup.csv")
save_if_not_empty(df_lineup_flat, "fixture_lineup", f"fixture_lineup.csv")

logging.info("✅ Processo concluído com sucesso!")

# %%
