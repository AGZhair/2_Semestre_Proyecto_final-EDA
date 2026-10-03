import pygame
import random

from settings import GRAVITY


class Decoration:

    def __init__(self, image, x, y):

        self.image = image

        self.x = x

        self.y = y

        # PHYSICS
        self.velocity_y = 0

        self.on_ground = False

        # HITBOX
        self.rect = pygame.Rect(
            self.x,
            self.y,
            image.get_width(),
            image.get_height()
        )

    # =========================
    # GRAVITY
    # =========================

    def apply_gravity(
        self,
        dt,
        platforms
    ):

        self.velocity_y += GRAVITY * dt

        self.y += self.velocity_y * dt

        self.rect.y = self.y

        self.on_ground = False

        for platform in platforms:

            if self.rect.colliderect(platform.rect):

                if self.velocity_y > 0:

                    self.rect.bottom = (
                        platform.rect.top
                    )

                    self.y = self.rect.y

                    self.velocity_y = 0

                    self.on_ground = True

    # =========================
    # UPDATE
    # =========================

    def update(
        self,
        dt,
        platforms
    ):

        if not self.on_ground:

            self.apply_gravity(
                dt,
                platforms
            )

    # =========================
    # DRAW
    # =========================

    def draw(self, screen, camera):

        screen.blit(
            self.image,
            (
                self.x - int(camera.offset_x),
                self.y
            )
        )


class DecorationManager:

    def __init__(self):

        self.decorations = []

        self.load_assets()

        self.generate_world()

    # =========================
    # LOAD IMAGES
    # =========================

    def load_assets(self):

        self.trees = []

        self.rocks = []

        # TREES
        for i in range(1, 7):

            image = pygame.image.load(
                f"assets/decorations/tree_{i}.png"
            ).convert_alpha()

            self.trees.append(image)

        # ROCKS
        for i in range(1, 7):

            image = pygame.image.load(
                f"assets/props/rock_{i}.png"
            ).convert_alpha()

            self.rocks.append(image)

    # =========================
    # GENERATE WORLD
    # =========================

    def generate_world(self):

        # TREES
        for x in range(300, 12000, 700):

            image = random.choice(self.trees)

            # MÁS ARRIBA
            y = random.randint(0, 250)

            self.decorations.append(
                Decoration(
                    image,
                    x,
                    y
                )
            )

        # ROCKS
        for x in range(200, 12000, 450):

            image = random.choice(self.rocks)

            # MÁS ARRIBA
            y = random.randint(0, 250)

            self.decorations.append(
                Decoration(
                    image,
                    x,
                    y
                )
            )

    # =========================
    # UPDATE
    # =========================

    def update(
        self,
        dt,
        platforms
    ):

        for decoration in self.decorations:

            decoration.update(
                dt,
                platforms
            )

    # =========================
    # DRAW
    # =========================

    def draw(self, screen, camera):

        for decoration in self.decorations:

            decoration.draw(screen, camera)