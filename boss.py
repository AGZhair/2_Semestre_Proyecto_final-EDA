import pygame

from settings import *


class Boss:

    def __init__(self, x, y):

        # =========================
        # HITBOX
        # =========================

        self.rect = pygame.Rect(
            x,
            y,
            140,
            140
        )

        # =========================
        # STATS
        # =========================

        self.max_health = 350
        self.health = self.max_health

        self.damage = 10
        self.speed = 120

        self.is_dead = False
        self.facing_right = False

        # =========================
        # PHYSICS
        # =========================

        self.velocity_y = 0
        self.on_ground = False

        # =========================
        # ATTACK
        # =========================

        self.is_attacking = False

        self.attack_cooldown = 0

        self.attack_rect = pygame.Rect(
            0,
            0,
            170,
            140
        )

        self.has_hit = False

        self.attack_hit_frame = 8

        self.hit_flash_timer = 0

        # IMPORTANTE:
        # indica que la animación completa terminó.
        self.attack_finished = False

        # =========================
        # STATE
        # =========================

        self.state = "idle"

        # =========================
        # ANIMATION
        # =========================

        self.animation_timer = 0
        self.animation_speed = 0.08
        self.current_frame = 0

        # =========================
        # LOAD SHEETS
        # =========================

        self.idle_sheet = pygame.image.load(
            "assets/boss/boss_idle.png"
        ).convert_alpha()

        self.run_sheet = pygame.image.load(
            "assets/boss/boss_run.png"
        ).convert_alpha()

        self.attack_sheet = pygame.image.load(
            "assets/boss/boss_attack.png"
        ).convert_alpha()

        self.dead_sheet = pygame.image.load(
            "assets/boss/boss_dead.png"
        ).convert_alpha()

        # =========================
        # LOAD FRAMES
        # =========================

        self.idle_frames = self.load_frames(
            self.idle_sheet,
            7
        )

        self.run_frames = self.load_frames(
            self.run_sheet,
            7
        )

        self.attack_frames = self.load_frames(
            self.attack_sheet,
            16
        )

        self.dead_frames = self.load_frames(
            self.dead_sheet,
            3
        )

        self.image = self.idle_frames[0]

    # =========================
    # LOAD FRAMES
    # =========================

    def load_frames(self, sheet, count):

        frames = []

        frame_width = (
            sheet.get_width() // count
        )

        frame_height = sheet.get_height()

        for i in range(count):

            frame = sheet.subsurface(
                (
                    i * frame_width,
                    0,
                    frame_width,
                    frame_height
                )
            )

            frame = pygame.transform.scale(
                frame,
                (256, 256)
            )

            frames.append(frame)

        return frames

    # =========================
    # GRAVITY
    # =========================

    def apply_gravity(self, dt, platforms):

        self.velocity_y += GRAVITY * dt

        self.rect.y += self.velocity_y * dt

        self.on_ground = False

        for platform in platforms:

            if self.rect.colliderect(platform.rect):

                if self.velocity_y > 0:

                    self.rect.bottom = platform.rect.top

                    self.velocity_y = 0

                    self.on_ground = True

    # =========================
    # UPDATE
    # =========================

    def update(
        self,
        dt,
        player,
        platforms
    ):

        self.apply_gravity(
            dt,
            platforms
        )

        if self.hit_flash_timer > 0:

            self.hit_flash_timer -= dt

        # =========================
        # COOLDOWN
        # =========================

        if self.attack_cooldown > 0:

            self.attack_cooldown -= dt

        # =========================
        # DEAD
        # =========================

        if self.is_dead:

            self.state = "dead"

            self.is_attacking = False

            self.attack_rect.x = -9999
            self.attack_rect.y = -9999

            self.update_animation(dt)

            return

        # =====================================================
        # CONTINUAR ATAQUE
        # =====================================================

        if self.is_attacking:

            self.state = "attack"

            # -------------------------
            # HITBOX
            # -------------------------

            if self.current_frame == self.attack_hit_frame:

                if self.facing_right:

                    self.attack_rect.x = (
                        self.rect.right
                    )

                else:

                    self.attack_rect.x = (
                        self.rect.left - 140
                    )

                self.attack_rect.y = self.rect.y

            else:

                self.attack_rect.x = -9999
                self.attack_rect.y = -9999

            # -------------------------
            # DAÑO AL JUGADOR
            # -------------------------

            if (
                self.attack_rect.colliderect(player.rect)
                and not self.has_hit
            ):

                player.take_damage(
                    self.damage,
                    self.rect.centerx
                )

                self.has_hit = True

            # -------------------------
            # ANIMACIÓN
            # -------------------------

            self.attack_finished = False

            self.update_animation(dt)

            # -------------------------
            # TERMINÓ ATAQUE
            # -------------------------

            if self.attack_finished:

                self.is_attacking = False

                self.state = "idle"

                self.attack_cooldown = 2.0

                self.has_hit = False

                self.attack_finished = False

                self.attack_rect.x = -9999
                self.attack_rect.y = -9999

            return

        # =========================
        # DISTANCIA
        # =========================

        distance = abs(
            player.rect.centerx
            - self.rect.centerx
        )

        # =========================
        # START ATTACK
        # =========================

        if (
            distance < 140
            and self.attack_cooldown <= 0
        ):

            self.state = "attack"

            self.is_attacking = True

            self.has_hit = False

            self.attack_finished = False

            self.current_frame = 0

            self.animation_timer = 0

            self.attack_rect.x = -9999
            self.attack_rect.y = -9999

            return

        # =========================
        # RUN
        # =========================

        self.state = "run"

        move_speed = self.speed * dt

        if player.rect.centerx < self.rect.centerx:

            self.rect.x -= move_speed

            self.facing_right = False

        else:

            self.rect.x += move_speed

            self.facing_right = True

        self.update_animation(dt)

    # =========================
    # ANIMATION
    # =========================

    def update_animation(self, dt):

        self.animation_timer += dt

        if self.animation_timer >= self.animation_speed:

            self.animation_timer = 0

            self.current_frame += 1

            # =========================
            # IDLE
            # =========================

            if self.state == "idle":

                if self.current_frame >= len(
                    self.idle_frames
                ):

                    self.current_frame = 0

                self.image = self.idle_frames[
                    self.current_frame
                ]

            # =========================
            # RUN
            # =========================

            elif self.state == "run":

                if self.current_frame >= len(
                    self.run_frames
                ):

                    self.current_frame = 0

                self.image = self.run_frames[
                    self.current_frame
                ]

            # =========================
            # ATTACK
            # =========================

            elif self.state == "attack":

                if self.current_frame >= len(
                    self.attack_frames
                ):

                    self.current_frame = 0

                    self.attack_finished = True

                self.image = self.attack_frames[
                    self.current_frame
                ]

            # =========================
            # DEAD
            # =========================

            elif self.state == "dead":

                if self.current_frame >= len(
                    self.dead_frames
                ):

                    self.current_frame = (
                        len(self.dead_frames) - 1
                    )

                self.image = self.dead_frames[
                    self.current_frame
                ]

    # =========================
    # DAMAGE
    # =========================

    def take_damage(self, damage, player):

        final_damage = damage

        self.health -= final_damage

        self.hit_flash_timer = HIT_FLASH_TIME

        if self.health <= 0:

            self.health = 0

            self.is_dead = True

            self.is_attacking = False

            self.attack_finished = False

            self.attack_rect.x = -9999
            self.attack_rect.y = -9999

            self.current_frame = 0
            self.animation_timer = 0

        return final_damage

    # =========================
    # DRAW
    # =========================

    def draw(self, screen, camera):

        image = self.image

        if not self.facing_right:

            image = pygame.transform.flip(
                image,
                True,
                False
            )

        # Hit flash: silueta blanca al recibir daño.
        if self.hit_flash_timer > 0:

            image = pygame.mask.from_surface(
                image
            ).to_surface(
                setcolor=(255, 255, 255, 255),
                unsetcolor=(0, 0, 0, 0)
            )

        draw_x = (
            self.rect.x
            - camera.offset_x
            - 70
        )

        draw_y = self.rect.y - 120

        screen.blit(
            image,
            (draw_x, draw_y)
        )

        # =========================
        # BOSS HP BAR
        # =========================

        if not self.is_dead:

            pygame.draw.rect(
                screen,
                (40, 0, 0),
                (
                    200,
                    20,
                    800,
                    30
                ),
                border_radius=10
            )

            current_width = (
                self.health
                / self.max_health
            ) * 800

            pygame.draw.rect(
                screen,
                (220, 40, 40),
                (
                    200,
                    20,
                    current_width,
                    30
                ),
                border_radius=10
            )