import json
import os


SAVE_FILE = "rpg_save.json"


WEAPONS = {
    "katana_aurora": {
        "id": "katana_aurora",
        "name": "Katana Aurora",
        "character": "Samurai",
        "rarity": 4,
        "attack_bonus": 0,
        "health_bonus": 0,
        "max_level": 20,
        "color": (230, 90, 90),
    },
    "katana_carmesi": {
        "id": "katana_carmesi",
        "name": "Katana Carmesí",
        "character": "Samurai",
        "rarity": 5,
        "attack_bonus": 3,
        "health_bonus": 20,
        "max_level": 20,
        "color": (255, 140, 80),
    },
    "espada_guardian": {
        "id": "espada_guardian",
        "name": "Espada del Guardián",
        "character": "Caballero",
        "rarity": 4,
        "attack_bonus": 0,
        "health_bonus": 0,
        "max_level": 20,
        "color": (100, 220, 140),
    },
    "espada_bastion": {
        "id": "espada_bastion",
        "name": "Hoja del Bastión",
        "character": "Caballero",
        "rarity": 5,
        "attack_bonus": 2,
        "health_bonus": 80,
        "max_level": 20,
        "color": (150, 255, 190),
    },
    "baston_arcano": {
        "id": "baston_arcano",
        "name": "Bastón Arcano",
        "character": "Hechicera",
        "rarity": 4,
        "attack_bonus": 0,
        "health_bonus": 0,
        "max_level": 20,
        "color": (120, 150, 255),
    },
    "baston_estelar": {
        "id": "baston_estelar",
        "name": "Bastón Estelar",
        "character": "Hechicera",
        "rarity": 5,
        "attack_bonus": 4,
        "health_bonus": 10,
        "max_level": 20,
        "color": (190, 140, 255),
    },
}


STARTER_WEAPONS = {
    "Samurai": "katana_aurora",
    "Caballero": "espada_guardian",
    "Hechicera": "baston_arcano",
}


CHARACTER_DATA_CACHE = []


class CharacterProgression:
    """Progreso individual de un personaje."""

    def __init__(self, data, saved=None):
        self.name = data["name"]
        self.base_health = data["health"]
        self.base_damage = data.get("damage", 1)
        self.base_speed = data["speed"]
        self.attack_width = data["attack_width"]
        self.color = data["color"]

        saved = saved or {}

        self.level = max(1, int(saved.get("level", 1)))
        self.exp = max(0, int(saved.get("exp", 0)))

        starter_weapon = STARTER_WEAPONS[self.name]
        alternate_weapon = self._alternate_weapon_id()

        self.equipped_weapon = saved.get(
            "equipped_weapon",
            starter_weapon
        )

        unlocked = saved.get(
            "unlocked_weapons",
            [starter_weapon, alternate_weapon]
        )

        self.unlocked_weapons = list(dict.fromkeys(unlocked))

        if starter_weapon not in self.unlocked_weapons:
            self.unlocked_weapons.append(starter_weapon)

        if alternate_weapon not in self.unlocked_weapons:
            self.unlocked_weapons.append(alternate_weapon)

        if self.equipped_weapon not in self.unlocked_weapons:
            self.equipped_weapon = starter_weapon

        # Cada personaje guarda el nivel de cada una de sus armas.
        # También migramos el formato viejo si existe en el archivo.
        saved_weapon_levels = saved.get("weapon_levels", {})
        self.weapon_levels = {}

        for weapon_id in self.unlocked_weapons:
            self.weapon_levels[weapon_id] = max(
                1,
                int(saved_weapon_levels.get(weapon_id, 1))
            )

    def _alternate_weapon_id(self):
        candidates = [
            weapon_id
            for weapon_id, weapon in WEAPONS.items()
            if weapon["character"] == self.name
            and weapon_id != STARTER_WEAPONS[self.name]
        ]

        return candidates[0] if candidates else STARTER_WEAPONS[self.name]

    @property
    def exp_required(self):
        return 100 + (self.level - 1) * 60

    @property
    def can_level_up(self):
        return self.level < 60 and self.exp >= self.exp_required

    @property
    def weapon(self):
        return WEAPONS[self.equipped_weapon]

    def get_weapon_level(self, weapon_id):
        return self.weapon_levels.get(weapon_id, 1)

    def get_weapon_data(self, weapon_id=None):
        weapon_id = weapon_id or self.equipped_weapon
        base = WEAPONS[weapon_id]
        level = self.get_weapon_level(weapon_id)

        data = dict(base)
        data["level"] = level
        data["effective_attack_bonus"] = (
            base["attack_bonus"] + level - 1
        )
        data["effective_health_bonus"] = (
            base["health_bonus"] + (level - 1) * 5
        )
        data["equipped"] = weapon_id == self.equipped_weapon
        return data

    def add_exp(self, amount):
        if amount > 0:
            self.exp += int(amount)

    def level_up(self):
        if not self.can_level_up:
            return False

        # Consumimos la EXP necesaria y subimos exactamente un nivel.
        self.exp -= self.exp_required
        self.level += 1
        return True

    def get_stats(self):
        level_offset = self.level - 1
        weapon = self.get_weapon_data()

        health = round(
            self.base_health * (1 + level_offset * 0.08)
        )

        damage = self.base_damage + (level_offset // 3)

        health += weapon["effective_health_bonus"]
        damage += weapon["effective_attack_bonus"]

        return {
            "name": self.name,
            "color": self.color,
            "health": health,
            "damage": damage,
            "speed": self.base_speed,
            "attack_hit_frame": self._get_attack_hit_frame(),
            "attack_width": self.attack_width,
            "level": self.level,
            "exp": self.exp,
            "exp_required": self.exp_required,
            "weapon_name": weapon["name"],
            "weapon_level": weapon["level"],
            "weapon_attack_bonus": weapon["effective_attack_bonus"],
            "weapon_health_bonus": weapon["effective_health_bonus"],
        }

    def _get_attack_hit_frame(self):
        for character in CHARACTER_DATA_CACHE:
            if character["name"] == self.name:
                return character["attack_hit_frame"]
        return 2


class RPGManager:

    def __init__(self, characters):
        global CHARACTER_DATA_CACHE
        CHARACTER_DATA_CACHE = characters

        self.characters = {
            character["name"]: character
            for character in characters
        }

        self.gold = 1000
        self.materials = 15
        self.active_character = characters[0]["name"]
        self.profiles = {}

        self.load()

        if self.active_character not in self.profiles:
            self.active_character = characters[0]["name"]
            self.save()

    # ---------------------------------------------------------
    # SAVE / LOAD
    # ---------------------------------------------------------

    def load(self):
        if not os.path.exists(SAVE_FILE):
            self.profiles = {
                character["name"]: CharacterProgression(character)
                for character in self.characters.values()
            }
            self.save()
            return

        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.gold = max(0, int(data.get("gold", 1000)))
            self.materials = max(0, int(data.get("materials", 15)))
            self.active_character = data.get(
                "active_character",
                next(iter(self.characters))
            )

            saved_profiles = data.get("characters", {})

            for character in self.characters.values():
                saved = saved_profiles.get(character["name"], {})
                self.profiles[character["name"]] = CharacterProgression(
                    character,
                    saved
                )

        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            self.gold = 1000
            self.materials = 15
            self.active_character = next(iter(self.characters))
            self.profiles = {
                character["name"]: CharacterProgression(character)
                for character in self.characters.values()
            }
            self.save()

    def save(self):
        data = {
            "gold": self.gold,
            "materials": self.materials,
            "active_character": self.active_character,
            "characters": {},
        }

        for name, profile in self.profiles.items():
            data["characters"][name] = {
                "level": profile.level,
                "exp": profile.exp,
                "equipped_weapon": profile.equipped_weapon,
                "unlocked_weapons": profile.unlocked_weapons,
                "weapon_levels": profile.weapon_levels,
            }

        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )
        except OSError:
            pass

    # ---------------------------------------------------------
    # PERSONAJES
    # ---------------------------------------------------------

    def get_profile(self, name=None):
        name = name or self.active_character
        return self.profiles[name]

    def get_character_data(self, name=None):
        return self.get_profile(name).get_stats()

    def set_active_character(self, name):
        if name not in self.profiles:
            return False

        self.active_character = name
        self.save()
        return True

    def level_up(self, name):
        profile = self.get_profile(name)

        if profile.level_up():
            self.save()
            return True

        return False

    # ---------------------------------------------------------
    # ARMAS
    # ---------------------------------------------------------

    def get_available_weapons(self, character_name):
        profile = self.get_profile(character_name)

        return [
            profile.get_weapon_data(weapon_id)
            for weapon_id in profile.unlocked_weapons
            if weapon_id in WEAPONS
        ]

    def equip_weapon(self, character_name, weapon_id):
        profile = self.get_profile(character_name)

        if weapon_id not in profile.unlocked_weapons:
            return False

        weapon = WEAPONS.get(weapon_id)

        if weapon is None or weapon["character"] != character_name:
            return False

        profile.equipped_weapon = weapon_id
        self.save()
        return True

    def get_weapon_upgrade_cost(self, character_name, weapon_id=None):
        profile = self.get_profile(character_name)
        weapon_id = weapon_id or profile.equipped_weapon
        level = profile.get_weapon_level(weapon_id)

        return {
            "gold": 150 + level * 75,
            "materials": 1 + level // 5,
        }

    def upgrade_weapon(self, character_name, weapon_id=None):
        profile = self.get_profile(character_name)
        weapon_id = weapon_id or profile.equipped_weapon

        if weapon_id not in profile.unlocked_weapons:
            return False, "ARMA NO DISPONIBLE"

        weapon = WEAPONS[weapon_id]
        current_level = profile.get_weapon_level(weapon_id)

        if current_level >= weapon["max_level"]:
            return False, "ARMA AL MÁXIMO"

        cost = self.get_weapon_upgrade_cost(
            character_name,
            weapon_id
        )

        if self.gold < cost["gold"]:
            return False, "ORO INSUFICIENTE"

        if self.materials < cost["materials"]:
            return False, "MATERIALES INSUFICIENTES"

        self.gold -= cost["gold"]
        self.materials -= cost["materials"]
        profile.weapon_levels[weapon_id] = current_level + 1
        self.save()

        return True, "ARMA MEJORADA"

    # ---------------------------------------------------------
    # RECOMPENSAS
    # ---------------------------------------------------------

    def reward_enemy(self, character_name):
        reward = {
            "exp": 40,
            "gold": 35,
            "materials": 1,
        }

        self.get_profile(character_name).add_exp(reward["exp"])
        self.gold += reward["gold"]
        self.materials += reward["materials"]
        self.save()

        return reward

    def reward_boss(self, character_name):
        reward = {
            "exp": 300,
            "gold": 500,
            "materials": 8,
        }

        self.get_profile(character_name).add_exp(reward["exp"])
        self.gold += reward["gold"]
        self.materials += reward["materials"]
        self.save()

        return reward

    def reward_chest(self):
        reward = {
            "gold": 1000,
            "materials": 5,
        }

        self.gold += reward["gold"]
        self.materials += reward["materials"]
        self.save()

        return reward

    # ---------------------------------------------------------
    # APLICAR STATS AL JUGADOR
    # ---------------------------------------------------------

    def refresh_player_stats(self, player):
        data = self.get_character_data(player.character_name)

        old_max_health = player.max_health
        old_health_ratio = (
            player.health / old_max_health
            if old_max_health > 0
            else 1
        )

        player.max_health = data["health"]
        player.damage = data["damage"]
        player.speed = data["speed"]

        # Al cambiar de nivel/arma mantenemos aproximadamente el
        # mismo porcentaje de vida, evitando curaciones gratuitas.
        player.health = round(
            player.max_health * old_health_ratio
        )
        player.health = max(
            0,
            min(player.health, player.max_health)
        )

        return data