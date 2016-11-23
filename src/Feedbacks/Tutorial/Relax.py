import random

import pygame

from FeedbackBase.PygameFeedback import PygameFeedback


class Relax(PygameFeedback):

    def init(self):
        PygameFeedback.init(self)
        # your init code goes here
        # set the initial position of the polygon
        self.positions = []
        for i in range(6):
            self.positions.append([random.randint(0, self.screenSize[0]),
                                   random.randint(0, self.screenSize[1])])
        # set the initial speed vectors
        self.speed = []
        for i in range(6):
            self.speed.append([random.random(), random.random()])
        # set the initial color
        self.color = [0, 255, 128]


    def play_tick(self):
        # paint the background black
        self.screen.fill(self.backgroundColor)
        self.update_polygon()
        self.draw_polygon()
        # do the actual drawing
        pygame.display.flip()


    def update_polygon(self):
        """Update position and color of the polygon."""
        for i in range(6):
            self.positions[i][0] += self.speed[i][0]
            self.positions[i][1] += self.speed[i][1]
        self.color[0] = random.randint(0, 255)
        self.color[1] = random.randint(0, 255)
        self.color[2] = random.randint(0, 255)

    def draw_polygon(self):
        """Draw the polygon."""
        pygame.draw.polygon(self.screen, self.color, self.positions)
