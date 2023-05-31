from gymnasium import Env
from gymnasium import spaces
from ai.simulation import init_game
from game.core import run, Circuit
import numpy as np
from game.pygame_rendering import setup


class RaceEnv(Env):

    def __init__(self):
        self.number_of_pods = 1
        self.number_of_checkpoints = 4
        self.maxThrust = 100
        self.pods, self.checkpoints, self.circuit = init_game(number_of_pods=self.number_of_pods,
                                                              number_of_checkpoints=self.number_of_checkpoints)

        self.action_space = spaces.Box(
            low=np.array([0.0, 0.0, 0.0]),
            high=np.array([9000.0, 16000.0, self.maxThrust]),
            dtype=int
        )

        self.observation_space = spaces.Box(
            np.array([0, 0, 0, -600, -600, 0, 0, 0, 0]),
            np.array([360, 9000, 16000, 600, 600, 16000, 9000, 16000, 9000]),
            dtype=np.float64
        )

        self.setState()
        self.init_viewer = False


    def step(self, action):
        targets = action[:2]
        thrusts = action[2]
        previous_checkpoint = self.pods[0].nextCheckPointId
        run(self.pods, self.circuit, targets, thrusts)
        self.setState()
        new_checkpoint = self.pods[0].nextCheckPointId

        if previous_checkpoint != new_checkpoint:
            reward = self.pods[0].timeout
        else:
            reward = 0.0

        done = self.pods[0].win

        info = {}

        return self.state, reward, done, info

    def render(self):
        if not(self.init_viewer):
            self.viewer, self.text = setup(self.pods, self.checkpoints)
            self.init_viewer = True
        self.text.setText(f"{self.pods[0].lap}/{self.circuit.nb_laps}")
        self.render()

    def reset(self):
        self.pods, self.checkpoints, self.circuit = init_game(
            number_of_pods=self.number_of_pods,
            number_of_checkpoints=self.number_of_checkpoints
        )
        self.setState()

        return self.state

    def setState(self):
        self.state = np.array(
            [
                self.pods[0].angle,
                self.pods[0].x,
                self.pods[0].y,
                self.pods[0].vx,
                self.pods[0].vy,
                self.checkpoints[self.pods[0].nextCheckPointId].x,
                self.checkpoints[self.pods[0].nextCheckPointId].y,
                self.checkpoints[(self.pods[0].nextCheckPointId+1) % self.circuit.nb_checkpoints].x,
                self.checkpoints[(self.pods[0].nextCheckPointId+1) % self.circuit.nb_checkpoints].y,
            ]
        )

env = RaceEnv()

