import pygame
import random

from settings import *


class Enemy:

    def __init__(self, x, y):

        # =========================
        # HITBOX
        # =========================

        self.rect = pygame.Rect(
            x,
            y,
            60,
            70
        )

        # =========================
        # PHYSICS
        # =========================

        self.velocity_y = 0
        self.on_ground = False

        # =========================
        # STATS
        # =========================

        self.speed = 200

        self.health = 3 + random.randint(0, 2)
        self.max_health = self.health

        self.damage = 1

        self.is_dead = False

        self.facing_right = False

        # =========================
        # ATTACK SYSTEM
        # =========================

        self.is_attacking = False
        self.has_hit = False

        self.attack_cooldown = 0

        self.attack_rect = pygame.Rect(
            0,
            0,
            70,
            80
        )

        # =========================
        # KNOCKBACK
        # =========================

        self.knockback_velocity = 0
        self.stun_timer = 0

        self.hit_flash_timer = 0

        # =========================
        # HEALTH BAR
        # =========================

        self.show_health_bar = False
        self.health_bar_timer = 0

        # =========================
        # ANIMATION
        # =========================

        self.animation_timer = 0
        self.animation_speed = 0.10

        self.current_frame = 0
        self.state = "idle"

        # Esta variable nos dice si
        # la animación de ataque terminó.
        self.attack_finished = False

        # =========================
        # LOAD SPRITES
        # =========================

        self.idle_sheet = pygame.image.load(
            "assets/enemies/idle.png"
        ).convert_alpha()

        self.run_sheet = pygame.image.load(
            "assets/enemies/run.png"
        ).convert_alpha()

        self.attack_sheet = pygame.image.load(
            "assets/enemies/attack.png"
        ).convert_alpha()

        self.idle_frames = self.load_frames(
            self.idle_sheet,
            7
        )

        self.run_frames = self.load_frames(
            self.run_sheet,
            8
        )

        self.attack_frames = self.load_frames(
            self.attack_sheet,
            5
        )

        self.image = self.idle_frames[0]

    # =========================
    # LOAD FRAMES
    # =========================

    def load_frames(self, sheet, frame_count):

        frames = []

        frame_width = (
            sheet.get_width() // frame_count
        )

        frame_height = sheet.get_height()

        for i in range(frame_count):

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
                (128, 128)
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

    def update(self, dt, player, platforms):

        self.apply_gravity(
            dt,
            platforms
        )

        if self.hit_flash_timer > 0:

            self.hit_flash_timer -= dt

        # =========================
        # HEALTH BAR TIMER
        # =========================

        if self.health_bar_timer > 0:

            self.health_bar_timer -= dt

        else:

            self.show_health_bar = False

        # =========================
        # ATTACK COOLDOWN
        # =========================

        if self.attack_cooldown > 0:

            self.attack_cooldown -= dt

        # =========================
        # STUN
        # =========================

        if self.stun_timer > 0:

            self.stun_timer -= dt

            self.attack_rect.x = -9999
            self.attack_rect.y = -9999

            self.update_animation(dt)

            return

        # =========================
        # KNOCKBACK
        # =========================

        if abs(self.knockback_velocity) > 1:

            self.rect.x += (
                self.knockback_velocity * dt
            )

            self.knockback_velocity *= 0.85

            self.state = "hurt"

            self.is_attacking = False

            self.attack_rect.x = -9999
            self.attack_rect.y = -9999

            self.update_animation(dt)

            return

        # =====================================================
        # ATAQUE ACTUAL
        # =====================================================

        if self.is_attacking:

            self.state = "attack"

            # -------------------------
            # HITBOX
            # -------------------------

            if self.current_frame == 2:

                if self.facing_right:

                    self.attack_rect.x = (
                        self.rect.right - 10
                    )

                else:

                    self.attack_rect.x = (
                        self.rect.left - 60
                    )

                self.attack_rect.y = (
                    self.rect.y + 10
                )

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
            # TERMINÓ EL ATAQUE
            # -------------------------

            if self.attack_finished:

                self.is_attacking = False

                self.state = "idle"

                self.attack_cooldown = 1.0

                self.has_hit = False

                self.attack_finished = False

                self.attack_rect.x = -9999
                self.attack_rect.y = -9999

            return

        # =========================
        # DISTANCIA AL JUGADOR
        # =========================

        horizontal_distance = abs(
            player.rect.centerx
            - self.rect.centerx
        )

        vertical_distance = abs(
            player.rect.centery
            - self.rect.centery
        )

        can_see_player = (
            horizontal_distance < 600
            and vertical_distance < 100
        )

        if not can_see_player:

            self.state = "idle"

            self.attack_rect.x = -9999
            self.attack_rect.y = -9999

            self.update_animation(dt)

            return

        distance = horizontal_distance

        # =========================
        # START ATTACK
        # =========================

        if (
            distance < 70
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
        # MOVEMENT
        # =========================

        if distance <= 70:

            self.state = "idle"

            self.attack_rect.x = -9999
            self.attack_rect.y = -9999

            self.update_animation(dt)

            return


        self.state = "run"

        move_speed = self.speed * dt

        if player.rect.x < self.rect.x:

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
            # HURT
            # =========================

            elif self.state == "hurt":

                self.image = self.run_frames[0]

    # =========================
    # DAMAGE
    # =========================

    def take_damage(self, damage, player):

        final_damage = damage

        self.health -= final_damage

        self.show_health_bar = True
        self.health_bar_timer = 2

        self.hit_flash_timer = HIT_FLASH_TIME

        self.stun_timer = 0.25

        if player.facing_right:

            self.knockback_velocity = 450

        else:

            self.knockback_velocity = -450

        self.is_attacking = False

        self.attack_finished = False

        self.attack_rect.x = -9999
        self.attack_rect.y = -9999

        if self.health <= 0:

            self.health = 0

            self.is_dead = True

        return final_damage

    # =========================
    # DRAW
    # =========================

    def draw(self, screen, camera):

        draw_x = (
            self.rect.x
            - int(camera.offset_x)
            - 34
        )

        draw_y = self.rect.y - 58

        shake = camera.get_shake_offset()

        draw_x += shake
        draw_y += shake

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

        screen.blit(
            image,
            (draw_x, draw_y)
        )

        # =========================
        # HEALTH BAR
        # =========================

        if self.show_health_bar:

            bar_width = 60
            bar_height = 8

            health_ratio = (
                self.health / self.max_health
            )

            current_width = (
                bar_width * health_ratio
            )

            pygame.draw.rect(
                screen,
                (60, 0, 0),
                (
                    self.rect.x
                    - int(camera.offset_x),

                    self.rect.y - 18,

                    bar_width,
                    bar_height
                ),
                border_radius=4
            )

            pygame.draw.rect(
                screen,
                (255, 50, 50),
                (
                    self.rect.x
                    - int(camera.offset_x),

                    self.rect.y - 18,

                    current_width,
                    bar_height
                ),
                border_radius=4
            )