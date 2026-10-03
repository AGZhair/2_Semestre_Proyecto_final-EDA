import pygame
import sys
import random

from boss import Boss
from decoration import DecorationManager
from tilemap import TileMap
from hit_spark import HitSpark
from world import Platform
from camera import Camera
from particle import Particle
from settings import *
from player import Player
from enemy import Enemy
from damage_text import DamageText
from character_menu import CharacterMenu
from rpg_system import RPGManager

pygame.init()
pygame.mixer.init()

# =========================
# WINDOW
# =========================

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption(TITLE)

clock = pygame.time.Clock()

# =========================
# AUDIO
# =========================

pygame.mixer.music.load(
    "assets/audio/music/bg_music.mp3"
)

pygame.mixer.music.set_volume(0.4)

pygame.mixer.music.play(-1)

attack_sound = pygame.mixer.Sound(
    "assets/audio/sfx/attack.wav"
)

hit_sound = pygame.mixer.Sound(
    "assets/audio/sfx/hit.wav"
)

# =========================
# BACKGROUND
# =========================

background = pygame.image.load(
    "assets/background/bg.png"
).convert_alpha()

background = pygame.transform.scale(
    background,
    (1600, HEIGHT)
)

# =========================
# FONTS
# =========================
font = pygame.font.SysFont(None, 50)

hud_font = pygame.font.SysFont(None, 32)


class Chest:

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 64, 48)

        self.opened = False

    def draw(self, screen, camera):

        draw_x = self.rect.x - int(camera.offset_x)

        draw_y = self.rect.y

        color = (
            200,
            150,
            50
        ) if not self.opened else (
            140,
            100,
            35
        )

        pygame.draw.rect(
            screen,
            color,
            (draw_x, draw_y, self.rect.width, self.rect.height),
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            (80, 50, 20),
            (draw_x + 8, draw_y + 10, self.rect.width - 16, self.rect.height - 20),
            2,
            border_radius=6
        )

        if self.opened:

            pygame.draw.line(
                screen,
                (255, 220, 120),
                (draw_x + 14, draw_y + 24),
                (draw_x + 50, draw_y + 24),
                4
            )


# =========================
# GAME STATES
# =========================

MENU = "menu"

CHARACTER_SELECT = "character_select"

CHARACTER_MENU = "character_menu"

PLAYING = "playing"

PAUSE = "pause"

GAME_OVER = "game_over"

game_state = MENU

# Estado al que regresamos cuando cerramos la pantalla de personaje.
character_menu_return_state = MENU

# =========================
# RPG SYSTEM
# =========================

rpg_manager = RPGManager(
    [WARRIOR, ARCHER, MAGE]
)

# =========================
# CHARACTER MENU
# =========================

character_menu = CharacterMenu(
    screen,
    rpg_manager
)


def sync_player_from_rpg():
    """Aplica al jugador los cambios realizados en el menú RPG."""

    if player is not None:
        rpg_manager.refresh_player_stats(player)


def open_character_menu(return_state):
    """Abre la pantalla de personaje y conserva el contexto actual."""

    global game_state
    global character_menu_return_state

    character_menu_return_state = return_state

    character_menu.set_context(return_state)

    if player is not None:
        character_menu.select_by_name(
            player.character_name
        )
        character_menu.set_context(return_state)

    game_state = CHARACTER_MENU


# =========================
# WORLD
# =========================

platforms = []

# =========================
# GENERATE WORLD
# =========================

world_length = 12000

x = 0

ground_y = 560

while x < world_length:

    # VARIACIÓN TERRENO
    if x % 1536 == 0:

        ground_y += random.choice(
            [-64, -32, 0, 32, 64]
        )

        # LIMITES
        ground_y = max(420, min(620, ground_y))

    # SUELO PRINCIPAL
    platforms.append(
        Platform(
            x,
            ground_y,
            512,
            HEIGHT - ground_y
        )
    )

    x += 512

camera = Camera()
tilemap = TileMap()
decorations = DecorationManager()

# =========================
# GAME OBJECTS
# =========================

player = None
boss = None

boss_spawned = False
boss_defeated = False
chest = None
reward_message = ""
reward_timer = 0
boss_banner_timer = 0

enemies = []
particles = []
hit_sparks = []
damage_texts = []

# =========================
# GAME DATA
# =========================

score = 0

kills = 0

checkpoints = [
    (200, 300),  # Inicio
    (2200, 300),  # Después de primer tramo
    (4200, 300),  # Medio
    (6200, 300),  # Más allá
    (8200, 300),  # Casi final
    (10200, 300)  # Antes del jefe
]

current_checkpoint = 0

enemy_spawn_timer = 0

enemy_spawn_delay = 4.0

hit_stop_timer = 0

# =========================
# START GAME
# =========================

def start_game(character_name):

    global player
    global enemies
    global particles
    global hit_sparks
    global damage_texts
    global score
    global kills
    global game_state
    global boss
    global boss_spawned
    global boss_defeated
    global chest
    global reward_message
    global reward_timer
    global boss_banner_timer
    global current_checkpoint

    rpg_manager.set_active_character(character_name)

    character_data = rpg_manager.get_character_data(
        character_name
    )

    player = Player(character_data)

    enemies = [

        Enemy(
            900,
            platforms[0].rect.y - 110
        ),

        Enemy(
            1200,
            platforms[0].rect.y - 110
        )
    ]

    particles = []

    hit_sparks = []

    damage_texts = []

    score = 0

    kills = 0

    game_state = PLAYING
    boss = None

    boss_spawned = False
    boss_defeated = False
    chest = None
    reward_message = ""
    reward_timer = 0
    boss_banner_timer = 0

    current_checkpoint = 0

# =========================
# RESPAWN
# =========================

def respawn():
    global player
    global enemies
    global particles
    global hit_sparks
    global damage_texts
    global game_state
    global enemy_spawn_timer

    # Reset player
    player.rect.x = checkpoints[current_checkpoint][0]
    player.rect.y = checkpoints[current_checkpoint][1]
    player.health = player.max_health
    player.is_dead = False
    player.current_animation = "idle"
    player.frame_index = 0
    player.animation_timer = 0
    player.image = player.animations["idle"][0]
    player.velocity_y = 0
    player.on_ground = False
    player.facing_right = True
    player.is_attacking = False
    player.has_hit = False
    player.attack_timer = 0
    player.attack_cooldown_timer = 0
    player.attack_rect.x = -9999
    player.attack_rect.y = -9999
    player.is_dashing = False
    player.dash_timer = 0
    player.dash_cooldown_timer = 0
    player.damage_cooldown = 0
    player.invulnerable = False
    player.knockback_velocity = 0
    player.knockback_timer = 0
    player.death_timer = 0

    # Clear enemies, particles, etc.
    enemies = []
    particles = []
    hit_sparks = []
    damage_texts = []

    # Reset spawn timer
    enemy_spawn_timer = 0

    game_state = PLAYING

# =========================
# MAIN LOOP
# =========================

running = True

while running:

    dt = clock.tick(FPS) / 1000

    # =========================
    # EVENTS
    # =========================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        # MENU
        if game_state == MENU:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:

                    game_state = CHARACTER_SELECT

                if event.key == pygame.K_c:

                    open_character_menu(MENU)

                if event.key == pygame.K_ESCAPE:

                    running = False

        # CHARACTER SELECT
        elif game_state == CHARACTER_SELECT:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1:

                    start_game("Samurai")

                if event.key == pygame.K_2:

                    start_game("Caballero")

                if event.key == pygame.K_3:

                    start_game("Hechicera")

                if event.key == pygame.K_c:

                    open_character_menu(MENU)

                if event.key == pygame.K_ESCAPE:

                    game_state = MENU

        # CHARACTER MENU
        elif game_state == CHARACTER_MENU:

            action = character_menu.handle_event(event)

            if action == "back":

                sync_player_from_rpg()
                game_state = character_menu_return_state

            elif action == "changed":

                sync_player_from_rpg()

            elif action == "select":

                # Desde el menú principal, ENTER inicia una partida
                # con el personaje que estamos viendo.
                if character_menu_return_state in (MENU, CHARACTER_SELECT):

                    start_game(
                        character_menu.character_name
                    )

                else:

                    sync_player_from_rpg()
                    game_state = character_menu_return_state

        # GAME OVER
        elif game_state == GAME_OVER:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:

                    respawn()

                if event.key == pygame.K_m:

                    game_state = MENU

        # PAUSE MENU
        elif game_state == PAUSE:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_p:

                    game_state = PLAYING

                if event.key == pygame.K_m:

                    game_state = MENU

                if event.key == pygame.K_c:

                    open_character_menu(PAUSE)

        # PLAYING
        elif game_state == PLAYING:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_p:

                    game_state = PAUSE

                if event.key == pygame.K_c:

                    open_character_menu(PLAYING)


    # =========================
    # CHARACTER MENU UPDATE
    # =========================

    if game_state == CHARACTER_MENU:

        character_menu.update(dt)

    # =========================
    # GAMEPLAY
    # =========================

    if game_state == PLAYING:

        # =========================
        # HIT STOP
        # =========================

        if hit_stop_timer > 0:

            hit_stop_timer -= dt

        else:

            # PLAYER
            player.update(dt, platforms)

            # LIMITES DEL MUNDO:
            # evita que el jugador salga por la izquierda
            # (quedaría invisible con la cámara fija en 0).
            if player.rect.x < 0:

                player.rect.x = 0

            if player.rect.x > world_length:

                player.rect.x = world_length

            # POLVO AL ATERRIZAR
            if player.just_landed:

                player.just_landed = False

                for _ in range(10):

                    particles.append(
                        Particle(
                            player.rect.centerx,
                            player.rect.bottom,
                            color=(170, 170, 170)
                        )
                    )

            # ESTELA DEL DASH
            if player.is_dashing:

                particles.append(
                    Particle(
                        player.rect.centerx,
                        player.rect.centery,
                        color=(120, 170, 255)
                    )
                )

            # CAMERA
            camera.follow(
                player,
                WIDTH,
                world_length
            )

            camera.update(dt)

            keys = pygame.key.get_pressed()

            # UPDATE CHECKPOINT
            if current_checkpoint < len(checkpoints) - 1 and player.rect.x > checkpoints[current_checkpoint + 1][0]:
                current_checkpoint += 1

            # PARTICLES
            for particle in particles:

                particle.update(dt)

            particles = [
                p for p in particles
                if not p.is_dead()
            ]

            # HIT SPARKS
            for spark in hit_sparks:

                spark.update(dt)

            hit_sparks = [
                spark
                for spark in hit_sparks
                if not spark.is_dead
            ]

            # =========================
            # DAMAGE TEXT
            # =========================

            for damage_text in damage_texts:

                damage_text.update(dt)

            damage_texts = [
                damage_text
                for damage_text in damage_texts
                if not damage_text.is_finished()
            ]

            # =========================
            # ENEMIES
            # =========================

            for enemy in enemies:

                enemy.update(
                    dt,
                    player,
                    platforms
                )

            # =========================
            # BOSS SPAWN
            # =========================

            if (
                player.rect.x > world_length - 1800
                and not boss_spawned
            ):

                boss = Boss(
                    world_length - 700,
                    350
                )

                boss_spawned = True

                boss_banner_timer = 3.5

            # =========================
            # PLAYER ATTACK
            # =========================

            if player.can_attack_hit() and not player.has_hit:

                attack_sound.play()

                for enemy in enemies:

                    if player.attack_rect.colliderect(enemy.rect):

                        # =========================
                        # CÁLCULO DEL DAÑO
                        # =========================

                        base_damage = player.current_attack_damage()

                        is_crit = random.random() < CRIT_CHANCE

                        if is_crit:

                            final_damage = base_damage * CRIT_MULT

                        else:

                            final_damage = base_damage

                        damage = enemy.take_damage(
                            final_damage,
                            player
                        )

                        # =========================
                        # DAÑO VISUAL
                        # =========================

                        damage_texts.append(
                            DamageText(
                                enemy.rect.centerx,
                                enemy.rect.y - 20,
                                damage,
                                crit=is_crit
                            )
                        )

                        hit_sound.play()

                        if is_crit:

                            camera.shake(16, 0.16)

                            hit_stop_timer = 0.09

                        else:

                            camera.shake(
                                10,
                                0.12
                            )

                            hit_stop_timer = 0.05

                        hit_sparks.append(
                            HitSpark(
                                enemy.rect.centerx,
                                enemy.rect.centery
                            )
                        )

                        for _ in range(15):

                            particles.append(
                                Particle(
                                    enemy.rect.centerx,
                                    enemy.rect.centery
                                )
                            )

                        # IMPORTANTE:
                        # Solo marcamos el ataque como usado
                        # si realmente golpeó algo.
                        player.has_hit = True

                        # Un ataque del jugador solo puede
                        # golpear a un objetivo.
                        break

            # =========================
            # REMOVE DEAD ENEMIES
            # =========================

            alive_enemies = []

            for enemy in enemies:

                if enemy.is_dead:

                    score += 100

                    kills += 1

                    # Explosión de partículas al morir.
                    for _ in range(20):

                        particles.append(
                            Particle(
                                enemy.rect.centerx,
                                enemy.rect.centery
                            )
                        )

                    reward = rpg_manager.reward_enemy(
                        player.character_name
                    )

                    reward_message = (
                        f"+{reward['exp']} EXP   "
                        f"+{reward['gold']} ORO   "
                        f"+{reward['materials']} MATERIAL"
                    )

                    reward_timer = 1.4

                    continue

                alive_enemies.append(enemy)

            enemies = alive_enemies

            # =========================
            # FALL DEATH
            # =========================

            if player.rect.y > HEIGHT + 400 and not player.is_dead:

                # Muerte real: activa la animación de muerte y el
                # flujo de GAME OVER. Antes solo ponía la vida a 0
                # y el personaje quedaba invisible para siempre.
                player.take_damage(99999, player.rect.centerx)

            # RED DE SEGURIDAD:
            # ningún estado puede dejar al jugador con 0 de vida
            # y vivo a la vez (invisible y atascado). Si ocurre,
            # se fuerza la muerte real con su flujo de GAME OVER.
            if (
                player.health <= 0
                and not player.is_dead
                and player.max_health > 0
            ):

                player.take_damage(99999, player.rect.centerx)

            # =========================
            # BOSS UPDATE
            # =========================

            if boss:

                boss.update(
                    dt,
                    player,
                    platforms
                )

                # =========================
                # PLAYER DAMAGE TO BOSS
                # =========================

                if (
                    player.can_attack_hit()
                    and not player.has_hit
                    and player.attack_rect.colliderect(
                        boss.rect
                    )
                ):

                    # =========================
                    # CÁLCULO DEL DAÑO
                    # =========================

                    base_damage = player.current_attack_damage()

                    is_crit = random.random() < CRIT_CHANCE

                    if is_crit:

                        final_damage = base_damage * CRIT_MULT

                    else:

                        final_damage = base_damage

                    damage = boss.take_damage(
                        final_damage,
                        player
                    )

                    # =========================
                    # DAÑO VISUAL
                    # =========================

                    damage_texts.append(
                        DamageText(
                            boss.rect.centerx,
                            boss.rect.y - 20,
                            damage,
                            crit=is_crit
                        )
                    )

                    if is_crit:

                        camera.shake(24, 0.22)

                        hit_stop_timer = 0.09

                    else:

                        camera.shake(18, 0.18)

                    hit_sound.play()

                    hit_sparks.append(
                        HitSpark(
                            boss.rect.centerx,
                            boss.rect.centery
                        )
                    )

                    for _ in range(20):

                        particles.append(
                            Particle(
                                boss.rect.centerx,
                                boss.rect.centery
                            )
                        )

                    player.has_hit = True

                if boss.is_dead and not boss_defeated:

                    boss_defeated = True

                    chest = Chest(
                        boss.rect.centerx - 32,
                        boss.rect.bottom - 48
                    )

                    score += 500

                    reward = rpg_manager.reward_boss(
                        player.character_name
                    )

                    player.health = min(
                        player.max_health,
                        player.health + 50
                    )

                    reward_message = (
                        "JEFE DERROTADO!  "
                        f"+{reward['exp']} EXP  "
                        f"+{reward['gold']} ORO  "
                        f"+{reward['materials']} MATERIAL"
                    )

                    reward_timer = 4

            # =========================
            # GAME OVER
            # =========================

            if player.is_dead:

                if player.frame_index >= len(player.animations["dead"]) - 1:

                    player.death_timer += dt

                    if player.death_timer >= 0.7:

                        game_state = GAME_OVER

            # =========================
            # ENEMY SPAWN
            # =========================

            enemy_spawn_timer += dt

            if enemy_spawn_timer >= enemy_spawn_delay:

                enemy_spawn_timer = 0

                if len(enemies) < 5:

                    spawn_x = (
                        player.rect.x + 1200
                    )

                    new_enemy = Enemy(
                        spawn_x,
                        ground_y - 110
                    )

                    new_enemy.speed += kills * 2

                    enemies.append(new_enemy)

    # =========================
    # DRAW
    # =========================

    screen.fill((20, 20, 30))

    # BACKGROUND
    bg_width = background.get_width()

    bg_x = int(-camera.offset_x * 0.3)

    for i in range(-1, 20):

        screen.blit(
            background,
            (
                bg_x + i * bg_width,
                0
            )
        )

    # =========================
    # MENU
    # =========================

    if game_state == MENU:

        title = font.render(
            "DARKRISE PROJECT",
            True,
            (255,255,255)
        )

        play_text = font.render(
            "PRESIONA ENTER PARA EMPEZAR",
            True,
            (200,200,200)
        )

        character_text = font.render(
            "C - PERSONAJE",
            True,
            (200,200,200)
        )

        quit_text = font.render(
            "ESC PARA SALIR",
            True,
            (200,200,200)
        )

        screen.blit(title, (WIDTH//2 - 220, 180))

        screen.blit(play_text, (WIDTH//2 - 250, 300))

        screen.blit(character_text, (WIDTH//2 - 150, 360))

        screen.blit(quit_text, (WIDTH//2 - 150, 420))

        # CONTROLS
        controls_font = pygame.font.SysFont(None, 28)

        control_lines = [
            "CONTROLES:",
            "A - MOVER IZQUIERDA | D - MOVER DERECHA",
            "ESPACIO - SALTAR | J - ATACAR",
            "MAYÚS - ESQUIVA | E - INTERACTUAR",
            "P - PAUSA | M - MENÚ | C - PERSONAJE"
        ]

        start_y = 500
        for i, line in enumerate(control_lines):
            control_text = controls_font.render(
                line,
                True,
                (0, 0, 0)
            )
            screen.blit(
                control_text,
                (WIDTH//2 - control_text.get_width()//2, start_y + i * 28)
            )

    # =========================
    # CHARACTER SELECT
    # =========================

    elif game_state == CHARACTER_SELECT:

        title = font.render(
            "SELECCIONA TU CLASE",
            True,
            (255,255,255)
        )

        warrior_text = font.render(
            "1 - SAMURAI",
            True,
            WARRIOR["color"]
        )

        archer_text = font.render(
            "2 - CABALLERO",
            True,
            ARCHER["color"]
        )

        mage_text = font.render(
            "3 - HECHICERA",
            True,
            MAGE["color"]
        )

        screen.blit(title, (WIDTH//2 - 220, 150))

        screen.blit(warrior_text, (WIDTH//2 - 170, 280))

        screen.blit(archer_text, (WIDTH//2 - 170, 360))

        screen.blit(mage_text, (WIDTH//2 - 170, 440))

        # DESCRIPTIONS
        desc_font = pygame.font.SysFont(None, 26)

        warrior_desc = desc_font.render("Guerrero rápido", True, (0, 0, 0))
        archer_desc = desc_font.render("Especialista en defensa", True, (0, 0, 0))
        mage_desc = desc_font.render("Poder mágico", True, (0, 0, 0))

        screen.blit(warrior_desc, (WIDTH//2 + 150, 280))
        screen.blit(archer_desc, (WIDTH//2 + 150, 360))
        screen.blit(mage_desc, (WIDTH//2 + 150, 440))

        hint = desc_font.render(
            "C - ABRIR PANTALLA DE PERSONAJE | ESC - VOLVER",
            True,
            (0, 0, 0)
        )

        screen.blit(
            hint,
            (WIDTH//2 - hint.get_width()//2, 570)
        )

    # =========================
    # CHARACTER MENU
    # =========================

    elif game_state == CHARACTER_MENU:

        character_menu.draw()

    # =========================
    # PLAYING
    # =========================

    elif game_state == PLAYING:

        # PLATFORMS
        decorations.update(
            dt,
            platforms
        )
        decorations.draw(screen, camera)
        for platform in platforms:

            platform.draw(
                screen,
                camera,
                tilemap
            )

        # PLAYER
        player.draw(screen, camera)

        # ENEMIES
        for enemy in enemies:

            enemy.draw(screen, camera)

        if boss:

            boss.draw(screen, camera)

        if chest:

            chest.draw(screen, camera)

            if (
                not chest.opened
                and player.rect.colliderect(chest.rect)
                and keys[pygame.K_e]
            ):

                chest.opened = True

                score += 1000

                reward = rpg_manager.reward_chest()

                player.health = min(
                    player.max_health,
                    player.health + 50
                )

                reward_message = (
                    "COFRE ABIERTO!  "
                    f"+{reward['gold']} ORO  "
                    f"+{reward['materials']} MATERIAL"
                )

                reward_timer = 4

            if (
                chest
                and not chest.opened
                and player.rect.colliderect(chest.rect)
            ):

                press_e_text = hud_font.render(
                    "PRESIONA E PARA ABRIR",
                    True,
                    (255, 215, 0)
                )

                screen.blit(
                    press_e_text,
                    (
                        chest.rect.x - int(camera.offset_x),
                        chest.rect.y - 30
                    )
                )

        # PARTICLES
        for particle in particles:

            particle.draw(screen, camera)

        # HIT SPARKS
        for spark in hit_sparks:

            spark.draw(screen, camera)

        # =========================
        # DAMAGE TEXT
        # =========================

        for damage_text in damage_texts:

            damage_text.draw(
                screen,
                camera
            )

        # =========================
        # HUD
        # =========================

        hud_x = 25

        hud_y = 20

        pygame.draw.rect(
            screen,
            (15,15,15),
            (15, 10, 390, 215),
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            (80,80,80),
            (15, 10, 390, 215),
            3,
            border_radius=12
        )

        # CLASS
        class_text = hud_font.render(
            player.character_name,
            True,
            (255,255,255)
        )

        screen.blit(class_text, (hud_x, hud_y))

        # HP BAR
        bar_width = 260

        bar_height = 24

        pygame.draw.rect(
            screen,
            (60,0,0),
            (
                hud_x,
                hud_y + 40,
                bar_width,
                bar_height
            ),
            border_radius=8
        )

        health_width = (
            player.health
            / player.max_health
        ) * bar_width

        pygame.draw.rect(
            screen,
            (220,40,40),
            (
                hud_x,
                hud_y + 40,
                health_width,
                bar_height
            ),
            border_radius=8
        )

        hp_text = hud_font.render(
            f"{player.health}/{player.max_health}",
            True,
            (255,255,255)
        )

        screen.blit(
            hp_text,
            (hud_x + 95, hud_y + 38)
        )

        # DASH BAR
        dash_ratio = max(
            0,
            player.dash_cooldown_timer
            / DASH_COOLDOWN
        )

        dash_width = (
            1 - dash_ratio
        ) * bar_width

        pygame.draw.rect(
            screen,
            (20,20,50),
            (
                hud_x,
                hud_y + 80,
                bar_width,
                18
            ),
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            (80,120,255),
            (
                hud_x,
                hud_y + 80,
                dash_width,
                18
            ),
            border_radius=8
        )

        dash_text = hud_font.render(
            "ESQUIVA",
            True,
            (255,255,255)
        )

        screen.blit(
            dash_text,
            (hud_x + 90, hud_y + 75)
        )

        # RPG LEVEL / EXP
        profile = rpg_manager.get_profile(
            player.character_name
        )

        level_text = hud_font.render(
            f"NIVEL : {profile.level}",
            True,
            (255, 215, 100)
        )

        gold_text = hud_font.render(
            f"ORO : {rpg_manager.gold}",
            True,
            (255, 215, 100)
        )

        screen.blit(
            level_text,
            (hud_x, hud_y + 120)
        )

        screen.blit(
            gold_text,
            (hud_x + 150, hud_y + 120)
        )

        exp_ratio = min(
            1,
            profile.exp / max(1, profile.exp_required)
        )

        pygame.draw.rect(
            screen,
            (35, 40, 55),
            (hud_x, hud_y + 155, 260, 14),
            border_radius=6
        )

        pygame.draw.rect(
            screen,
            (90, 145, 245),
            (hud_x, hud_y + 155, int(260 * exp_ratio), 14),
            border_radius=6
        )

        exp_text = hud_font.render(
            f"EXP {profile.exp}/{profile.exp_required}",
            True,
            (220, 225, 240)
        )

        screen.blit(
            exp_text,
            (hud_x + 75, hud_y + 150)
        )

        # SCORE / KILLS
        score_text = hud_font.render(
            f"PUNTOS : {score}",
            True,
            (255,255,255)
        )

        kills_text = hud_font.render(
            f"MUERTES : {kills}",
            True,
            (255,255,255)
        )

        screen.blit(
            score_text,
            (hud_x, hud_y + 180)
        )

        screen.blit(
            kills_text,
            (hud_x + 180, hud_y + 180)
        )

        if reward_timer > 0:

            reward_timer -= dt

            reward_text = hud_font.render(
                reward_message,
                True,
                (255, 215, 0)
            )

            screen.blit(
                reward_text,
                (
                    WIDTH // 2
                    - reward_text.get_width() // 2,
                    hud_y + 170
                )
            )

        # BANNER DE JEFE FINAL
        if boss_banner_timer > 0:

            boss_banner_timer -= dt

            banner_font = pygame.font.SysFont(None, 90)

            banner_text = banner_font.render(
                "¡JEFE FINAL!",
                True,
                (255, 60, 60)
            )

            if (pygame.time.get_ticks() // 250) % 2 == 0:

                screen.blit(
                    banner_text,
                    (
                        WIDTH // 2
                        - banner_text.get_width() // 2,
                        120
                    )
                )

        # ALERTA DE VIDA BAJA
        if (
            not player.is_dead
            and player.health <= player.max_health * 0.3
        ):

            blink_on = (pygame.time.get_ticks() // 300) % 2 == 0

            vignette = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            vignette.fill(
                (
                    180,
                    0,
                    0,
                    50 if blink_on else 20
                )
            )

            screen.blit(vignette, (0, 0))

        # INDICACIÓN DE LA NUEVA PANTALLA
        character_hint = pygame.font.SysFont(None, 24).render(
            "C - PERSONAJE",
            True,
            (220, 220, 220)
        )

        screen.blit(
            character_hint,
            (WIDTH - character_hint.get_width() - 25, HEIGHT - 35)
        )

    # =========================
    # GAME OVER
    # =========================

    elif game_state == GAME_OVER:

        game_over_text = font.render(
            "FIN DEL JUEGO",
            True,
            (255, 50, 50)
        )

        retry_text = font.render(
            "PRESIONA R PARA REAPARRECER",
            True,
            (255,255,255)
        )

        menu_text = font.render(
            "PRESIONA M PARA MENÚ",
            True,
            (255,255,255)
        )

        screen.blit(
            game_over_text,
            (WIDTH//2 - 160, 250)
        )

        screen.blit(
            retry_text,
            (WIDTH//2 - 280, 350)
        )

        screen.blit(
            menu_text,
            (WIDTH//2 - 200, 430)
        )

    # =========================
    # PAUSE MENU
    # =========================

    elif game_state == PAUSE:

        pause_title = font.render(
            "PAUSADO",
            True,
            (255, 255, 100)
        )

        resume_text = font.render(
            "PRESIONA P PARA REANUDAR",
            True,
            (255,255,255)
        )

        character_text = font.render(
            "PRESIONA C PARA PERSONAJE",
            True,
            (255,255,255)
        )

        menu_text = font.render(
            "PRESIONA M PARA MENÚ",
            True,
            (255,255,255)
        )

        screen.blit(
            pause_title,
            (WIDTH//2 - 120, 200)
        )

        screen.blit(
            resume_text,
            (WIDTH//2 - 260, 300)
        )

        screen.blit(
            character_text,
            (WIDTH//2 - 240, 360)
        )

        screen.blit(
            menu_text,
            (WIDTH//2 - 200, 420)
        )

    pygame.display.update()

pygame.quit()

sys.exit()
