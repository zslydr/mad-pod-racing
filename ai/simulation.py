from game.core import Pod, Checkpoint, run, Circuit
import os
import time
import random
import numpy as np

path = os.path.dirname(os.path.abspath(__file__)) + "/../"

screen_width = 640
gamePixelWidth = 16000

podRadius = 400
checkpointRadius = 600


def init_game(number_of_pods, number_of_checkpoints):
    checkpoints = []
    for i in range(number_of_checkpoints):
        C = Checkpoint(
            x=random.randint(0, 16000),
            y=random.randint(0, 9000),
            number=i,
            imgPath=path + "/imgs/ckpt.png",
            width=checkpointRadius,
            height=checkpointRadius
        )
        while np.any([C.distance(checkpoint)<2500 for checkpoint in checkpoints]):
            C = Checkpoint(
                x=random.randint(0, 16000),
                y=random.randint(0, 9000),
                number=i,
                imgPath=path + "/imgs/ckpt.png",
                width=checkpointRadius,
                height=checkpointRadius
            )
        checkpoints.append(C)

    circuit = Circuit(checkpoints=checkpoints, nb_laps=3)
    pods = []
    for i in range(number_of_pods):
        P = Pod(
            x=checkpoints[0].x + i * 1000,
            y=checkpoints[0].y + i * 1000,
            identifier=i,
            angle=0,
            nextCheckPointId=1,
            checked=False,
            timeout=100, partner=None,
            shield=False,
            imgPath=path + "/imgs/pod.png",
            width=podRadius,
            height=podRadius
        )
        pods.append(P)

    return pods, checkpoints, circuit


def simulate_one_game(number_of_pods, number_of_checkpoints):
    pods, checkpoints, circuit = init_game(number_of_pods, number_of_checkpoints)

    # for i in range(1000):
    while not (np.any(np.array([p.win for p in pods]))) or (np.any(np.array([p.timeout == 0 for p in pods]))):
        targets = []
        thrusts = []
        for p in pods:
            targets.append([checkpoints[p.nextCheckPointId].x, checkpoints[p.nextCheckPointId].y])
            thrusts.append(100)
        run(pods, circuit, targets, thrusts)
        # time.sleep(1.0 / 30)

    for p in pods:
        if p.win:
            return p.score / circuit.length


if __name__ == "__main__":
    score = simulate_one_game(1, random.randint(2, 5))
    print(score)
