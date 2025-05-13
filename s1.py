# IMPORTANTE
# Antes de executar esse código, é necessário iniciar a simulação no coppelia,
# como explicado no passo a passo no readme do projeto.

import sim
import time
import math

# O código funciona com base na seguinte lógica:
# O robô segue a parede direita ao longo do labirinto. Acompanhando-a até o
# final do labirinto. Isso só funciona em mapas cujo o labirinto é formado de
# apenas uma parte, isto é, um labirinto que pode ser descrito como uma única
# linha reta dobrada várias vezes, com cada dobra formando uma virada no labirinto.

# Uma versão simplificada do código é a seguinte:
# [Lê os sensores]
# |- se não detectar nada na frente, ou a detecção estiver longe:
# |  |- se não detectar parede na direita, virar para a direita
# |  |- se detectar parede na direita, seguir reto
# |
# |- se detectar uma parede na frente e estiver perto:
# |  para o robô
# |  |- se houverem paredes na frente e dos lados, vira pra trás
# |  |- se não detectar parede na direita, vira pra direita
# |  |- se não detectar parede na esquerda, vira para a esquerda


# A função se conecta à simulação do coppelia pelo clientID, lê o sensor cujo
# handler é passado como argumento, recebe as informações úteis, com elas sendo:
# se o sensor está detectando algo (detectionState), e as distâncias detectadas
# ([detectpx, detectpy, detectpz]). Os sensores do robô no simulador estão organizados 
# de forma que é utilizado o valor de detectpz para medir a distância entre o
# sensor e a parede.
def lersensor(clientID, sensor_handler):
    [
        _,
        detectionState,
        [detectpx, detectpy, detectpz],
        _,
        _
    ] = sim.simxReadProximitySensor(clientID, sensor_handler, sim.simx_opmode_oneshot_wait)
    return detectionState, detectpx, detectpy, detectpz


# A função preve_acionamento estima a velocidade angular, posteriormente usada nas
# outras funções de preve_acionamento (vai_reto, mov_dir, mov_esq, mov_tras) para calcular
# o tempo de preve_acionamento das rodas para que o robô vire nos ângulos necessários.
# É importante ressaltar que essa estimativa não utiliza leituras da velocidade das
# rodas do robô, não podendo ser considerada uma odometria.
# Optamos por não utilizar odometria por causa que a função do coppelia que permitiria
# implementar odometria também dava muita informação extra, como a posição exata
# do robô no mapa do simulador no instante da chamada da função.
def preve_acionamento(phid, phie):
    r = 0.195/2
    l = 0.331
    omega = r*(phid-phie)/(l)
    return omega


# Função de acionamento que faz o robô ir para a direita. O time.sleep conta com +0.25
# segundos para corrigir o tempo do processamento dos PCs no lab 404-1.
def mov_dir(handleR, handleL, client, v):
    vang = preve_acionamento(-v, v)
    tempo = abs(math.pi/(2*vang))
    sim.simxSetJointTargetVelocity(
        client, handleR, -v, sim.simx_opmode_oneshot)
    sim.simxSetJointTargetVelocity(client, handleL, v, sim.simx_opmode_oneshot)
    time.sleep(tempo+0.25)
    sim.simxSetJointTargetVelocity(client, handleR, 0, sim.simx_opmode_oneshot)
    sim.simxSetJointTargetVelocity(client, handleL, 0, sim.simx_opmode_oneshot)


# Função de acionamento que faz o robô ir para a esquerda. O time.sleep conta com +0.25
# segundos para corrigir o tempo do processamento dos PCs no lab 404-1.
def mov_esq(handleR, handleL, client, v):
    vang = preve_acionamento(v, -v)
    tempo = abs(math.pi/(2*vang))
    sim.simxSetJointTargetVelocity(client, handleR, v, sim.simx_opmode_oneshot)
    sim.simxSetJointTargetVelocity(
        client, handleL, -v, sim.simx_opmode_oneshot)
    time.sleep(tempo+0.25)
    sim.simxSetJointTargetVelocity(client, handleR, 0, sim.simx_opmode_oneshot)
    sim.simxSetJointTargetVelocity(client, handleL, 0, sim.simx_opmode_oneshot)


# Função de acionamento que faz o robô ir para trás. O time.sleep conta com +0.6
# segundos para corrigir o tempo do processamento dos PCs no lab 404-1.
def mov_tras(handleR, handleL, client, v):
    vang = preve_acionamento(v, -v)
    sim.simxSetJointTargetVelocity(client, handleR, v, sim.simx_opmode_oneshot)
    sim.simxSetJointTargetVelocity(
        client, handleL, -v, sim.simx_opmode_oneshot)
    tempo = abs(math.pi/(vang))
    time.sleep(tempo+0.6)
    sim.simxSetJointTargetVelocity(client, handleR, 0, sim.simx_opmode_oneshot)
    sim.simxSetJointTargetVelocity(client, handleL, 0, sim.simx_opmode_oneshot)


# Função de acionamento que faz o robô ir para a frente
def vai_reto(handleR, handleL, client, v, v2):
    sim.simxSetJointTargetVelocity(client, handleR, v, sim.simx_opmode_oneshot)
    sim.simxSetJointTargetVelocity(
        client, handleL, v2, sim.simx_opmode_oneshot)
    time.sleep(0.01)


print('Program started')
sim.simxFinish(-1)  # just in case, close all opened connections
# Connect to CoppeliaSim
clientID = sim.simxStart('127.0.0.1', 19999, True, True, 5000, 5)
if clientID != -1:
    print('Connected to remote API server')
    sim.simxAddStatusbarMessage(
        clientID, 'Funcionando...', sim.simx_opmode_oneshot_wait)
    time.sleep(0.02)

    # handler para o robo
    robotname = 'Pioneer_P3DX'
    returnCode, robotHandle = sim.simxGetObjectHandle(
        clientID, robotname, sim.simx_opmode_oneshot_wait)

    # Handlers para as rodas.
    returnCode, l_wheel = sim.simxGetObjectHandle(clientID,
                                                  '_leftMotor1',
                                                  sim.simx_opmode_oneshot_wait)

    returnCode, r_wheel = sim.simxGetObjectHandle(clientID,
                                                  '_rightMotor1',
                                                  sim.simx_opmode_oneshot_wait)
    # Lembrar de habilitar o 'Real-time mode'
    t = 0
    startTime = time.time()
    lastTime = startTime
    distanciaL = 0
    distanciaR = 0

    # Velocidade básica (linear). Controla a velocidade do robô no simulador.
    v = 5

    # handlers de sensores
    returnCode, l_sensor = sim.simxGetObjectHandle(clientID,
                                                   'sensor0',
                                                   sim.simx_opmode_oneshot_wait)

    returnCode, r_sensor = sim.simxGetObjectHandle(clientID,
                                                   'sensor1',
                                                   sim.simx_opmode_oneshot_wait)

    returnCode, f_sensor = sim.simxGetObjectHandle(clientID,
                                                   'sensor2',
                                                   sim.simx_opmode_oneshot_wait)

    returnCode, t_sensor = sim.simxGetObjectHandle(clientID,
                                                   'sensor5',
                                                   sim.simx_opmode_oneshot_wait)

    while True:

        detectionStateL, detectpx0, detectpy0, detectpz0 = lersensor(clientID, l_sensor)
        detectionStateR, detectpx1, detectpy1, detectpz1 = lersensor(clientID, r_sensor)
        detectionStateF, detectpx2, detectpy2, detectpz2 = lersensor(clientID, f_sensor)
        detectionStateT, detectpx3, detectpy3, detectpz3 = lersensor(clientID, t_sensor)

        # os valores extras no acionamento (como v+1 ou v-0.5) são para corrigir o
        # ângulo do robô, impedindo que ele colida com as paredes.
        if not detectionStateF or detectpz2 > 0.7:
            if detectionStateR and detectpz1 < 0.4:
                vai_reto(r_wheel, l_wheel, clientID, v+1, v)
            elif detectionStateL and detectpz0 < 0.4:
                vai_reto(r_wheel, l_wheel, clientID, v, v+1)
            if detectionStateR and distanciaR-detectpz1 > 0:
                vai_reto(r_wheel, l_wheel, clientID, v+0.5, v)
            elif detectionStateL and distanciaL-detectpz0 > 0:
                vai_reto(r_wheel, l_wheel, clientID, v, v+0.5)
            elif detectionStateR and distanciaR-detectpz1 < 0:
                vai_reto(r_wheel, l_wheel, clientID, v-0.5, v)
            elif detectionStateL and distanciaL-detectpz0 < 0:
                vai_reto(r_wheel, l_wheel, clientID, v, v-0.5)
            else:
                vai_reto(r_wheel, l_wheel, clientID, v, v)
            distanciaR = detectpz1
            distanciaL = detectpz0
            time.sleep(0.01)
        elif (detectionStateF == True and detectpz2 < 0.7):
            # faz o robô parar, freando ambas as rodas até pararem (denotado
            # pelo 0 nas funções abaixo).
            sim.simxSetJointTargetVelocity(clientID,
                                           l_wheel,
                                           0,
                                           sim.simx_opmode_oneshot)

            sim.simxSetJointTargetVelocity(clientID,
                                           r_wheel,
                                           0,
                                           sim.simx_opmode_oneshot)

            print('Estou parando. Então analisarei o que fazer.')
            print("Objeto frontal detectado, mudar direção.")

            if detectionStateL == True and detectionStateR == True:
                print("Paredes detectadas na frente, na direita e na esquerda: virar 180 graus!")
                mov_tras(r_wheel, l_wheel, clientID, v)
            elif detectionStateR == False:
                print("Direita livre: virando para direita!")
                distanciaL = 1
                mov_dir(r_wheel, l_wheel, clientID, v)

                detectionStateR, detectpx1, detectpy1, detectpz1 = lersensor(clientID, r_sensor)
                detectionStateF, detectpx2, detectpy2, detectpz2 = lersensor(clientID, f_sensor)
                detectionStateT, detectpx3, detectpy3, detectpz3 = lersensor(clientID, t_sensor)

                # Controle do robô após virar: Se não detectar nenhuma parede na direita, à frente ou atrás
                # após virar, segue em linha reta, até encontrar novamente uma parede para se guiar.
                while detectionStateT == False and detectionStateF == False and detectionStateR == False:
                    if detectionStateR and distanciaR-detectpz1 > 0:
                        vai_reto(r_wheel, l_wheel, clientID, v+0.4, v)
                        time.sleep(0.05)
                    elif detectionStateL and distanciaL-detectpz0 > 0:
                        vai_reto(r_wheel, l_wheel, clientID, v, v+0.4)
                        time.sleep(0.01)
                    elif detectionStateR and distanciaR-detectpz1 < 0:
                        vai_reto(r_wheel, l_wheel, clientID, v-0.4, v)
                        time.sleep(0.01)
                    elif detectionStateL and distanciaL-detectpz0 < 0:
                        vai_reto(r_wheel, l_wheel, clientID, v, v-0.4)
                        time.sleep(0.01)
                    vai_reto(r_wheel, l_wheel, clientID, v, v)

                    distanciaR = detectpz1
                    distanciaL = detectpz0

                    detectionStateR, detectpx1, detectpy1, detectpz1 = lersensor(clientID, r_sensor)
                    detectionStateF, detectpx2, detectpy2, detectpz2 = lersensor(clientID, f_sensor)
                    detectionStateT, detectpx3, detectpy3, detectpz3 = lersensor(clientID, t_sensor)

            elif detectionStateL == False:
                print("Esquerda livre: virando para esquerda!")
                distanciaR = 1
                mov_esq(r_wheel, l_wheel, clientID, v)

        if (detectionStateR == False and detectionStateF == False and detectionStateT == False):
            vai_reto(r_wheel, l_wheel, clientID, v, v)
            time.sleep(0.5)
            mov_dir(r_wheel, l_wheel, clientID, v)
            # Controle do robô após virar: Se não detectar nenhuma parede na direita, à frente ou atrás
            # após virar, segue em linha reta, até encontrar novamente uma parede para se guiar.
            while detectionStateT == False and detectionStateF == False and detectionStateR == False:
                if detectionStateR and distanciaR-detectpz1 > 0:
                    vai_reto(r_wheel, l_wheel, clientID, v+0.5, v)
                    time.sleep(0.01)
                elif detectionStateL and distanciaL-detectpz0 > 0:
                    vai_reto(r_wheel, l_wheel, clientID, v, v+0.5)
                    time.sleep(0.01)
                elif detectionStateR and distanciaR-detectpz1 < 0:
                    vai_reto(r_wheel, l_wheel, clientID, v-0.5, v)
                    time.sleep(0.01)
                elif detectionStateL and distanciaL-detectpz0 < 0:
                    vai_reto(r_wheel, l_wheel, clientID, v, v-0.5)
                    time.sleep(0.01)
                vai_reto(r_wheel, l_wheel, clientID, v, v)
                distanciaR = detectpz1
                distanciaL = detectpz0
                detectionStateR, detectpx1, detectpy1, detectpz1 = lersensor(clientID, r_sensor)
                detectionStateF, detectpx2, detectpy2, detectpz2 = lersensor(clientID, f_sensor)
                detectionStateT, detectpx3, detectpy3, detectpz3 = lersensor(clientID, t_sensor)
else:
    print('Falha ao conectar com a API do simulador. Inicie a simulação antes de rodar este script.')
