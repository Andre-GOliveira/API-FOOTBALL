/leagues
Nela há a lista de ligas existentes no mundo e os detalhes se a API retorna dados sobre a lista de partidas daquela liga, estatísticas de player, eventos, etc.
Cada liga é representada por um ID.

/teams
Estrutura com a lista de times relacionados a liga.
Como parametro é necessário passar o ID da liga e o ano da liga buscada.
Nela há a lista de times relacionados a liga buscada, código do time, país de origem, localização geográfica, data de criação, etc.

/fixtures
Estrutura com a lista de partidas relacionada a liga. 
Como parametro é necessário passar o ID da liga e o ano da liga buscada. 
Nela é passado detalhes da partida, como data, local, times, tempos e estatisticas da partida, como quantidades de gols e penaltis. 

/fixtures_player
Estrutura com as estatisticas de cada jogador dentro das partidas. 
Como parametro é necessário passar o ID da partida a ser buscada.
No script é feito um carregamento inicial com a lista de partidas que devem ser consultadas, o qual foram geradas a partir do endpoint fixtures, a lista de partidas já consultadas anteriormente, assim evitando que o código faça consultas de partidas o qual já temos os dados e também é carregado a lista de partidas que já foram consultadas previamente e tiveram como retorno algum erro relacionado ao ID da partida ou um retorno vazio. 
Nela há detalhes estatísticos sobre cada jogadores relacionado a uma partida, assim como quantidades de gols do jogador na partida, quantidade de passes, disputas de bola, dribles, cartão amarelo e vermelho, posição, rating, se foi capitão ou não, etc. 

/fixtures_lineup
Estrutura com o lineup de cada partida.
Como parametro é necessário passar o ID da partida a ser buscada.
No script é feito um carregamento inicial com a lista de partidas que devem ser consultadas, o qual foram geradas a partir do endpoint fixtures, a lista de partidas já consultadas anteriormente, assim evitando que o código faça consultas de partidas o qual já temos os dados e também é carregado a lista de partidas que já foram consultadas previamente e tiveram como retorno algum erro relacionado ao ID da partida ou um retorno vazio. 
Nele há a lista de jogadores e coach de cada partida, posição, se há titular ou banco e formação da partida. 