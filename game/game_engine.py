import pygame
import random
from .fruit import Fruit

WHITE = (255, 255, 255)
BOMB_BLACK = (30, 30, 30)
FRUIT_COLORS = [(220, 60, 60), (230, 140, 40), (230, 200, 40), (90, 180, 90)]

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.fruits = []
        self.trail = []

        self.spawn_interval = 55
        self._spawn_timer = 0
        self.bomb_chance = 0.15
        self.speed_scale = 1.0

        self.lives = 3
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 28)
        self.game_over_font = pygame.font.SysFont("Arial", 60)
        self.final_score_font = pygame.font.SysFont("Arial", 36)

        self.game_over = False

    def spawn_fruit(self):
        x = random.randint(60, self.width - 60)
        vy = -random.uniform(13, 16) * self.speed_scale
        vx = random.uniform(-2, 2)
        gravity = 0.35
        kind = "bomb" if random.random() < self.bomb_chance else "fruit"

        fruit = Fruit(x, self.height + 30, vx, vy, gravity, kind=kind)
        fruit.color = BOMB_BLACK if kind == "bomb" else random.choice(FRUIT_COLORS)

        self.fruits.append(fruit)

    def handle_event(self, event):
        if self.game_over:
            return

        if event.type == pygame.MOUSEMOTION:
            self._handle_motion(event.pos)

    def _segment_hits_circle(self, start, end, fruit):
        x1, y1 = start
        x2, y2 = end

        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            return fruit.contains_point(x1, y1)

        length_squared = dx * dx + dy * dy

        t = ((fruit.x - x1) * dx + (fruit.y - y1) * dy) / length_squared
        t = max(0, min(1, t))

        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        distance_squared = (
            (fruit.x - closest_x) ** 2 +
            (fruit.y - closest_y) ** 2
        )

        return distance_squared <= fruit.radius ** 2

    def _handle_motion(self, pos):
        previous_pos = self.trail[-1] if self.trail else pos

        for fruit in self.fruits:
            if not fruit.sliced and self._segment_hits_circle(previous_pos, pos, fruit):
                self._slice(fruit)

        self.trail.append(pos)

        if len(self.trail) > 15:
            self.trail.pop(0)

    def _slice(self, fruit):
        fruit.sliced = True

        if fruit.kind == "bomb":
            self.game_over = True
        else:
            self.score += 1

    def handle_input(self):
        pass

    def update(self):
        if self.game_over:
            return

        self._spawn_timer += 1

        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.spawn_fruit()

        still_alive = []

        for fruit in self.fruits:
            fruit.update()

            if fruit.sliced:
                continue

            if fruit.off_screen(self.height):
                if fruit.kind == "fruit":
                    self.lives -= 1
                continue

            still_alive.append(fruit)

        self.fruits = still_alive

        if self.lives <= 0:
            self.game_over = True

    def render(self, screen):
        for fruit in self.fruits:
            color = getattr(fruit, "color", WHITE)

            pygame.draw.circle(
                screen,
                color,
                (int(fruit.x), int(fruit.y)),
                fruit.radius
            )

        if len(self.trail) >= 2 and not self.game_over:
            pygame.draw.lines(screen, WHITE, False, self.trail, 3)

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            WHITE
        )
        screen.blit(score_text, (10, 10))

        lives_text = self.font.render(
            f"Lives: {self.lives}",
            True,
            WHITE
        )
        screen.blit(lives_text, (self.width - 130, 10))

        if self.game_over:
            self.render_game_over(screen)

    def render_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        game_over_text = self.game_over_font.render(
            "GAME OVER",
            True,
            WHITE
        )

        score_text = self.final_score_font.render(
            f"Final Score: {self.score}",
            True,
            WHITE
        )

        game_over_rect = game_over_text.get_rect(
            center=(self.width // 2, self.height // 2 - 40)
        )

        score_rect = score_text.get_rect(
            center=(self.width // 2, self.height // 2 + 35)
        )

        screen.blit(game_over_text, game_over_rect)
        screen.blit(score_text, score_rect)