⚽ API-Football Data Pipeline

Este projeto consiste em uma série de scripts em Python para extração, transformação e armazenamento de dados de futebol, utilizando a API-Football. O objetivo é estruturar e persistir informações ricas sobre ligas, times, partidas, estatísticas de jogadores e formações (lineups).

📁 Estrutura dos Endpoints

/leagues

Retorna a lista de ligas existentes no mundo, incluindo:

Nome e país da liga;

Se a API disponibiliza dados de partidas, estatísticas de jogadores, eventos, etc.;

Cada liga é identificada por um ID único.

/teams

Lista os times participantes de uma liga em determinada temporada.

Parâmetros necessários: league e season;

Inclui nome do time, código, país, cidade, estádio, capacidade e data de fundação;

Dados são normalizados e salvos em CSV.

/fixtures

Lista todas as partidas de uma liga e temporada.

Parâmetros necessários: league e season;

Informações como data, local, status, times envolvidos, resultado, tempo regulamentar e pênaltis;

Dados são transformados em uma tabela estruturada com informações de times, placares e rodadas.

/fixtures_player

Retorna as estatísticas detalhadas dos jogadores para cada partida.

Parâmetro necessário: fixture (ID da partida);

Os scripts carregam previamente:

A lista de partidas a consultar (derivada de /fixtures);

Partidas já consultadas com sucesso;

Partidas com erro ou resposta vazia;

Estatísticas incluem: gols, passes, dribles, duelos, cartões, posição, rating, etc.;

Os dados são transformados, normalizados e salvos em arquivos segmentados.

/fixtures_lineup

Retorna a escalação (lineup) de cada time na partida.

Parâmetro necessário: fixture (ID da partida);

Os scripts também controlam partidas já consultadas e erros anteriores;

Dados extraídos:

Jogadores titulares e reservas;

Treinador;

Formação tática e posição dos jogadores;

A estrutura finaliza com um DataFrame transformado com colunas padronizadas para cada jogador.

⚙️ Execução e Organização

Todos os scripts compartilham uma estrutura comum:

Uso de variáveis de ambiente (API_HOST e API_KEY) via .env;

Conexão HTTP usando http.client com autenticação via headers;

Normalização e transformação dos dados com pandas;

Logs em api_fetch_log.log e tratamento robusto para respostas vazias, erros ou limites da API;

Controle de chamadas em lote para respeitar o limite da API (batch_size e interval);

Salvamento dos dados em arquivos .csv organizados por tipo e ano, dentro da pasta /data.

📦 Dependências

Instale os requisitos com:

pip install -r requirements.txt

Principais bibliotecas utilizadas:

pandas

python-dotenv

http.client

json

urllib.parse

logging

📂 Organização das Pastas

api-football/
├── 1_leagues.py
├── 2_teams.py
├── 2_fixtures.py
├── 3_fixtures_player.py
├── 4_fixtures_lineups.py
├── utils.py
├── .env
├── data/
│   ├── fixture_list/
│   ├── consulted/
│   ├── errors/
│   ├── fixture_stats/
│   ├── fixture_lineup/
│   └── ...
└── README.md

🛡️ Controle de Qualidade

Validação de dados ausentes ou vazios;

Logs de erro e sucesso para rastreabilidade;

Separação clara de erros por tipo (empty, limit, exception);

Verificação para evitar reconsultas desnecessárias.