#%%
import pandas as pd
import http.client
import json
import urllib.parse
from dotenv import load_dotenv, find_dotenv
import os
from IPython.display import display
from utils import fetch_data, save_to_csv, load_from_csv

#%% 
def configure():
    load_dotenv(find_dotenv())

#%% 
configure()

#%% 
API_HOST = os.getenv("API_HOST")
API_KEY = os.getenv("API_KEY")
dataframes = {}
league = 2
season = 2023

#%%
endpoints = [
    "/teams",
]

#%%
def fetch_data(endpoint, params=None):
    try:
        conn = http.client.HTTPSConnection(API_HOST)
        headers = {
            'x-rapidapi-host': API_HOST,
            'x-rapidapi-key': API_KEY
        }

        query_string = f"?{urllib.parse.urlencode(params)}" if params else ""
        full_endpoint = f"{endpoint}{query_string}"

        conn.request("GET", full_endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()

        data_dict = json.loads(data.decode("utf-8"))

        if 'response' in data_dict:
            df = pd.DataFrame(data_dict['response'])
            dataframes[endpoint] = df 
            print(f"✅ Dados do endpoint {endpoint} atualizados com sucesso.")
            return df
        else:
            print(f"⚠️ Nenhum dado encontrado no endpoint: {endpoint}")
            return None
    except Exception as e:
        print(f"❌ Erro ao buscar dados do endpoint {endpoint}: {e}")
        return None

#%%
df_teams = fetch_data("/teams", {"league": league, "season": season})
display(df_teams)
#%%
df_expanded_teams = pd.concat([
    pd.json_normalize(df_teams['team']).add_prefix('team.'),
    pd.json_normalize(df_teams['venue']).add_prefix('venue.')
], axis=1)

# %%
display(df_expanded_teams)

#%% Salva os dados em um arquivo CSV
save_to_csv(df_expanded_teams, f"teams_fullinfo_{league}_{season}.csv")
# %%
# %%
save_to_csv(df_expanded_teams["team.name"], f"teams_names_{league}_{season}.csv")
# %%
