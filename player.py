import os
import pygame

from settings import *
from utils import load_spritesheet


class Player:

    def __init__(self, character_data):

        self.character_name = character_data["name"]
        self.attack_hit_frame = character_data["attack_hit_frame"]

        self.rect = pygame.Rect(
            200,
            300,
            80,
            100
        )

        # =========================
        # MOVEMENT
        # =========================

        self.velocity_y = 0

        self.speed = character_data["speed"]

        self.on_ground = False

        self.facing_right = True

        # =========================
        # STATS
        # =========================

        self.max_health = character_data["health"]

        self.health = self.max_health

        self.damage = character_data["damage"]

        # =========================
        # DAMAGE SYSTEM
        # =========================

        self.damage_cooldown = 0

        self.invulnerable = False

        self.knockback_velocity = 0

        self.knockback_timer = 0

        self.knockback_duration = 0.22

        self.is_dead = False

        # =========================
        # ATTACK SYSTEM
        # =========================

        self.is_attacking = False

        self.has_hit = False

        self.attack_timer = 0

        self.attack_cooldown_timer = 0

        self.attack_width = character_data["attack_width"]

        self.attack_rect = pygame.Rect(
            0,
            0,
            self.attack_width,
            ATTACK_HEIGHT
        )

        # =========================
        # DASH
        # =========================

        self.is_dashing = False

        self.dash_timer = 0

        self.dash_cooldown_timer = 0

        self.dash_direction = 1

        # =========================
        # ANIMATION
        # =========================

        self.animations = {}

        self.load_animations()

        self.current_animation = "idle"

        self.frame_index = 0

        self.animation_timer = 0

        self.death_timer = 0

        # =========================
        # GAME FEEL: salto y combo
        # =========================

        self.coyote_timer = 0

        self.jump_buffer_timer = 0

        self.just_landed = False

        self.combo_index = 0

        self.combo_timer = 0

        self.animation_speed = 0.07

        self.animation_speeds = {
            "idle": 0.07,
            "walk": 0.07,
            "run": 0.055,
            "jump": 0.16,
            "attack": 0.06,
            "dead": 0.1,
        }

        self.walk_timer = 0

        self.image = self.animations["idle"][0]

    # =========================
    # LOAD ANIMATIONS
    # =========================

    def load_animations(self):

        folder = self.character_name.lower()

        folder_map = {
            "samurai": "warrior",
            "caballero": "archer",
            "hechicera": "mage"
        }

        folder = folder_map.get(folder, folder)

        base_path = os.path.join(
            "assets",
            "player",
            folder
        )

        attack_file = (
            "Attack_1.png"
            if folder == "archer"
            else "Attack_1.png"
        )

        self.animations["idle"] = load_spritesheet(
            os.path.join(base_path, "Idle.png"),
            128,
            128
        )

        self.animations["walk"] = load_spritesheet(
            os.path.join(base_path, "Walk.png"),
            128,
            128
        )

        self.animations["run"] = load_spritesheet(
            os.path.join(base_path, "Run.png"),
            128,
            128
        )

        self.animations["jump"] = load_spritesheet(
            os.path.join(base_path, "Jump.png"),
            128,
            128
        )

        self.animations["attack"] = load_spritesheet(
            os.path.join(base_path, attack_file),
            128,
            128
        )

        self.animations["dead"] = load_spritesheet(
            os.path.join(base_path, "Dead.png"),
            128,
            128
        )

    # =========================
    # INPUT
    # =========================

    def handle_input(self, dt):

        if self.is_dead:

            self.current_animation = "dead"

            return

        keys = pygame.key.get_pressed()

        moving = False

        # =========================
        # MOVEMENT
        # =========================

        # Mientras recibe knockback,
        # el jugador no puede contrarrestarlo
        # caminando.
        if (
            not self.is_attacking
            and self.knockback_timer <= 0
        ):

            if keys[pygame.K_a]:

                self.rect.x -= self.speed * dt

                self.facing_right = False

                moving = True

            if keys[pygame.K_d]:

                self.rect.x += self.speed * dt

                self.facing_right = True

                moving = True

        if moving:

            self.walk_timer += dt

        else:

            self.walk_timer = 0

        # =========================
        # JUMP (buffer + coyote + variable)
        # =========================

        if keys[pygame.K_SPACE]:

            self.jump_buffer_timer = JUMP_BUFFER

        if (
            self.jump_buffer_timer > 0
            and (
                self.on_ground
                or self.coyote_timer > 0
            )
            and self.knockback_timer <= 0
        ):

            self.velocity_y = JUMP_FORCE

            self.on_ground = False

            self.coyote_timer = 0

            self.jump_buffer_timer = 0

        # Soltar el salto corta el impulso
        # y permite saltos cortos o largos.
        if (
            not keys[pygame.K_SPACE]
            and self.velocity_y < -350
        ):

            self.velocity_y = -350

        # =========================
        # ATTACK
        # =========================

        if (
            keys[pygame.K_j]
            and self.knockback_timer <= 0
        ):

            self.attack()

        # =========================
        # DASH
        # =========================

        if (
            keys[pygame.K_LSHIFT]
            and self.knockback_timer <= 0
        ):

            self.dash()

        # =========================
        # ANIMATION STATE
        # =========================

        if self.is_attacking:

            self.current_animation = "attack"

        elif not self.on_ground:

            self.current_animation = "jump"

        elif moving:

            if self.walk_timer > 1.0:

                self.current_animation = "run"

            else:

                self.current_animation = "walk"

        else:

            self.current_animation = "idle"

    # =========================
    # ATTACK
    # =========================

    def attack(self):

        # Encadenar combo: si el golpe actual ya pasó
        # su frame de impacto, se corta y empieza
        # el siguiente golpe de la cadena.
        if self.attack_cooldown_timer > 0:

            if (
                self.is_attacking
                and self.frame_index >= self.attack_hit_frame
            ):

                self.is_attacking = False

                self.attack_cooldown_timer = 0

                self.combo_index = (
                    self.combo_index + 1
                ) % len(COMBO_DAMAGE)

                self._start_attack()

            return

        if not self.is_attacking:

            if self.combo_timer <= 0:

                self.combo_index = 0

            self._start_attack()

    def _start_attack(self):

        self.is_attacking = True

        self.frame_index = 0

        self.has_hit = False

        self.attack_timer = ATTACK_DURATION

        self.attack_cooldown_timer = ATTACK_COOLDOWN

        self.combo_timer = COMBO_WINDOW

    def current_attack_damage(self):
        """Daño del golpe actual de la cadena de combo."""

        return max(
            1,
            round(self.damage * COMBO_DAMAGE[self.combo_index])
        )

    # =========================
    # DASH
    # =========================

    def dash(self):

        if self.dash_cooldown_timer <= 0:

            self.is_dashing = True

            self.dash_timer = DASH_DURATION

            self.dash_cooldown_timer = DASH_COOLDOWN

            if self.facing_right:

                self.dash_direction = 1

            else:

                self.dash_direction = -1

    # =========================
    # UPDATE ATTACK
    # =========================

    def update_attack(self, dt):

        if self.attack_cooldown_timer > 0:

            self.attack_cooldown_timer -= dt

        # La ventana de combo solo corre
        # cuando no estamos atacando.
        if (
            not self.is_attacking
            and self.combo_timer > 0
        ):

            self.combo_timer -= dt

            if self.combo_timer <= 0:

                self.combo_index = 0

        if self.is_attacking:

            self.attack_timer -= dt

            # =========================
            # HIT FRAME
            # =========================

            if self.frame_index == self.attack_hit_frame:

                if self.facing_right:

                    self.attack_rect.x = (
                        self.rect.centerx - 10
                    )

                else:

                    self.attack_rect.x = (
                        self.rect.centerx
                        - self.attack_width
                        + 19.9
                    )

                self.attack_rect.y = (
                    self.rect.y + 55
                )

            else:

                self.attack_rect.x = -9999

                self.attack_rect.y = -9999

            if self.attack_timer <= 0:

                self.is_attacking = False

                self.combo_timer = COMBO_WINDOW

    # =========================
    # UPDATE DASH
    # =========================

    def update_dash(self, dt):

        if self.dash_cooldown_timer > 0:

            self.dash_cooldown_timer -= dt

        if self.is_dashing:

            self.rect.x += (
                self.dash_direction
                * DASH_SPEED
                * dt
            )

            self.dash_timer -= dt

            if self.dash_timer <= 0:

                self.is_dashing = False

    # =========================
    # TAKE DAMAGE
    # =========================

    def take_damage(self, amount, enemy_x):

        # I-frames del dash: una esquiva a tiempo
        # evita el daño por completo.
        if self.is_dashing:

            return

        if self.damage_cooldown <= 0:

            self.health -= amount

            self.damage_cooldown = (
                PLAYER_DAMAGE_COOLDOWN
            )

            self.invulnerable = True

            # =========================
            # KNOCKBACK
            # =========================

            if self.rect.centerx < enemy_x:

                # Enemigo está a la derecha
                self.knockback_velocity = -650

            else:

                # Enemigo está a la izquierda
                self.knockback_velocity = 650

            self.knockback_timer = self.knockback_duration

            # Cancelar acciones actuales
            self.is_attacking = False

            self.is_dashing = False

            self.combo_index = 0

            self.combo_timer = 0

            # =========================
            # MUERTE
            # =========================

            if self.health <= 0:

                self.health = 0

                self.is_dead = True

                self.is_attacking = False

                self.is_dashing = False

                self.knockback_velocity = 0

                self.knockback_timer = 0

                self.current_animation = "dead"

                self.frame_index = 0

                self.animation_timer = 0

                self.death_timer = 0

    # =========================
    # DAMAGE COOLDOWN
    # =========================

    def update_damage_cooldown(self, dt):

        if self.damage_cooldown > 0:

            self.damage_cooldown -= dt

        else:

            self.invulnerable = False

    # =========================
    # KNOCKBACK
    # =========================

    def update_knockback(self, dt):

        if self.knockback_timer > 0:

            self.rect.x += (
                self.knockback_velocity * dt
            )

            self.knockback_timer -= dt

            # Frenado progresivo
            self.knockback_velocity *= 0.82

        else:

            self.knockback_velocity = 0

    # =========================
    # GRAVITY
    # =========================

    def apply_gravity(self, dt, platforms):

        self.velocity_y += GRAVITY * dt

        fall_speed = self.velocity_y

        was_ground = self.on_ground

        self.rect.y += self.velocity_y * dt

        self.on_ground = False

        for platform in platforms:

            if self.rect.colliderect(platform.rect):

                if self.velocity_y > 0:

                    self.rect.bottom = (
                        platform.rect.top
                    )

                    self.velocity_y = 0

                    self.on_ground = True

        # Aterrizaje fuerte: main.py lo usa
        # para soltar polvo.
        self.just_landed = (
            not was_ground
            and self.on_ground
            and fall_speed > LAND_DUST_THRESHOLD
        )

    # =========================
    # ANIMATION
    # =========================

    def update_animation(self, dt):

        speed = self.animation_speeds.get(
            self.current_animation,
            self.animation_speed
        )

        self.animation_timer += dt

        if self.animation_timer >= speed:

            self.animation_timer = 0

            animation = self.animations[
                self.current_animation
            ]

            # =========================
            # MUERTE
            # =========================

            if self.current_animation == "dead":

                if self.frame_index < len(animation) - 1:

                    self.frame_index += 1

                self.image = animation[
                    self.frame_index
                ]

                return

            # =========================
            # ANIMACIONES NORMALES
            # =========================

            self.frame_index += 1

            if self.frame_index >= len(animation):

                if self.current_animation == "attack":

                    self.is_attacking = False

                    self.combo_timer = COMBO_WINDOW

                    self.frame_index = 0

                else:

                    self.frame_index = 0

            # Asegurar que frame_index esté dentro del rango válido
            self.frame_index = self.frame_index % len(animation)

            self.image = animation[
                self.frame_index
            ]

    # =========================
    # CAN ATTACK HIT
    # =========================

    def can_attack_hit(self):

        if not self.is_attacking:

            return False

        return (
            self.frame_index
            == self.attack_hit_frame
        )

    # =========================
    # UPDATE
    # =========================

    def update(self, dt, platforms):

        if self.jump_buffer_timer > 0:

            self.jump_buffer_timer -= dt

        self.handle_input(dt)

        self.apply_gravity(
            dt,
            platforms
        )

        if self.on_ground:

            self.coyote_timer = COYOTE_TIME

        else:

            self.coyote_timer -= dt

        self.update_dash(dt)

        self.update_damage_cooldown(dt)

        self.update_knockback(dt)

        # IMPORTANTE:
        # La animación se actualiza ANTES
        # de calcular el ataque.
        #
        # Esto fue lo que solucionó
        # nuestro problema anterior.

        self.update_animation(dt)

        self.update_attack(dt)

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

        shake = camera.get_shake_offset()

        screen.blit(
            image,
            (
                self.rect.x
                - int(camera.offset_x)
                - 20
                + shake,

                self.rect.y
                - 28
                + shake
            )
        )