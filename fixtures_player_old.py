#%%
import pandas as pd
import http.client
import json
import urllib.parse
from dotenv import load_dotenv
import os
from IPython.display import display
from utils import fetch_data, save_to_csv, load_from_csv
import time
import logging

#%%
logging.basicConfig(filename="api_fetch_log.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
#%%
def configure():
    load_dotenv()
    
#%%
API_HOST = os.getenv("API_HOST")
API_KEY = os.getenv("API_KEY")

#%%
df_fixture = load_from_csv("fixtures_2_2023 - part2.csv")
df_teams = load_from_csv("teams_names_2_2023.csv")
df_consulted = load_from_csv("consulted_fixtures.csv")
df_error = load_from_csv("error_fixtures_vazios.csv")
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


        if res.status != 200:
            print(f"❌ Erro da API para fixture {fixture_id}: {res.status} - {data_dict}")
            logging.error(f"Erro da API para fixture {fixture_id}: {res.status} - {data_dict}")
            return None, False

        if 'response' in data_dict:
            if len(data_dict['response']) > 0:
                df_players = pd.json_normalize(data_dict['response'], record_path=['players'], meta=['team'])
                df_players['fixture.id'] = fixture_id
                logging.info(f"Fixture {fixture_id} carregada com sucesso.")
                return df_players, True
            else:
                print(f"⚠️ Resposta vazia da API para fixture {fixture_id}: {data_dict}")
                logging.warning(f"Resposta vazia da API para fixture {fixture_id}: {data_dict}")
                return None, False
        else:
            print(f"⚠️ Resposta inesperada da API para fixture {fixture_id}: {data_dict}")
            logging.warning(f"Resposta inesperada da API para fixture {fixture_id}: {data_dict}")
            return None, False
    except Exception as e:
        print(f"❌ Erro ao buscar jogadores da fixture {fixture_id}: {str(e)}")
        return None, False

#%%
FixuresColumns = ['fixture.id', 'league.id', 'league.name', 'league.season','league.round', 'teams.home.id','teams.home.name', 'teams.home.winner', 'teams.away.id','teams.away.name', 'teams.away.winner','score.fulltime.home', 'score.fulltime.away', 'score.extratime.home','score.extratime.away']
df_Fixtures_fc = df_fixture[FixuresColumns]
df_Fixtures_fc = df_Fixtures_fc[
    ~df_Fixtures_fc['fixture.id'].astype(str).isin(df_consulted['fixture.id'].astype(str)) 
    #& ~df_Fixtures_fc['fixture.id'].astype(str).isin(df_error['fixture.id'].astype(str))
]
df_Fixtures_fc.reset_index(drop=True, inplace=True)
display(df_Fixtures_fc)

#%%
FixuresColumns = ['fixture.id']
df_Fixtures_fc = df_fixture[FixuresColumns]
display(df_Fixtures_fc)

#%%
consulted_fixtures = []
error_fixtures = []
fixture_players = pd.DataFrame()
#%%
batch_size = 9  # Máximo de 9 chamadas por intervalo
interval = 70   # 1 minuto e 10 segundos

for i in range(0, len(df_Fixtures_fc), batch_size):
    batch = df_Fixtures_fc.iloc[i:i+batch_size]
    
    for fixture_id in batch['fixture.id']:
        result = fetch_fixture_players(fixture_id)
        
        if result:  # Garante que não é None
            df_fixture_players, success = result
        else:
            df_fixture_players, success = None, False

        if success:
            fixture_players = pd.concat([fixture_players, df_fixture_players], ignore_index=True)
            consulted_fixtures.append(fixture_id)
            print(f"✅ Dados carregados para fixture {fixture_id}")
            logging.info(f"✅ Dados carregados para fixture {fixture_id}")
        else:
            error_fixtures.append(fixture_id)
            logging.error(f"❌ Erro ao carregar fixture {fixture_id}")
    
    print(f"⏳ Aguardando {interval} segundos para próxima consulta...")
    logging.info(f"⏳ Aguardando {interval} segundos para próxima consulta...")
    time.sleep(interval)  # Aguarda para evitar violar limite da API

# %%
df_exploded = fixture_players.explode('statistics')
df_expanded_stats_RM = pd.json_normalize(df_exploded['statistics'])

# Adicionar as colunas principais de identificação
df_expanded_stats_RM['player.id'] = df_exploded['player.id']
df_expanded_stats_RM['player.name'] = df_exploded['player.name']
df_expanded_stats_RM['fixture.id'] = df_exploded['fixture.id']

display(df_expanded_stats_RM)
# %%
df_expanded_stats_RM.columns
# %%
save_to_csv(pd.DataFrame({'fixture.id': consulted_fixtures}), "consulted_fixtures.csv")
save_to_csv(pd.DataFrame({'fixture.id': error_fixtures}), "error_fixtures.csv")
save_to_csv(df_expanded_stats_RM, "fixture_team_stats.csv")

print("✅ Processo concluído!")
logging.info("✅ Processo concluído!")
# %%
# display(error_fixtures)
# %%
# error_fixtures = []
# %%
print(df_Fixtures_fc)
#%%
print(df_consulted)

#%%
df3 = df_Fixtures_fc[~df_Fixtures_fc['fixture.id'].isin(df_consulted['fixture.id'])]
df3 = df3.reset_index(drop=True)
# %%
print(df3)
# %%
