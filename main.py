import pygame, sys
from settings import *
#  from debug import debug
from level import Level
import time

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption('Hiro')
        self.clock = pygame.time.Clock()
        
        self.level = Level()
    
        # Load tutorial image
        self.tutorial_image = pygame.image.load('./graphics/tutorial11.png')
        self.tutorial_rect = self.tutorial_image.get_rect()
        self.tutorial_rect.center = (WIDTH // 2, HEIGHT // 2)
        # Blit tutorial image onto screen
        self.screen.blit(self.tutorial_image, self.tutorial_rect)
        pygame.display.flip()
        time.sleep(3)

        self.tutorial_image = pygame.image.load('./graphics/tutorial12.png')
        self.tutorial_rect = self.tutorial_image.get_rect()
        self.tutorial_rect.center = (WIDTH // 2, HEIGHT // 2)
        # Blit tutorial image onto screen
        self.screen.blit(self.tutorial_image, self.tutorial_rect)
        pygame.display.flip()
        time.sleep(3)
        
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
                        self.level.toggle_menu()
     
            self.screen.fill(WATER_COLOR)
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)
if __name__ == '__main__':
    game = Game()
    game.run()