# Filtro de time 

def filter_fixtures_by_team(df_fixtures, team_name):
    return df_fixtures[
        (df_fixtures['teams.home.name'] == team_name) |
        (df_fixtures['teams.away.name'] == team_name)
    ]

#%%
filtered_fixtures = filter_fixtures_by_team(df_Fixures_fc, team_name)
display(filtered_fixtures)


