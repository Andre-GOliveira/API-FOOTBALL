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

#%%
BASE_DIR = os.path.join(os.getcwd(), "data")

# Carregar arquivos com o caminho correto
df_fixture = load_from_csv(os.path.join(BASE_DIR, "fixture_list/fixtures_2_2023 - part1.csv"))
df_consulted = load_from_csv(os.path.join(BASE_DIR, "consulted/consulted_fixtures.csv"))
df_errors = load_from_csv(os.path.join(BASE_DIR, "errors/error_fixtures_vazios.csv"))
display(df_fixture)
#%%
def fetch_fixture_players(fixture_id):
    try:
        conn = http.client.HTTPSConnection(API_HOST)
        headers = {
            'x-rapidapi-host': API_HOST,
            'x-rapidapi-key': API_KEY
        }

        endpoint = f"/fixtures/players?fixture={fixture_id}"
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
            df_players = pd.json_normalize(data_dict['response'], record_path=['players'], meta=['team'])
            df_players['fixture.id'] = fixture_id
            logging.info(f"Fixture {fixture_id} carregada com sucesso.")
            return df_players, "success"

        print(f"⚠️ Resposta inesperada da API para fixture {fixture_id}: {res.status} - {data_dict}")
        logging.warning(f"⚠️ Resposta inesperada da API para fixture {fixture_id}: {res.status} - {data_dict}")
        return None, "unknown"

    except Exception as e:
        print(f"❌ Erro ao buscar jogadores da fixture {fixture_id}: {str(e)}")
        logging.error(f"❌ Erro ao buscar jogadores da fixture {fixture_id}: {str(e)}")
        return None, "exception"

#%%
FixuresColumns = ['fixture.id', 'league.id', 'league.name', 'league.season','league.round', 'teams.home.id','teams.home.name', 'teams.home.winner', 'teams.away.id','teams.away.name', 'teams.away.winner','score.fulltime.home', 'score.fulltime.away', 'score.extratime.home','score.extratime.away']
df_Fixtures_fc = df_fixture[FixuresColumns]
df_Fixtures_fc = df_Fixtures_fc[
    ~df_Fixtures_fc['fixture.id'].astype(str).isin(df_consulted['fixture.id'].astype(str)) 
    #& ~df_Fixtures_fc['fixture.id'].astype(str).isin(df_errors['fixture.id'].astype(str))
]
df_Fixtures_fc.reset_index(drop=True, inplace=True)
display(df_Fixtures_fc)

#%%
FixuresColumns = ['fixture.id']
df_Fixtures_fc = df_Fixtures_fc[FixuresColumns]
display(df_Fixtures_fc)

#%%
consulted_fixtures = []
error_fixtures = []
fixture_players = pd.DataFrame()
limit_error_fixtures = []
empty_response_fixtures = []
consulted_fixtures_list = []
#%%
batch_size = 9  # Máximo de 9 chamadas por intervalo
interval = 70   # 1 minuto e 10 segundos

for i in range(0, len(df_Fixtures_fc), batch_size):
    batch = df_Fixtures_fc.iloc[i:i+batch_size]
    
    for fixture_id in batch['fixture.id']:
        result = fetch_fixture_players(fixture_id)
        
        if result:
            df_fixture_players, status = result
        else:
            df_fixture_players, status = None, "exception"

        if status == "success":
            fixture_players = pd.concat([fixture_players, df_fixture_players], ignore_index=True)
            consulted_fixtures_list.append(fixture_id)
            print(f"✅ Dados carregados para fixture {fixture_id}")
            logging.info(f"✅ Dados carregados para fixture {fixture_id}")
        elif status == "limit":
            limit_error_fixtures.append(fixture_id)
        elif status == "empty":
            empty_response_fixtures.append(fixture_id)
        else:
            error_fixtures.append(fixture_id)
    
    print(f"⏳ Aguardando {interval} segundos para próxima consulta...")
    logging.info(f"⏳ Aguardando {interval} segundos para próxima consulta...")
    time.sleep(interval)  # Aguarda para evitar violar limite da API

# %%
if not fixture_players.empty and "statistics" in fixture_players.columns:
    df_exploded = fixture_players.explode("statistics")

    # Normalizar os dados das estatísticas apenas se houver valores
    if not df_exploded.empty:
        df_expanded_stats_RM = pd.json_normalize(df_exploded["statistics"])
        df_expanded_stats_RM["player.id"] = df_exploded["player.id"]
        df_expanded_stats_RM["player.name"] = df_exploded["player.name"]
        df_expanded_stats_RM["fixture.id"] = df_exploded["fixture.id"]
    else:
        df_expanded_stats_RM = pd.DataFrame()
else:
    print("⚠️ Nenhuma estatística encontrada. Pulando etapa de processamento.")
    df_expanded_stats_RM = pd.DataFrame()
# %%
save_if_not_empty(pd.DataFrame({'fixture.id': consulted_fixtures_list}), "consulted", f"consulted_fixtures.csv")
save_if_not_empty(pd.DataFrame({'fixture.id': error_fixtures}), "errors", f"{timestamp}_error_fixtures.csv")
save_if_not_empty(pd.DataFrame({'fixture.id': limit_error_fixtures}), "errors", f"{timestamp}_limit_error_fixtures.csv")
save_if_not_empty(pd.DataFrame({'fixture.id': empty_response_fixtures}), "errors", f"{timestamp}_empty_response_fixtures.csv")
save_if_not_empty(df_expanded_stats_RM, "fixture_stats", f"{timestamp}_fixture_team_stats.csv")

print("✅ Processo concluído com separação de erros!")
logging.info("✅ Processo concluído com separação de erros!")
