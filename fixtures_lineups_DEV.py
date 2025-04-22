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
    
#%%
API_HOST = os.getenv("API_HOST")
API_KEY = os.getenv("API_KEY")
timestamp = datetime.now().strftime("%Y%m%d_%H_%M_%S")
batch_size = 9  # Máximo de 9 chamadas por intervalo
interval = 70   # 1 minuto e 10 segundos

#%%
BASE_DIR = os.path.join(os.getcwd(), "data")

# Carregar arquivos com o caminho correto
df_fixture_load = load_from_csv(os.path.join(BASE_DIR, "fixture_list/fixtures_2_2023.csv"))
consulted_fixtures_list = load_from_csv(os.path.join(BASE_DIR, "status/fixture_status_lineup.csv"))
display(consulted_fixtures_list)
#%%
def fetch_fixture_lineups(fixture_id):
    try:
        conn = http.client.HTTPSConnection(API_HOST)
        headers = {
            'x-rapidapi-host': API_HOST,
            'x-rapidapi-key': API_KEY
        }

        endpoint = f"/fixtures/lineups?fixture={fixture_id}"
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()
        data_dict = json.loads(data.decode("utf-8"))

        # API limit reached
        if 'errors' in data_dict and isinstance(data_dict['errors'], dict) and data_dict['errors'].get('requests'):
            print(f"🚫 Limite da API atingido para fixture {fixture_id}: {res.status} - {data_dict}")
            logging.error(f"🚫 Limite da API atingido para fixture {fixture_id}: {res.status} - {data_dict}")
            return None, "limit"

        # Empty response
        if 'response' in data_dict and not data_dict['response']:
            print(f"⚠️ Resposta vazia da API para fixture {fixture_id}: {res.status} - {data_dict}")
            logging.warning(f"⚠️ Resposta vazia da API para fixture {fixture_id}: {res.status} - {data_dict}")
            return None, "empty"

        # Dados válidos
        if 'response' in data_dict and len(data_dict['response']) > 0:
            df_lineups = pd.DataFrame(data_dict['response'])
            df_lineups['fixture.id'] = fixture_id
            logging.info(f"Fixture {fixture_id} carregada com sucesso.")
            return df_lineups, "success"

        print(f"⚠️ Resposta inesperada da API para fixture {fixture_id}: {res.status} - {data_dict}")
        logging.warning(f"⚠️ Resposta inesperada da API para fixture {fixture_id}: {res.status} - {data_dict}")
        return None, "unknown"

    except Exception as e:
        print(f"❌ Erro ao buscar jogadores da fixture {fixture_id}: {str(e)}")
        logging.error(f"❌ Erro ao buscar jogadores da fixture {fixture_id}: {str(e)}")
        return None, "exception"


#%%
def transform_lineup(df_lineup):

    all_rows = []

    for _, row in df_lineup.iterrows():
        team_name = row["team"]["name"] if isinstance(row["team"], dict) else None
        formation = row["formation"]
        fixture_id = row["fixture.id"]

        if isinstance(row["coach"], dict):
            coach_dict = {
                "player.id":    row["coach"]["id"],
                "player.name":  row["coach"]["name"],
                "player.pos":   "coach",
                "player.grid":  None,
                "player.type":  "coach",
                "team":  team_name,
                "formation": formation,
                "fixture.id": fixture_id
            }
            all_rows.append(coach_dict)

        if isinstance(row["startXI"], list):
            for player_info in row["startXI"]:
                pl = player_info["player"]
                all_rows.append({
                    "player.id":         pl["id"],
                    "player.name":       pl["name"],
                    "player.pos":        pl.get("pos"),
                    "player.grid":       pl.get("grid"),
                    "player.type":       "holder",
                    "team":       team_name,
                    "formation":  formation,
                    "fixture.id": fixture_id
                })
        if isinstance(row["substitutes"], list):
            for player_info in row["substitutes"]:
                pl = player_info["player"]
                all_rows.append({
                    "player.id":         pl["id"],
                    "player.name":       pl["name"],
                    "player.pos":        pl.get("pos"),
                    "player.grid":       pl.get("grid"),
                    "player.type":       "substitute",
                    "team":       team_name,
                    "formation":  formation,
                    "fixture.id": fixture_id
                })
    return pd.DataFrame(all_rows)


#%%
df_fixture_ignore = consulted_fixtures_list[consulted_fixtures_list['status'].isin(['data_loaded', 'empty_response'])]['fixture.id'].astype(str)

df_fixture_load = df_fixture_load[
    ~df_fixture_load['fixture.id'].astype(str).isin(df_fixture_ignore)
][['fixture.id']].reset_index(drop=True)
display(df_fixture_load)
#%%
consulted_fixtures = []
final_status_list = []
limit_reached = False
fixture_lineups = pd.DataFrame()
#%%
for i in range(0, len(df_fixture_load), batch_size):
    if limit_reached:
        break
    batch = df_fixture_load.iloc[i:i+batch_size]
    
    for fixture_id in batch['fixture.id']:
        result = fetch_fixture_lineups(fixture_id)
        
        if result:
            df_fixture_lineups, status = result
        else:
            df_fixture_lineups, status = None, "exception"

        if status == "success":
            fixture_lineups = pd.concat([fixture_lineups, df_fixture_lineups], ignore_index=True)
            consulted_fixtures_list = pd.concat([consulted_fixtures_list, pd.DataFrame([{'fixture.id': fixture_id, 'status': 'data_loaded'}])], ignore_index=True)
            print(f"✅ Dados carregados para fixture {fixture_id}")
            logging.info(f"✅ Dados carregados para fixture {fixture_id}")

        elif status == "limit":
            consulted_fixtures_list = pd.concat([consulted_fixtures_list, pd.DataFrame([{'fixture.id': fixture_id, 'status': 'limit_error'}])], ignore_index=True)
            limit_reached = True
            print("⚠️ Limite diário atingido. Interrompendo todas as consultas.")
            logging.warning("⚠️ Limite diário atingido. Interrompendo todas as consultas.")
            break

        elif status == "empty":
            consulted_fixtures_list = pd.concat([consulted_fixtures_list, pd.DataFrame([{'fixture.id': fixture_id, 'status': 'empty_response'}])], ignore_index=True)

        else:
            consulted_fixtures_list = pd.concat([consulted_fixtures_list, pd.DataFrame([{'fixture.id': fixture_id, 'status': 'error_fixture'}])], ignore_index=True)
    
    # Se o limite foi atingido, interrompe também o loop externo
    if limit_reached:
        break
    
    print(f"⏳ Aguardando {interval} segundos para próxima consulta...")
    logging.info(f"⏳ Aguardando {interval} segundos para próxima consulta...")
    time.sleep(interval)  # Aguarda para evitar violar limite da API

# %%
if not fixture_lineups.empty:
    df_lineup_flat = transform_lineup(fixture_lineups)
    
else:
    df_lineup_flat = pd.DataFrame()
    print("⚠️ Nenhum dado retornado para lineups. Pulando etapa de processamento.")
    df_final_status = pd.DataFrame(consulted_fixtures_list)

#%%
display(df_lineup_flat)
# %%
df_final_status = pd.DataFrame(consulted_fixtures_list)

save_if_not_empty(df_final_status, "status", f"fixture_status_lineup.csv")
save_if_not_empty(df_lineup_flat, "fixture_lineup", f"fixture_lineup.csv")

print("✅ Processo concluído com arquivo único de status e carga final!")
logging.info("✅ Processo concluído com arquivo único de status e carga final!")
