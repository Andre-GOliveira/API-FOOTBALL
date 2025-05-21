Sistema de Extração de Dados de API de Futebol
Visão Geral
Este projeto é um sistema desenvolvido em Python para extrair dados de uma API de futebol. Ele automatiza a coleta de informações sobre ligas, times, partidas, escalações e estatísticas de jogadores, processando esses dados e salvando-os em arquivos CSV para análise posterior. O sistema é projetado para ser executado sequencialmente através de um script orquestrador (main.py).

Funcionalidades Principais
Extração de dados de diversas fontes da API (ligas, times, partidas, etc.).

Normalização e processamento dos dados JSON recebidos.

Tratamento de limites de taxa da API com sistema de lotes e pausas.

Gerenciamento de registros já consultados para evitar reprocessamento desnecessário.

Registro de erros e respostas vazias da API.

Salvamento dos dados extraídos e processados em formato CSV.

Configuração flexível através de variáveis de ambiente.

Estrutura do Projeto
O projeto é composto pelos seguintes scripts principais:

main.py: Script orquestrador que executa todos os módulos de extração em uma sequência predefinida.

utils.py: Contém funções utilitárias comuns usadas por outros scripts (ex: requisições à API, salvamento/carregamento de CSVs).

leagues.py: Extrai informações sobre as ligas de futebol.

Teams.py: Extrai informações sobre os times, filtrados por liga e temporada.

fixtures.py: Extrai informações sobre as partidas, filtradas por liga e temporada.

fixtures_lineups_PROD.py: Extrai as escalações (lineups) para partidas específicas.

fixtures_player.py: Extrai as estatísticas detalhadas dos jogadores em partidas específicas.

.env: Arquivo para armazenar as credenciais da API (não versionado).

Configuração
Siga os passos abaixo para configurar e executar o projeto.

Pré-requisitos
Python 3.7+

PIP (gerenciador de pacotes Python)

Instalação
Clone o repositório (ou copie os arquivos):

# Se estiver usando git
# git clone <url_do_repositorio>
# cd <nome_do_diretorio_do_projeto>

Caso contrário, apenas certifique-se de que todos os arquivos .py estejam no mesmo diretório.

Crie um ambiente virtual (recomendado):

python -m venv venv
# No Windows
venv\Scripts\activate
# No macOS/Linux
source venv/bin/activate

Instale as dependências:
Crie um arquivo requirements.txt com o seguinte conteúdo:

pandas
python-dotenv

E então instale as dependências:

pip install -r requirements.txt

Variáveis de Ambiente
Crie um arquivo chamado .env na raiz do projeto com as suas credenciais da API:

API_HOST=seu_api_host_aqui
API_KEY=sua_api_key_aqui

Substitua seu_api_host_aqui e sua_api_key_aqui pelos valores corretos fornecidos pela API.

Uso (Como Executar)
Executando o Orquestrador
Para executar todo o processo de extração de forma sequencial, utilize o script main.py:

python main.py

Este script irá importar e executar cada um dos módulos de extração na ordem definida internamente. Logs de execução serão exibidos no console e, para scripts específicos como fixtures_lineups_PROD.py e fixtures_player.py, também no arquivo api_fetch_log.log.

Executando Scripts Individualmente
Embora o main.py seja a forma recomendada de execução, cada script de extração individual (leagues.py, Teams.py, etc.) também pode ser executado diretamente, se necessário para testes ou extrações parciais:

python leagues.py
python Teams.py
# e assim por diante

Lembre-se que ao executar individualmente, as dependências de dados entre scripts (ex: fixtures_player.py pode depender de uma lista de partidas gerada por fixtures.py) devem ser gerenciadas manualmente.

Descrição Detalhada dos Scripts de Extração
Cada script é responsável por interagir com um endpoint específico da API ou processar um tipo particular de dado.

leagues.py (Endpoint: /leagues)
Propósito: Busca a lista de todas as ligas de futebol disponíveis na API.

Detalhes: Retorna informações sobre cada liga, incluindo seu ID único e detalhes sobre quais tipos de dados (estatísticas de jogadores, eventos de partidas, etc.) estão disponíveis para ela.

Parâmetros: Nenhum parâmetro de entrada específico para a API (busca todas as ligas).

Saída Principal: Arquivo CSV (ex: leagues_data.csv) contendo os dados normalizados das ligas.

Teams.py (Endpoint: /teams)
Propósito: Extrai a lista de times pertencentes a uma liga específica em uma determinada temporada.

Detalhes: Fornece informações como código do time, nome, país de origem, detalhes do estádio (venue), data de fundação, etc.

Parâmetros para API:

league: ID da liga (obrigatório).

season: Ano da temporada (obrigatório).

(Estes parâmetros são configurados internamente no script, mas podem ser ajustados conforme a avaliação anterior sugeriu torná-los dinâmicos).

Saída Principal: Arquivos CSV (ex: teams_fullinfo_{leagueID}_{season}.csv, teams_names_{leagueID}_{season}.csv).

fixtures.py (Endpoint: /fixtures)
Propósito: Coleta a lista de partidas (fixtures) para uma liga e temporada específicas.

Detalhes: Inclui informações sobre cada partida, como data, horário, local, times envolvidos (mandante e visitante), status da partida, placares (tempo normal, prorrogação, pênaltis se houver) e algumas estatísticas gerais da partida.

Parâmetros para API:

league: ID da liga (obrigatório).

season: Ano da temporada (obrigatório).

(Configurados internamente no script).

Saída Principal: Arquivo CSV (ex: fixtures_{leagueID}_{season}.csv) com os dados normalizados das partidas. Este arquivo pode servir de entrada para os scripts fixtures_player.py e fixtures_lineups_PROD.py.

fixtures_player.py (Endpoint: /fixtures/players)
Propósito: Busca as estatísticas detalhadas de cada jogador em partidas específicas.

Detalhes: O script carrega uma lista de IDs de partidas (geralmente obtida a partir da saída de fixtures.py). Ele gerencia uma lista de partidas já consultadas e partidas que resultaram em erro para otimizar as chamadas à API. As estatísticas podem incluir gols, assistências, passes, desarmes, dribles, cartões, posição em campo, rating, etc.

Parâmetros para API:

fixture: ID da partida (obrigatório).

Saída Principal:

Arquivo CSV com estatísticas dos jogadores (ex: data/fixture_stats/{timestamp}_fixture_team_stats.csv).

Arquivos CSV em data/consulted/ e data/errors/ para rastrear o status das consultas.

fixtures_lineups_PROD.py (Endpoint: /fixtures/lineups)
Propósito: Extrai as informações de escalação (lineup) para cada time em partidas específicas.

Detalhes: Similar ao fixtures_player.py, este script utiliza uma lista de IDs de partidas. Ele também gerencia o histórico de consultas e erros. Os dados de lineup incluem a lista de jogadores titulares, reservas, o técnico, a formação tática (ex: 4-3-3) e a posição de cada jogador.

Parâmetros para API:

fixture: ID da partida (obrigatório).

Saída Principal:

Arquivo CSV com os dados de escalação (ex: data/fixture_lineup/{timestamp}_fixture_lineup.csv).

Arquivos CSV em data/consulted/ e data/errors/.

Estrutura de Dados de Saída
Os dados extraídos e processados são salvos em arquivos CSV, geralmente dentro de um diretório data/ na raiz do projeto. Este diretório pode conter subpastas para melhor organização, como:

data/leagues_data.csv

data/teams_fullinfo_X_Y.csv

data/fixtures_X_Y.csv

data/fixture_list/: Pode conter listas de fixtures para processamento.

data/fixture_stats/: Contém as estatísticas dos jogadores.

data/fixture_lineup/: Contém os dados de escalação.

data/consulted/: CSVs rastreando IDs já consultados com sucesso.

data/errors/: CSVs rastreando IDs que resultaram em erro ou resposta vazia.

Os nomes dos arquivos frequentemente incluem timestamps ou identificadores (como ID da liga e temporada) para facilitar a identificação.

Utilitários (utils.py)
O script utils.py é fundamental para o projeto, fornecendo funções reutilizáveis para:

fetch_data(endpoint, params): Função genérica para realizar requisições GET à API, tratando a autenticação e a resposta JSON básica.

save_to_csv(df, filepath): Salva um DataFrame Pandas em um arquivo CSV.

load_from_csv(filepath): Carrega dados de um arquivo CSV para um DataFrame Pandas.

save_if_not_empty(df, folder, filename): Salva um DataFrame apenas se não estiver vazio, útil para logs de erro e dados condicionais.

Ele também é responsável por carregar as variáveis de ambiente (API_HOST, API_KEY) do arquivo .env usando python-dotenv.

Este README deve servir como um bom ponto de partida. Você pode adicionar mais seções conforme necessário, como "Resolução de Problemas Comuns", "Contribuições" ou "Licença".