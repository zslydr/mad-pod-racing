from game.pygame_rendering import Viewer, Text
from game.core import Pod, Checkpoint, run, Circuit, run_angles
import os
import time
import random
import numpy as np
from game.pygame_rendering import setup

path = os.path.dirname(os.path.abspath(__file__))
print(path)
podRadius = 400
checkpointRadius = 600

checkpoints = []
for i in range(4):
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
for i in range(2):
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

V, text = setup(pods, checkpoints)
# for i in range(1000):
while not (np.any(np.array([p.win for p in pods]))):
    targets = []
    thrusts = []
    angles = []
    for p in pods:
        targets.append([checkpoints[p.nextCheckPointId].x, checkpoints[p.nextCheckPointId].y])
        angles.append(p.diffAngle(checkpoints[p.nextCheckPointId]))
        thrusts.append(100)
    # run(pods, circuit, targets, thrusts)
    run_angles(pods, circuit, angles, thrusts)
    text.setText(f"{pods[0].lap}/{circuit.nb_laps}")
    V.render()
    time.sleep(1.0 / 30)
