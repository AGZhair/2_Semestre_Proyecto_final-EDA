import pygame
import random
import math


class HitSpark:

    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.timer = 0.12
        self.is_dead = False

        # Cantidad de rayos del impacto
        self.rays = []

        for _ in range(8):

            angle = random.uniform(
                0,
                math.pi * 2
            )

            speed = random.uniform(
                180,
                350
            )

            self.rays.append({
                "angle": angle,
                "speed": speed,
                "length": random.randint(8, 18)
            })

    def update(self, dt):

        self.timer -= dt

        if self.timer <= 0:

            self.is_dead = True

    def draw(self, screen, camera):

        draw_x = (
            self.x
            - camera.offset_x
        )

        draw_y = self.y

        shake = camera.get_shake_offset()

        draw_x += shake
        draw_y += shake

        # Destello central
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (
                int(draw_x),
                int(draw_y)
            ),
            5
        )

        # Rayos del impacto
        for ray in self.rays:

            angle = ray["angle"]

            speed = ray["speed"]

            length = ray["length"]

            progress = (
                1
                - self.timer / 0.12
            )

            distance = (
                speed
                * progress
                * 0.12
            )

            start_x = (
                draw_x
                + math.cos(angle)
                * distance
            )

            start_y = (
                draw_y
                + math.sin(angle)
                * distance
            )

            end_x = (
                draw_x
                + math.cos(angle)
                * (distance + length)
            )

            end_y = (
                draw_y
                + math.sin(angle)
                * (distance + length)
            )

            pygame.draw.line(
                screen,
                (255, 220, 120),
                (
                    int(start_x),
                    int(start_y)
                ),
                (
                    int(end_x),
                    int(end_y)
                ),
                3
            )