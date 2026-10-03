import os
import pygame

from utils import load_spritesheet


class CharacterMenu:
    """Interfaz RPG para personajes, armas y mejoras."""

    TABS = ["stats", "weapon", "upgrade"]

    def __init__(self, screen, rpg_manager):
        self.screen = screen
        self.rpg = rpg_manager
        self.width, self.height = screen.get_size()

        self.title_font = pygame.font.SysFont("arial", 42, bold=True)
        self.name_font = pygame.font.SysFont("arial", 48, bold=True)
        self.level_font = pygame.font.SysFont("arial", 24, bold=True)
        self.stat_font = pygame.font.SysFont("arial", 23)
        self.small_font = pygame.font.SysFont("arial", 18)
        self.button_font = pygame.font.SysFont("arial", 20, bold=True)
        self.big_stat_font = pygame.font.SysFont("arial", 28, bold=True)

        self.character_names = list(self.rpg.characters.keys())
        self.selected_index = 0
        self.tab_index = 0
        self.weapon_index = 0
        self.allow_character_change = True

        self.animation_timer = 0.0
        self.animation_speed = 0.60
        self.frame_index = 0
        self.idle_frames = []
        self.loaded_character_key = None
        self.menu_background = None

        self.last_message = ""
        self.message_timer = 0.0

        self._set_initial_character()

    # ---------------------------------------------------------
    # PROPIEDADES
    # ---------------------------------------------------------

    @property
    def character_name(self):
        return self.character_names[self.selected_index]

    @property
    def profile(self):
        return self.rpg.get_profile(self.character_name)

    @property
    def character_data(self):
        return self.rpg.get_character_data(self.character_name)

    @property
    def available_weapons(self):
        return self.rpg.get_available_weapons(self.character_name)

    @property
    def selected_weapon(self):
        weapons = self.available_weapons

        if not weapons:
            return None

        self.weapon_index %= len(weapons)
        return weapons[self.weapon_index]

    @property
    def current_tab(self):
        return self.TABS[self.tab_index]

    # ---------------------------------------------------------
    # CONFIGURACIÓN
    # ---------------------------------------------------------

    def _set_initial_character(self):
        if self.rpg.active_character in self.character_names:
            self.selected_index = self.character_names.index(
                self.rpg.active_character
            )

        self._load_selected_animation()
        self._sync_weapon_index()

    def set_context(self, return_state):
        self.allow_character_change = return_state != "playing"

        if self.rpg.active_character in self.character_names:
            self.selected_index = self.character_names.index(
                self.rpg.active_character
            )

        self._load_selected_animation()
        self._sync_weapon_index()

    def _sync_weapon_index(self):
        weapons = self.available_weapons

        if not weapons:
            self.weapon_index = 0
            return

        equipped_id = self.profile.equipped_weapon

        for index, weapon in enumerate(weapons):
            if weapon["id"] == equipped_id:
                self.weapon_index = index
                return

        self.weapon_index = 0

    # ---------------------------------------------------------
    # ANIMACIÓN Y FONDO DEL MENÚ
    # ---------------------------------------------------------

    def _get_character_folder(self):
        folder_map = {
            "Samurai": "warrior",
            "Caballero": "archer",
            "Hechicera": "mage",
        }
        return folder_map.get(
            self.character_name,
            self.character_name.lower()
        )

    def _load_fixed_spritesheet(self, path, frame_width, frame_height):
        frames = []

        sheet = pygame.image.load(path).convert_alpha()
        columns = sheet.get_width() // frame_width
        rows = sheet.get_height() // frame_height

        if columns <= 0 or rows <= 0:
            return frames

        for row in range(rows):
            for column in range(columns):
                frame = sheet.subsurface(
                    (
                        column * frame_width,
                        row * frame_height,
                        frame_width,
                        frame_height,
                    )
                ).copy()
                frames.append(frame)

        return frames

    def _load_selected_animation(self):
        folder = self._get_character_folder()

        if folder == self.loaded_character_key:
            return

        # Animaciones especiales exclusivas para la pantalla de personaje.
        # Todas deben estar preparadas como spritesheet de 256x384 por frame.
        special_animation_candidates = {
            "Samurai": [
                os.path.join(
                    "assets",
                    "character_menu",
                    "menu_idle",
                    "samurai_menu_idle.png"
                ),
                os.path.join(
                    "assets",
                    "character_menu",
                    "menu_idle",
                    "samurai.png"
                ),
            ],
            "Caballero": [
                os.path.join(
                    "assets",
                    "character_menu",
                    "menu_idle",
                    "caballero_menu_idle.png"
                ),
                os.path.join(
                    "assets",
                    "character_menu",
                    "menu_idle",
                    "caballero.png"
                ),
            ],
            "Hechicera": [
                os.path.join(
                    "assets",
                    "character_menu",
                    "menu_idle",
                    "hechicera_menu_idle.png"
                ),
                os.path.join(
                    "assets",
                    "character_menu",
                    "menu_idle",
                    "hechicera.png"
                ),
            ],
        }

        self.using_special_animation = False

        if self.character_name in special_animation_candidates:
            path = None

            for candidate in special_animation_candidates[
                self.character_name
            ]:
                if os.path.exists(candidate):
                    path = candidate
                    break

            if path is not None:
                try:
                    self.idle_frames = self._load_fixed_spritesheet(
                        path,
                        256,
                        384
                    )
                    self.using_special_animation = bool(
                        self.idle_frames
                    )
                except (pygame.error, FileNotFoundError):
                    self.idle_frames = []
            else:
                self.idle_frames = []

        # Si todavía no existe la animación especial, usamos la Idle
        # normal como respaldo. Así el menú nunca se queda vacío.
        if not self.idle_frames:
            path = os.path.join(
                "assets",
                "player",
                folder,
                "Idle.png"
            )

            try:
                self.idle_frames = load_spritesheet(
                    path,
                    128,
                    128
                )
            except (pygame.error, FileNotFoundError):
                self.idle_frames = []

        self._load_selected_background()

        self.loaded_character_key = folder
        self.frame_index = 0
        self.animation_timer = 0.0

    def _load_selected_background(self):
        key_map = {
            "Samurai": "samurai",
            "Caballero": "caballero",
            "Hechicera": "hechicera",
        }

        key = key_map.get(
            self.character_name,
            self.character_name.lower()
        )

        path = os.path.join(
            "assets",
            "character_menu",
            "backgrounds",
            f"{key}.png"
        )

        try:
            self.menu_background = pygame.image.load(
                path
            ).convert_alpha()
        except (pygame.error, FileNotFoundError):
            self.menu_background = None

    # ---------------------------------------------------------
    # CAMBIO DE PERSONAJE
    # ---------------------------------------------------------

    def next_character(self):
        if not self.allow_character_change:
            return

        self.selected_index = (
            self.selected_index + 1
        ) % len(self.character_names)

        self._load_selected_animation()
        self._sync_weapon_index()

    def previous_character(self):
        if not self.allow_character_change:
            return

        self.selected_index = (
            self.selected_index - 1
        ) % len(self.character_names)

        self._load_selected_animation()
        self._sync_weapon_index()

    def select_by_name(self, name):
        if name not in self.character_names:
            return

        self.selected_index = self.character_names.index(name)
        self._load_selected_animation()
        self._sync_weapon_index()

    # ---------------------------------------------------------
    # ARMAS
    # ---------------------------------------------------------

    def next_weapon(self):
        weapons = self.available_weapons

        if not weapons:
            return

        self.weapon_index = (
            self.weapon_index + 1
        ) % len(weapons)

    def previous_weapon(self):
        weapons = self.available_weapons

        if not weapons:
            return

        self.weapon_index = (
            self.weapon_index - 1
        ) % len(weapons)

    def equip_selected_weapon(self):
        weapon = self.selected_weapon

        if weapon is None:
            return None

        if self.profile.equipped_weapon == weapon["id"]:
            self._set_message("ARMA YA EQUIPADA")
            return "changed"

        if self.rpg.equip_weapon(
            self.character_name,
            weapon["id"]
        ):
            self._set_message(
                f"EQUIPADA: {weapon['name']}"
            )
            return "changed"

        return None

    # ---------------------------------------------------------
    # MEJORAS
    # ---------------------------------------------------------

    def level_up(self):
        if self.rpg.level_up(self.character_name):
            self._set_message("¡PERSONAJE SUBIÓ DE NIVEL!")
            return "changed"

        self._set_message("EXP INSUFICIENTE")
        return None

    def upgrade_weapon(self):
        success, message = self.rpg.upgrade_weapon(
            self.character_name
        )

        self._set_message(message)

        if success:
            return "changed"

        return None

    def _set_message(self, message):
        self.last_message = message
        self.message_timer = 2.0

    # ---------------------------------------------------------
    # EVENTOS
    # ---------------------------------------------------------

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        if event.key in (pygame.K_ESCAPE, pygame.K_m):
            return "back"

        if event.key == pygame.K_TAB:
            self.tab_index = (
                self.tab_index + 1
            ) % len(self.TABS)
            return None

        if event.key == pygame.K_1:
            self.tab_index = 0
            return None

        if event.key == pygame.K_2:
            self.tab_index = 1
            return None

        if event.key == pygame.K_3:
            self.tab_index = 2
            return None

        if self.current_tab == "weapon":
            if event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_e):
                self.next_weapon()
                return None

            if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_q):
                self.previous_weapon()
                return None

            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self.equip_selected_weapon()

            if event.key == pygame.K_i:
                return self.upgrade_weapon()

        elif self.current_tab == "upgrade":
            # En la pestaña MEJORAR, I es el botón principal
            # para subir al personaje. U queda como atajo.
            if event.key in (pygame.K_i, pygame.K_u):
                return self.level_up()

        else:
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self.next_character()
                return None

            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.previous_character()
                return None

            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return "select"

        return None

    # ---------------------------------------------------------
    # ACTUALIZACIÓN
    # ---------------------------------------------------------

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt

        if not self.idle_frames:
            return

        self.animation_timer += dt

        if self.animation_timer >= self.animation_speed:
            self.animation_timer -= self.animation_speed
            self.frame_index += 1

            if self.frame_index >= len(self.idle_frames):
                self.frame_index = 0

    # ---------------------------------------------------------
    # DIBUJO
    # ---------------------------------------------------------

    def _draw_background(self):
        if self.menu_background is not None:
            background = pygame.transform.smoothscale(
                self.menu_background,
                (self.width, self.height)
            )
            self.screen.blit(background, (0, 0))

            # Capa oscura ligera para mantener legibles los paneles.
            overlay = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )
            overlay.fill((5, 8, 18, 65))
            self.screen.blit(overlay, (0, 0))
            return

        self.screen.fill((8, 10, 20))

        pygame.draw.rect(
            self.screen,
            (15, 18, 30),
            (25, 25, self.width - 50, self.height - 50),
            border_radius=18
        )

        pygame.draw.rect(
            self.screen,
            (55, 59, 82),
            (25, 25, self.width - 50, self.height - 50),
            2,
            border_radius=18
        )

        pygame.draw.circle(
            self.screen,
            (25, 29, 48),
            (360, 360),
            230
        )

        pygame.draw.circle(
            self.screen,
            (55, 60, 88),
            (360, 360),
            230,
            2
        )

    def _draw_character(self):
        if not self.idle_frames:
            text = self.small_font.render(
                "No se encontró la animación del personaje",
                True,
                (220, 220, 220)
            )
            rect = text.get_rect(center=(360, 360))
            self.screen.blit(text, rect)
            return

        image = self.idle_frames[self.frame_index]

        # Las animaciones especiales del menú se muestran más grandes
        # que las Idle normales del combate.
        target_height = 500 if self.using_special_animation else 410

        scale = target_height / image.get_height()
        image = pygame.transform.smoothscale(
            image,
            (
                int(image.get_width() * scale),
                target_height
            )
        )

        image_rect = image.get_rect(
            center=(360, 365)
        )

        # Centramos la parte visible del sprite, no el canvas completo.
        # Esto corrige diferencias de padding/transparencia entre personajes.
        visible_rect = image.get_bounding_rect()

        if visible_rect.width > 0 and visible_rect.height > 0:
            image_rect.centerx = 360 + (
                image.get_width() // 2 - visible_rect.centerx
            )

        self.screen.blit(image, image_rect)

    def _draw_text(self, text, x, y, font=None, color=(240, 240, 245)):
        surface = (font or self.stat_font).render(
            text,
            True,
            color
        )
        self.screen.blit(surface, (x, y))

    def _draw_stat(self, label, value, x, y):
        self._draw_text(
            label,
            x,
            y,
            self.stat_font,
            (175, 178, 195)
        )

        self._draw_text(
            str(value),
            x + 150,
            y,
            self.stat_font,
            (245, 245, 250)
        )

    def _draw_exp_bar(self, profile, x, y, width):
        required = max(1, profile.exp_required)
        ratio = min(1.0, profile.exp / required)

        pygame.draw.rect(
            self.screen,
            (40, 42, 58),
            (x, y, width, 18),
            border_radius=8
        )

        pygame.draw.rect(
            self.screen,
            (100, 155, 255),
            (x, y, int(width * ratio), 18),
            border_radius=8
        )

        self._draw_text(
            f"EXP {profile.exp} / {required}",
            x,
            y + 23,
            self.small_font,
            (175, 180, 200)
        )

    def _draw_header(self):
        data = self.character_data
        profile = self.profile

        self._draw_text(
            "PERSONAJE",
            55,
            48,
            self.title_font
        )

        color = data["color"]

        self._draw_text(
            data["name"],
            610,
            65,
            self.name_font,
            (245, 245, 250)
        )

        self._draw_text(
            f"NIVEL {profile.level}",
            615,
            125,
            self.level_font,
            color
        )

        self._draw_text(
            f"ORO  {self.rpg.gold}",
            930,
            52,
            self.small_font,
            (245, 205, 80)
        )

        self._draw_text(
            f"MATERIALES  {self.rpg.materials}",
            930,
            78,
            self.small_font,
            (150, 220, 255)
        )

    def _draw_tabs(self):
        labels = [
            ("ATRIBUTOS", 0),
            ("ARMA", 1),
            ("MEJORAR", 2),
        ]

        x = 605
        y = 560

        for label, index in labels:
            rect = pygame.Rect(x, y, 145, 46)
            active = index == self.tab_index

            pygame.draw.rect(
                self.screen,
                (60, 66, 92) if active else (30, 33, 48),
                rect,
                border_radius=10
            )

            pygame.draw.rect(
                self.screen,
                (125, 135, 180) if active else (60, 63, 82),
                rect,
                2,
                border_radius=10
            )

            surface = self.button_font.render(
                label,
                True,
                (245, 245, 250)
            )

            self.screen.blit(
                surface,
                surface.get_rect(center=rect.center)
            )

            x += 155

    def _draw_stats_tab(self):
        data = self.character_data
        profile = self.profile

        panel = pygame.Rect(600, 165, 575, 370)

        pygame.draw.rect(
            self.screen,
            (21, 24, 39),
            panel,
            border_radius=16
        )

        pygame.draw.rect(
            self.screen,
            (67, 71, 96),
            panel,
            2,
            border_radius=16
        )

        self._draw_stat(
            "VIDA",
            data["health"],
            635,
            200
        )

        self._draw_stat(
            "ATAQUE",
            data["damage"],
            635,
            250
        )

        self._draw_stat(
            "VELOCIDAD",
            data["speed"],
            635,
            300
        )

        self._draw_stat(
            "ALCANCE",
            data["attack_width"],
            635,
            350
        )

        self._draw_text(
            "ARMA EQUIPADA",
            635,
            405,
            self.small_font,
            (155, 160, 180)
        )

        weapon = profile.weapon
        self._draw_text(
            f"{weapon['name']}  •  Nv. {weapon.get('level', 1)}",
            635,
            430,
            self.stat_font,
            weapon["color"]
        )

        self._draw_exp_bar(
            profile,
            635,
            480,
            500
        )

    def _draw_weapon_tab(self):
        weapon = self.selected_weapon
        profile = self.profile

        panel = pygame.Rect(600, 165, 575, 370)

        pygame.draw.rect(
            self.screen,
            (21, 24, 39),
            panel,
            border_radius=16
        )

        pygame.draw.rect(
            self.screen,
            (67, 71, 96),
            panel,
            2,
            border_radius=16
        )

        if weapon is None:
            self._draw_text(
                "SIN ARMAS",
                635,
                205,
                self.big_stat_font
            )
            return

        stars = "★" * weapon["rarity"] + "☆" * (5 - weapon["rarity"])
        level = weapon.get("level", 1)
        equipped = profile.equipped_weapon == weapon["id"]

        self._draw_text(
            weapon["name"],
            635,
            200,
            self.name_font,
            weapon["color"]
        )

        self._draw_text(
            stars,
            640,
            265,
            self.big_stat_font,
            (255, 215, 110)
        )

        self._draw_text(
            f"Nivel {level} / {weapon['max_level']}",
            640,
            315,
            self.level_font
        )

        self._draw_stat(
            "BONO ATAQUE",
            f"+{weapon['effective_attack_bonus']}",
            640,
            360
        )

        self._draw_stat(
            "BONO VIDA",
            f"+{weapon['effective_health_bonus']}",
            640,
            410
        )

        status = "EQUIPADA" if equipped else "DISPONIBLE"
        status_color = (110, 230, 150) if equipped else (180, 185, 205)

        self._draw_text(
            status,
            640,
            458,
            self.button_font,
            status_color
        )

        cost = self.rpg.get_weapon_upgrade_cost(
            self.character_name,
            weapon["id"]
        )

        if level < weapon["max_level"]:
            self._draw_text(
                f"Mejorar: {cost['gold']} oro  •  {cost['materials']} material",
                640,
                487,
                self.small_font,
                (220, 200, 120)
            )
        else:
            self._draw_text(
                "ARMA AL NIVEL MÁXIMO",
                640,
                487,
                self.small_font,
                (220, 200, 120)
            )

        self._draw_text(
            "←/→ o A/D: cambiar    ENTER: equipar    I: mejorar",
            640,
            515,
            self.small_font,
            (150, 155, 175)
        )

    def _draw_upgrade_tab(self):
        profile = self.profile
        data = self.character_data
        weapon = profile.weapon

        panel = pygame.Rect(600, 165, 575, 370)

        pygame.draw.rect(
            self.screen,
            (21, 24, 39),
            panel,
            border_radius=16
        )

        pygame.draw.rect(
            self.screen,
            (67, 71, 96),
            panel,
            2,
            border_radius=16
        )

        self._draw_text(
            "PROGRESIÓN DEL PERSONAJE",
            635,
            195,
            self.level_font
        )

        self._draw_text(
            f"Nivel actual: {profile.level}",
            635,
            240,
            self.stat_font
        )

        self._draw_exp_bar(
            profile,
            635,
            280,
            500
        )

        next_health = round(
            data["health"] * 1.08
        )

        self._draw_text(
            "Al siguiente nivel:",
            635,
            345,
            self.small_font,
            (155, 160, 180)
        )

        self._draw_text(
            f"Vida aproximada: {next_health}",
            635,
            375,
            self.stat_font
        )

        current_damage = data["damage"]
        next_damage = current_damage
        if (profile.level % 3) == 0:
            next_damage += 1

        self._draw_text(
            f"Ataque aproximado: {current_damage} → {next_damage}",
            635,
            410,
            self.stat_font
        )

        self._draw_text(
            f"Arma equipada: {weapon['name']}  Nv. {weapon.get('level', 1)}",
            635,
            420,
            self.stat_font,
            weapon["color"]
        )

        self._draw_text(
            "I: MEJORAR PERSONAJE",
            635,
            460,
            self.button_font,
            (255, 215, 110)
        )

        self._draw_text(
            "U también funciona como atajo.",
            635,
            492,
            self.small_font,
            (175, 180, 200)
        )

    def draw(self):
        self._draw_background()
        self._draw_header()
        self._draw_character()

        if self.current_tab == "stats":
            self._draw_stats_tab()
        elif self.current_tab == "weapon":
            self._draw_weapon_tab()
        else:
            self._draw_upgrade_tab()

        self._draw_tabs()

        if self.allow_character_change:
            hint = (
                "A / D o ← / →: personaje   •   1/2/3: pestaña   •   TAB: siguiente   •   ESC: volver"
            )
        else:
            hint = (
                "Pestaña 1/2/3   •   TAB: siguiente   •   ESC: volver   •   personaje bloqueado durante la partida"
            )

        self._draw_text(
            hint,
            55,
            self.height - 55,
            self.small_font,
            (145, 149, 168)
        )

        if self.message_timer > 0:
            message = self.small_font.render(
                self.last_message,
                True,
                (255, 215, 100)
            )
            rect = message.get_rect(
                center=(self.width // 2, 110)
            )
            self.screen.blit(message, rect)