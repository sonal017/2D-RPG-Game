import asyncio
import builtins
import sys

import pygame

from level import Level
from level2 import Level2
from settings import *


def get_browser_window():
    window = globals().get('hiro_browser_window')
    if window is not None:
        return window

    runtime = getattr(builtins, '__EMSCRIPTEN__', None)
    window = getattr(runtime, 'window', None)
    if window is not None:
        return window

    try:
        import platform as browser_platform
    except ImportError:
        browser_platform = None

    window = getattr(browser_platform, 'window', None)
    if window is not None:
        return window

    try:
        import js
    except ImportError:
        return None

    window = getattr(js, 'window', None)
    if window is not None:
        return window
    return js if hasattr(js, 'document') else None


BROWSER_WINDOW = get_browser_window()
IS_BROWSER = BROWSER_WINDOW is not None

if IS_BROWSER:
    BROWSER_WINDOW.canvas.style.imageRendering = "pixelated"


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Hiro')
        self.clock = pygame.time.Clock()
        self.running = True

        self.state = None
        self.level = None
        self.level2 = None
        self.pending_level = None
        self.loading_message = ''
        self.shell_action_time = 0
        self.shell_action_cooldown = 250

        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.title_font = pygame.font.Font(UI_FONT, 42)
        self.small_font = pygame.font.Font(UI_FONT, 15)

        self.image_cache = {}
        self.main_sound = None
        self.tutorial_images = []
        self.home_image = self.load_screen_image('./graphics/bgimg/homebg.png')
        self.install_browser_input_bridge()
        self.set_state('home')

    def set_state(self, state):
        self.state = state
        captions = {
            'home': 'Hiro',
            'level1': 'Hiro - Level 1',
            'level2': 'Hiro - Level 2',
            'game_over': 'Hiro - Game Over',
            'level_complete': 'Hiro - Level Clear',
            'game_complete': 'Hiro - Complete'
        }
        caption = captions.get(state, 'Hiro')
        if state == 'loading' and self.loading_message:
            caption = f'Hiro - {self.loading_message.title()}'
        pygame.display.set_caption(caption)

    def install_browser_input_bridge(self):
        if not IS_BROWSER:
            return

        try:
            BROWSER_WINDOW.eval("""
                if (!window.__hiroInputBridgeInstalled) {
                    window.__hiroInputBridgeInstalled = true;
                    window.hiroStartRequested = false;

                    const requestStart = () => {
                        window.hiroStartRequested = true;
                    };

                    document.addEventListener('pointerdown', requestStart, { passive: true });
                    document.addEventListener('keydown', (event) => {
                        if (event.code === 'Space' || event.code === 'Enter') {
                            window.hiroStartRequested = true;
                            event.preventDefault();
                        }
                    });
                }
            """)
        except Exception:
            return

    def browser_start_requested(self):
        if not IS_BROWSER:
            return False

        try:
            requested = bool(BROWSER_WINDOW.hiroStartRequested)
        except AttributeError:
            return False

        if requested:
            BROWSER_WINDOW.eval("window.hiroStartRequested = false")
        return requested

    def clear_browser_start_request(self):
        if IS_BROWSER:
            BROWSER_WINDOW.eval("window.hiroStartRequested = false")

    def load_screen_image(self, path):
        if path in self.image_cache:
            return self.image_cache[path]

        try:
            image = pygame.image.load(path).convert()
        except pygame.error:
            return None
        image = pygame.transform.smoothscale(image, (WIDTH, HEIGHT))
        self.image_cache[path] = image
        return image

    def load_tutorial_images(self):
        if self.tutorial_images:
            return

        for path in ('./graphics/tutorial11.png', './graphics/tutorial12.png'):
            try:
                self.tutorial_images.append(pygame.image.load(path).convert())
            except pygame.error:
                self.tutorial_images.append(None)

    def start_music(self):
        if self.main_sound:
            return

        try:
            main_sound = pygame.mixer.Sound('./graphics/audio/main.ogg')
        except pygame.error:
            return
        main_sound.set_volume(0.5)
        main_sound.play(loops=-1)
        self.main_sound = main_sound

    def start_level_one(self):
        self.start_music()
        self.load_tutorial_images()
        self.level = Level()
        self.level2 = None
        self.set_state('level1')
        self.show_tutorial_until = pygame.time.get_ticks() + 6000

    def start_level_two(self):
        self.start_music()
        self.level = None
        self.level2 = Level2()
        self.set_state('level2')

    def queue_level_one(self):
        self.level = None
        self.level2 = None
        self.pending_level = 'level1'
        self.loading_message = 'LOADING LEVEL 1'
        self.set_state('loading')

    def queue_level_two(self):
        self.level = None
        self.level2 = None
        self.pending_level = 'level2'
        self.loading_message = 'LOADING LEVEL 2'
        self.set_state('loading')

    async def load_pending_level(self):
        pending_level = self.pending_level
        self.pending_level = None
        await asyncio.sleep(0)

        if pending_level == 'level1':
            self.start_level_one()
        elif pending_level == 'level2':
            self.start_level_two()

    def go_home(self):
        self.level = None
        self.level2 = None
        self.pending_level = None
        self.set_state('home')

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return

        if event.type == GAME_OVER_EVENT:
            self.set_state('game_over')
            return

        if event.type == LEVEL_COMPLETE_EVENT:
            self.set_state('level_complete')
            return

        if event.type == GAME_COMPLETE_EVENT:
            self.set_state('game_complete')
            return

        if event.type == pygame.KEYDOWN:
            self.handle_keydown(event.key)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click()

    def handle_keydown(self, key):
        if self.state == 'home':
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                self.queue_level_one()
            return

        if self.state == 'level1':
            if key == pygame.K_m:
                self.level.toggle_menu()
            elif key == pygame.K_ESCAPE:
                self.go_home()
            return

        if self.state == 'level2':
            if key == pygame.K_m:
                self.level2.toggle_menu()
            elif key == pygame.K_ESCAPE:
                self.go_home()
            return

        if self.state == 'game_over':
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                self.queue_level_one()
            elif key == pygame.K_h:
                self.go_home()
            return

        if self.state == 'level_complete':
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                self.queue_level_two()
            elif key == pygame.K_h:
                self.go_home()
            return

        if self.state == 'game_complete':
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                self.queue_level_one()
            elif key == pygame.K_h:
                self.go_home()

    def handle_click(self):
        if self.state == 'home':
            self.queue_level_one()
        elif self.state == 'game_over':
            self.queue_level_one()
        elif self.state == 'level_complete':
            self.queue_level_two()
        elif self.state == 'game_complete':
            self.go_home()

    def shell_input_pressed(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.shell_action_time < self.shell_action_cooldown:
            return False

        if self.browser_start_requested():
            self.shell_action_time = current_time
            return True

        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        pressed = keys[pygame.K_SPACE] or keys[pygame.K_RETURN] or mouse_buttons[0]
        if pressed:
            self.shell_action_time = current_time
        return pressed

    def poll_shell_controls(self):
        if self.state not in ('home', 'game_over', 'level_complete', 'game_complete'):
            self.clear_browser_start_request()
            return

        if not self.shell_input_pressed():
            return

        if self.state == 'home':
            self.queue_level_one()
        elif self.state == 'game_over':
            self.queue_level_one()
        elif self.state == 'level_complete':
            self.queue_level_two()
        elif self.state == 'game_complete':
            self.go_home()

    def draw_text(self, text, font, color, center):
        text_surf = font.render(text, False, color)
        text_rect = text_surf.get_rect(center=center)
        self.screen.blit(text_surf, text_rect)

    def draw_lines(self, lines, y, font=None, color=TEXT_COLOR, gap=12):
        font = font or self.font
        for line in lines:
            text_surf = font.render(line, False, color)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, y))
            self.screen.blit(text_surf, text_rect)
            y += text_rect.height + gap

    def darken(self, amount=130):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, amount))
        self.screen.blit(overlay, (0, 0))

    def draw_home(self):
        if self.home_image:
            self.screen.blit(self.home_image, (0, 0))
        else:
            self.screen.fill(WATER_COLOR)
        self.darken(95)
        self.draw_text('HIRO', self.title_font, 'gold', (WIDTH // 2, 155))
        self.draw_lines(
            [
                'SPACE / CLICK TO START',
                'ARROWS MOVE   SPACE ATTACK   LEFT CTRL MAGIC',
                'Q WEAPON   E MAGIC   M UPGRADE'
            ],
            275,
            self.small_font
        )

    def draw_game_over(self):
        game_over_image = self.load_screen_image('./graphics/bgimg/game_over_neon_lights_hd_game_over.png')
        if game_over_image:
            self.screen.blit(game_over_image, (0, 0))
        else:
            self.screen.fill(UI_BG_COLOR)
        self.darken(60)
        self.draw_lines(
            ['SPACE / CLICK TO RESTART', 'H FOR HOME'],
            500,
            self.font
        )

    def draw_loading(self):
        if self.home_image:
            self.screen.blit(self.home_image, (0, 0))
            self.darken(150)
        else:
            self.screen.fill(UI_BG_COLOR)
        message = self.loading_message or 'LOADING'
        self.draw_text(message, self.title_font, 'gold', (WIDTH // 2, HEIGHT // 2 - 20))
        self.draw_text('PLEASE WAIT', self.font, TEXT_COLOR, (WIDTH // 2, HEIGHT // 2 + 45))

    def draw_level_complete(self):
        victory_image = self.load_screen_image('./graphics/bgimg/victory1.png')
        if victory_image:
            self.screen.blit(victory_image, (0, 0))
        else:
            self.screen.fill(WATER_COLOR)
        self.darken(70)
        self.draw_text('LEVEL CLEAR', self.title_font, 'gold', (WIDTH // 2, 150))
        self.draw_lines(
            ['SPACE / CLICK FOR LEVEL 2', 'H FOR HOME'],
            440,
            self.font
        )

    def draw_game_complete(self):
        victory_image = self.load_screen_image('./graphics/bgimg/victory1.png')
        if victory_image:
            self.screen.blit(victory_image, (0, 0))
        else:
            self.screen.fill(WATER_COLOR2)
        self.darken(75)
        self.draw_text('YOU WON', self.title_font, 'gold', (WIDTH // 2, 150))
        self.draw_lines(
            ['SPACE TO PLAY AGAIN', 'CLICK OR H FOR HOME'],
            440,
            self.font
        )

    def draw_tutorial(self):
        elapsed = 6000 - max(0, self.show_tutorial_until - pygame.time.get_ticks())
        tutorial_index = 0 if elapsed < 3000 else 1
        if tutorial_index < len(self.tutorial_images):
            tutorial_image = self.tutorial_images[tutorial_index]
        else:
            tutorial_image = None

        if tutorial_image:
            tutorial_rect = tutorial_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(tutorial_image, tutorial_rect)

    def draw(self):
        if self.state == 'home':
            self.draw_home()
            return

        if self.state == 'level1':
            self.screen.fill(WATER_COLOR)
            self.level.run()
            if pygame.time.get_ticks() < self.show_tutorial_until:
                self.draw_tutorial()
            return

        if self.state == 'loading':
            self.draw_loading()
            return

        if self.state == 'level2':
            self.screen.fill(WATER_COLOR2)
            self.level2.run()
            return

        if self.state == 'game_over':
            self.draw_game_over()
            return

        if self.state == 'level_complete':
            self.draw_level_complete()
            return

        if self.state == 'game_complete':
            self.draw_game_complete()

    async def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)

            self.poll_shell_controls()
            self.draw()
            pygame.display.update()
            if self.pending_level:
                await self.load_pending_level()
            self.clock.tick(FPS)
            await asyncio.sleep(0)

        pygame.quit()


asyncio.run(Game().run())
