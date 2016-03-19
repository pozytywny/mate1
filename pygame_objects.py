import pygame
import random
import time
LEFT = -1
RIGHT = 1
PADDING = 5
HEART_WIDTH = 25

EVENTID_PUSHQUIZ = 24
EVENTID_KILLQUIZ = 25
EVENTID_GAMEOVEr = 26


class PyGameWidget(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.settings = game.settings
        self.font = self.settings.font



class ScoreWidget(PyGameWidget):
    score = 0
    lives = 3

    def __init__(self, game, heart, score=0, lives=3):
        PyGameWidget.__init__(self, game)
        self.heart = heart
        self.draw()


    def draw(self):
        caption = self.font.render(str(self.score), 0, self.settings.color_normal)
        w, h = caption.get_size()
        self.image = pygame.Surface((w + (PADDING * HEART_WIDTH), h))
        self.image.blit(caption, (0, 0))
        caption_rect = caption.get_rect()

        for life in range(self.lives):
            h_pos = caption_rect.right + (5 + life * HEART_WIDTH)
            self.image.blit(self.heart, (h_pos, -10))
        self.game.screen.blit(self.image, (0,0))

    def on_score(self, good):
        if not good: self.lives -= 1
        else: self.score += 1
        self.draw()


class QuizWidget(PyGameWidget):
    selected = False

    def __init__(self, text, image, sound, game, direction):
        PyGameWidget.__init__(self, game)

        self.text = text.decode('utf-8')
        caption = self.font.render(self.text, 1, self.settings.color_normal)
        self.sound = sound

        self.direction = direction

        self.dy = random.choice([1,0, -1])


        iw, ih = image.get_size()
        cw, ch = caption.get_size()
        width = max(cw, iw)
        height = ih + ch + PADDING
        self.image = pygame.surface.Surface((width, height))
        self.image.fill((0, 255, 0))
        self.image.set_colorkey((0,255,0))

        self.rect = self.image.get_rect()

        self.rect.x = (self.game.rect.width if self.direction == LEFT
                       else -width)
        self.rect.y = random.randrange(self.game.rect.height)

        self.orig_image = image
        self.pos = 0
        self.update()

    def update(self):
        w, h = self.image.get_size()
        iw, ih = self.orig_image.get_size()
        centerw, centerh = w//2, h//2

        self.caption = self.font.render(self.text, 0, self.settings.color_normal)
        self.highlight = self.font.render(self.text[:self.pos], 0, self.settings.color_highlight)
        cw, ch = self.caption.get_size()

        self.image.blit(self.orig_image, (centerw - w//2, 0))
        self.image.blit(self.caption, (centerw - cw//2, ih))
        self.image.blit(self.highlight, (centerw - cw//2, ih))
        if self.selected:   # FIXME:
            line = pygame.draw.line(self.image, (255, 0, 0), (0, h-1), (w, h-1))
            line = pygame.draw.line(self.image, (255, 0, 0), (0, 1), (w, 1))
            line = pygame.draw.line(self.image, (255, 0, 0), (1, 0), (1, h))
            line = pygame.draw.line(self.image, (255, 0, 0), (w-1, 0), (w-1, h))

        self.move()
        pygame.sprite.Sprite.update(self)

    def move(self):
        self.rect.x += self.direction
        self.rect.y += self.dy
        outbound_left = self.rect.right <= 0
        outbound_right = self.rect.left >= self.game.rect.width
        partial_outbound_left = self.rect.left <= 0
        partial_outbound_right = self.rect.right >= self.game.rect.width

        if self.direction == LEFT:
            if outbound_left:
                self.kill(False)
            elif partial_outbound_right:
                self.rect.x += self.direction

        if self.direction == RIGHT:
            if outbound_right:
                self.kill(False)
            elif partial_outbound_left:
                self.rect.x += self.direction

        if self.rect.top <= 0: self.dy = 1
        if self.rect.bottom >= self.game.rect.height: self.dy = -1

    def kill(self, good):
      pygame.sprite.Sprite.kill(self)
      Event = pygame.event.Event(EVENTID_KILLQUIZ, {'good': good})
      pygame.event.post(Event)
      self.sound.play()
      #self.game.on_kill(self, good)

    def keyin(self, key):
        if key == self.text[self.pos]:
            self.pos = self.pos + 1
        if len(self.text) == self.pos:
            self.kill(True)


class OptionsWidget(pygame.sprite.Group):
    def __init__(self, game):
        self.game = game
        self.settings = game.settings
        pass



class QuizCarrousel(pygame.sprite.Group):
    selected = None

    def __init__(self, game):
        pygame.time.set_timer(EVENTID_PUSHQUIZ, 1000)
        self.widget_buffer = []
        self.last_time_added = 0
        self.game = game
        self.settings = game.settings
        pygame.sprite.Group.__init__(self)
        self.max_images = self.settings.max_quizzes

    def push_widget(self):
        print('push')
        if len(self.sprites()) < self.settings.max_quizzes and self.widget_buffer:
            widget = self.widget_buffer.pop()
            self.add(widget)

        if not self.selected:
            self.select_widget()


    def select_widget(self):
        print('select')
        if self.selected:
            self.selected.selected = False
        if self.sprites():
            self.selected = self.sprites()[0]
            self.selected.selected = True


    def mouseclick(self, pos):
        x, y = pos
        rect = self.selected.rect
        for w in self.sprites():
            if w.rect.left < x < w.rect.right and w.rect.top < y < w.rect.bottom:
                w.kill(True)


    def add_random(self, direction=None):
        direction = direction or random.choice([LEFT, RIGHT])
        text, image, sound =  random.choice(self.game.assets)
        widget =QuizWidget(text, image, sound, self.game, direction=direction)
        self.widget_buffer.append(widget)

    def step(self, key):
        if self.selected and key:
            self.selected.keyin(key)

        self.clear(self.game.screen, self.game.background)
        self.update()
        return self.draw(self.game.screen)
