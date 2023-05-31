from pygame.locals import *
import pygame
import sys
import numpy as np
from game.core import Geometry


class Viewer(object):
    def __init__(self, gamePixelWidth, gamePixelHeight, width, height, display=None):
        pygame.init()

        self.width = width
        self.height = height
        self.gamePixelWidth = gamePixelWidth
        self.gamePixelHeight = gamePixelHeight
        self.screen = pygame.display.set_mode((width, height), 0, 32)
        surface = pygame.Surface(self.screen.get_size())
        self.surface = surface.convert()

        self.fpsClock = pygame.time.Clock()

        self.backgroundImage = None
        self.pods = []
        self.checkpoints = []
        self.text = None

        self.isOpen = True

    def addPod(self, pod):
        self.pods.append(pod)

    def addCheckpoint(self, checkpoint):
        self.checkpoints.append(checkpoint)

    def addText(self, text):
        if self.text is None:
            self.text = text

    def removeText(self):
        if self.text is not None:
            self.text = None

    def setBackground(self, imgPath):
        self.backgroundImage = pygame.image.load(imgPath)

    def render(self):

        scale_width = self.width / self.gamePixelWidth
        scale_height = self.height / self.gamePixelHeight
        scale = 0.1
        for event in pygame.event.get():
            if event.type == QUIT:
                self.isOpen = False
                pygame.quit()
                return False

        # Background
        if self.backgroundImage is not None:
            self.surface.blit(self.backgroundImage, (0, 0))
        else:
            self.surface.fill((0, 0, 0))

        # Checkpoints
        drawed_circle = False
        for ckpt in self.checkpoints:
            if ckpt.visible:
                cx, cy = ckpt.getCoordinates()
                cx = cx * scale_width
                cy = cy * scale_height
                self.surface.blit(
                    pygame.transform.scale(ckpt.image, (scale * ckpt.r, scale * ckpt.r)),
                    (cx, cy)
                )
                font = pygame.font.Font(None, 24)
                text = font.render(str(ckpt.number), 1, (255, 255, 255))
                textpos = text.get_rect()
                textpos.centerx = cx
                textpos.centery = cy
                self.surface.blit(text, textpos)

                if not drawed_circle:
                    drawed_circle = True
                    pygame.draw.circle(self.surface, (0, 255, 0), (int(ckpt.x), int(ckpt.y)),
                                       int(ckpt.width / 2), 2)

        # Pods
        for pod in self.pods:
            cx, cy = pod.getCoordinates()
            cx = cx * scale_width
            cy = cy * scale_height
            self.surface.blit(
                pygame.transform.scale(pod.image, (scale * pod.r, scale * pod.r)),
                (cx, cy)
            )
            # if pod.target_arrow is not None:
            #  pygame.draw.line(self.surface, GREEN, pod.pos, pod.target_arrow, width=1)

        # Text
        if self.text is not None:
            font = pygame.font.Font(None, self.text.fontSize)
            text = font.render(self.text.text, 1, self.text.color, self.text.backgroundColor)
            textpos = text.get_rect()
            textpos.left = self.text.pos[0]
            textpos.top = self.text.pos[1]
            self.surface.blit(text, textpos)

        self.screen.blit(self.surface, (0, 0))
        pygame.display.flip()
        pygame.display.update()

        # pygame.time.wait(50)

        return self.isOpen

    def close(self):
        pygame.quit()


class Text(object):
    def __init__(self, text='text', pos=(0, 0), color=(255, 0, 0), backgroundColor=None, fontSize=32):
        self.text = text
        self.pos = pos
        self.color = color
        self.fontSize = fontSize
        self.backgroundColor = backgroundColor

    def setText(self, text):
        self.text = text


import os


def setup(pods, checkpoints):
    path = os.path.dirname(os.path.abspath(__file__)) + "/../"

    V = Viewer(16000, 9000, 640, 360)
    V.setBackground(imgPath=path + "/imgs/back.png")

    for C in checkpoints:
        V.addCheckpoint(C)

    for P in pods:
        V.addPod(P)

    text = Text(text='0/3', pos=(0, 0), color=(255, 0, 0), backgroundColor=None, fontSize=32)
    V.addText(text)

    return V, text
