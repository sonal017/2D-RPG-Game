import pygame, sys
from settings import *
#  from debug import debug
from level2 import Level2

class Game2:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption('Hiro')
        self.clock = pygame.time.Clock()
        
        self.level2 = Level2()

        # sound
        main_sound =pygame.mixer.Sound('./graphics/audio/main.ogg')
        main_sound.set_volume(0.5)
        main_sound.play(loops = -1)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.level2.toggle_menu()

            self.screen.fill(WATER_COLOR2)
            self.level2.run()
            pygame.display.update()
            self.clock.tick(FPS)
if __name__ == '__main__':
    game2 = Game2()
    game2.run()