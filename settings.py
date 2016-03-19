from ConfigParser import ConfigParser, NoOptionError
import pygame


class GameConfig():
    _defaults = {
        "font_path": "resources/ubuntu.ttf",
        "resolution": (800, 600),
        "font_size": 26,
        "color_normal": (100, 100, 100),
        "color_highlight": (255, 255, 255),
        "max_speed": 1,
        "max_quizzes": 5
    }

    _font = None

    def __init__(self, file_paths=None):
        pygame.font.init()
        self.settings = {}
        if not file_paths:
            return
        self.load_settings(file_paths)

    def load_settings(self, file_paths):
        parser = ConfigParser()
        parser.read(file_paths)
        parser.add_section('game')
        for key, default in self._defaults.items():
            try:
                value = parser.get('game', key)
                value = (map(int, value.split(',')) if isinstance(default, tuple)
                            else type(default)(value))

                self.settings[key] = value

            except NoOptionError:
                self.settings[key] = default


    @property
    def font(self):
        if not self._font:
            self._font = pygame.font.Font(self.font_path, self.font_size)

        return self._font

    def __getattr__(self, attr):
        return self.settings[attr]

settings = GameConfig(['settings.ini'])
