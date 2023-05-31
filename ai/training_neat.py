import math
import os
import neat
import numpy as np
from game.core import run, Point, run_angles
from ai.simulation import init_game
from game.pygame_rendering import Viewer, Text
import time
import copy
import math

path = os.path.dirname(os.path.abspath(__file__))


def score(pod, checkpoints, circuit, net):
    i = 0
    # pod2 = copy.copy(pod)
    initial_dist = pod.distance(checkpoints[pod.nextCheckPointId])
    angles=[]
    while not (pod.win) and not (pod.timeout == 0):
        i += 1
        dist_next_cp = pod.distance(checkpoints[pod.nextCheckPointId])
        angle = net.activate(
            np.array(
                [
                    # pod.x, pod.y,
                    # pod.vx, pod.vy,
                    # pod.angle,
                    # checkpoints[pod.nextCheckPointId].x,
                    # checkpoints[pod.nextCheckPointId].y,
                    # checkpoints[(pod.nextCheckPointId+1) % circuit.nb_checkpoints].x,
                    # checkpoints[(pod.nextCheckPointId+1) % circuit.nb_checkpoints].y,
                    # dist_next_cp,
                    pod.diffAngle(checkpoints[pod.nextCheckPointId]),
                    pod.diffAngle(checkpoints[(pod.nextCheckPointId+1) % circuit.nb_checkpoints])
                ]
            )
        )[0]
        angles.append(angle)
        run_angles([pod], circuit, [angle*180], [100])
        # run_angles([pod2], circuit, [pod2.diffAngle(checkpoints[pod2.nextCheckPointId])], [100])

    # if pod.win:
    #     return pod.score / circuit.length
    # else:
    return (pod.lap - 1) * 3 + pod.nextCheckPointId - sum([abs(a) for a in angles]) #* (100 * ((pod.lap - 1) * 3 + pod.nextCheckPointId) - pod.score)
    # print(pod.score, pod2.score)
    # return pod.score - pod2.score


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        pods, checkpoints, circuit = init_game(1, 4)
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        genome.fitness = score(pods[0], checkpoints, circuit, net)


config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     path + '/config/config.txt')

# Create the population, which is the top-level object for a NEAT run.
p = neat.Population(config)

# Add a stdout reporter to show progress in the terminal.
p.add_reporter(neat.StdOutReporter(False))

# Run until a solution is found.
winner = p.run(eval_genomes)

net = neat.nn.FeedForwardNetwork.create(winner, config)

pods, checkpoints, circuit = init_game(1, 4)

V = Viewer(16000, 9000, 640, 360)
V.setBackground(imgPath=path + "/../imgs/back.png")
text = Text(text='', pos=(0, 0), color=(255, 0, 0), backgroundColor=None, fontSize=32)
V.addText(text)
for p in pods:
    V.addPod(p)
for cp in checkpoints:
    V.addCheckpoint(cp)
while not (np.any(np.array([p.win for p in pods]))) or (np.any(np.array([p.timeout == 0 for p in pods]))):
    angles = []
    thrusts = []
    for pod in pods:
        dist_next_cp = pod.distance(checkpoints[pod.nextCheckPointId])
        angle = (
            net.activate(
                np.array(
                    [
                        pod.x, pod.y,
                        pod.vx, pod.vy,
                        # pod.angle,
                        checkpoints[pod.nextCheckPointId].x,
                        checkpoints[pod.nextCheckPointId].y,
                        checkpoints[(pod.nextCheckPointId + 1) % circuit.nb_checkpoints].x,
                        checkpoints[(pod.nextCheckPointId + 1) % circuit.nb_checkpoints].y,
                        dist_next_cp,
                        pod.diffAngle(checkpoints[pod.nextCheckPointId]),
                        pod.diffAngle(checkpoints[(pod.nextCheckPointId+1) % circuit.nb_checkpoints])
                    ]
                )
            )[0]
        )
        # thrusts.append(100)
    run_angles(pods, circuit, [angle*180], [100])
    time.sleep(1.0 / 30)
    text.setText(f"{angle*180}")
    V.render()
