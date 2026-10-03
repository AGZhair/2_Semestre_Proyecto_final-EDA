import pygame
import random

class Particle:
    def __init__(self, x, y, color=None):

        self.x = x
        self.y = y

        self.size = random.randint(4, 8)

        self.velocity_x = random.uniform(-250, 250)
        self.velocity_y = random.uniform(-250, 250)

        self.life = random.uniform(0.3, 0.6)

        if color is None:

            self.color = (
                random.randint(200,255),
                random.randint(180,255),
                random.randint(50,100)
            )

        else:

            self.color = color

    def update(self, dt):

        self.life -= dt

        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        # gravedad leve
        self.velocity_y += 500 * dt

    def draw(self, screen, camera):

        pygame.draw.rect(
            screen,
            self.color,
            (
                self.x - camera.offset_x + camera.get_shake_offset(),
                self.y + camera.get_shake_offset(),
                self.size,
                self.size
            )
        )

    def is_dead(self):

        return self.life <= 0