# Projeto final de RMA
## Passo a passo
Para rodar o projeto, basta seguir o passo a passo abaixo, obedecendo a ordem:
1. Abrir o arquivo `labirinto.ttt` no copelliaSim, selecionando File >> Open scene... >> escolha o arquivo `labirinto.ttt`.
2. Habilitar o Real-Time mode (clicando no botão com um relógio escrito RT).
3. Clicar no Start/Resume simulation (o botão com o ícone que parece a logo do youtube).
4. Executar o arquivo s1.py: `python src/s1.py`, quando na pasta principal do projeto, ou `python s1.py` se dentro da pasta src.
5. Esperar o robô atravessar o labirinto.

Gravação acelerada com uma simulação no pc do lab 404-1: https://youtu.be/2kOpwJvSXE8

## Ressalva
Devido ao simulador rodar a simulação com base nos recursos computacionais da máquina, é possível que simulações em máquinas consideravelmente mais lentas ou mais potentes do que os computadores do lab 404-1 contem com colisões, devido à diferença no tempo necessário para o processamento das informações dos sensores e envio das instruções para o simulador. O código é feito de forma que funcione plenamente nos computadores do lab 404-1, com o robô completando o labirinto aproximadamente 6 minutos.

## Software necessário
- Coppeliasim (versão gratuita disponível em https://www.coppeliarobotics.com)
- Python3

## Estrutura do código
```
src
├── labirinto.ttt
├── remoteApi.dll
├── remoteApi.so
├── s1.py
├── simConst.py
└── sim.py
```
O arquivo `s1.py` contém o código que controla o robô. 
`simConst.py`, `sim.py`, e os `remoteApi` são arquivos advindos do copelliasim para permitir a integração com o simulador.

## Membros
- Henrique Silva Barbosa
- Matheus Souza Zanzin
- Rodrigo Guikang Liu
