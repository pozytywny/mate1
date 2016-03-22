import csv
import os
from collections import namedtuple


import pygame
from pygame.locals import *
from settings import settings, resource, asset
from pygame_objects import (ScoreWidget, QuizCarrousel, LEFT, RIGHT,
                            EVENTID_KILLQUIZ, EVENTID_PUSHQUIZ)
from logging import Logger

AssetsEntry = namedtuple('AssetsEntry', ['text', 'image', 'sound'])


class Game():
    running = False

    def __init__(self, settings):
        pygame.init()
        width, height = settings.resolution
        self.settings = settings
        self.font = settings.font
        self.screen = pygame.display.set_mode(Rect(0, 0, width, height).size)

        heart_image = pygame.image.load(resource('heart.png')).convert_alpha()

        self.score_widget = ScoreWidget(self, heart_image)
        self.background = pygame.Surface(self.screen.get_rect().size).convert()
        self.rect = self.screen.get_rect()
        self.assets = self.read_assets()

    @property
    def assets(self):
        if not self._assets:
            self._assets = self.read_assets()

    def read_assets(self):

        def load_gfx(path):
            return pygame.image.load(asset(path)).convert()
        def load_sfx(path):
            return pygame.mixer.Sound(asset(path))


        with open(asset('assets.csv')) as file:
            reader = csv.reader(file, delimiter=',')
            return [AssetsEntry(text, load_gfx(image), load_sfx(sound))
                    for [text, image, sound] in reader]

    def lost(self):
        pass

    def run(self):
        self.running = True
        clock = pygame.time.Clock()
        self.quiz_carrousel = QuizCarrousel(self)
        for _ in range(self.settings.max_quizzes):
            self.quiz_carrousel.add_random()

        while self.running:
            key = None
            for event in pygame.event.get():
                if event.type == EVENTID_PUSHQUIZ:
                    self.quiz_carrousel.push_widget()
                elif event.type == EVENTID_KILLQUIZ:
                    self.quiz_carrousel.add_random()
                    self.quiz_carrousel.select_widget()
                    self.score_widget.on_score(event.good)

                elif event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.options()
                    else:
                        key = event.unicode
                elif event.type==VIDEORESIZE:
                    screen=pygame.display.set_mode(event.dict['size'],HWSURFACE|DOUBLEBUF|RESIZABLE)
                    screen.blit(pygame.transform.scale(pic,event.dict['size']),(0,0))
                    pygame.display.flip()

                elif event.type==MOUSEBUTTONDOWN and event.button == 1:
                    self.quiz_carrousel.mouseclick(event.pos)

            self.score_widget.draw()
            dirty = self.quiz_carrousel.step(key)
            #self.screen.blit(self.score_widget, (0,0))
            pygame.display.flip()
            clock.tick(40)


    def options(self):
        pass


def main():
    g = Game(settings)
    g.run()

if __name__ == '__main__': main()
