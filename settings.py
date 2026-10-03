WIDTH = 1280
HEIGHT = 720
FPS = 60

TITLE = "Darkrise Project v2.4"

GROUND_Y = 600

PLAYER_WIDTH = 50
PLAYER_HEIGHT = 80

PLAYER_SPEED = 400
JUMP_FORCE = -900
GRAVITY = 2000
ATTACK_WIDTH = 140

ATTACK_HEIGHT = 40

# GAME FEEL
COYOTE_TIME = 0.10
JUMP_BUFFER = 0.12
COMBO_WINDOW = 0.9
COMBO_DAMAGE = (1.0, 1.0, 1.6)
CRIT_CHANCE = 0.12
CRIT_MULT = 2
HIT_FLASH_TIME = 0.12
LAND_DUST_THRESHOLD = 650

ATTACK_DURATION = 0.5
ATTACK_COOLDOWN = 0.4
PLAYER_MAX_HEALTH = 100

PLAYER_DAMAGE_COOLDOWN = 1.0
# CLASES

WARRIOR = {
    "name": "Samurai",
    "color": (200, 50, 50),
    "health": 150,
    "damage": 2,
    "speed": 400,
    "attack_hit_frame": 2,
    "attack_width": 140
}

ARCHER = {
    "name": "Caballero",
    "color": (50, 200, 50),
    "health": 240,
    "damage": 1,
    "speed": 300,
    "attack_hit_frame": 3,
    "attack_width": 100
}

MAGE = {
    "name": "Hechicera",
    "color": (100, 100, 255),
    "health": 110,
    "damage": 4,
    "speed": 500,
    "attack_hit_frame": 7,
    "attack_width": 140
}
DASH_SPEED = 1200

DASH_DURATION = 0.15

DASH_COOLDOWN = 0.8