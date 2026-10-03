import random


class Camera:

    def __init__(self):

        self.offset_x = 0

        self.target_offset_x = 0

        # SCREEN SHAKE
        self.shake_intensity = 0

        self.shake_duration = 0

    # =========================
    # FOLLOW PLAYER
    # =========================

    def follow(
        self,
        target,
        screen_width,
        world_width
    ):

        self.target_offset_x = (
            target.rect.centerx
            - screen_width // 2
        )

        # LIMITES DEL MUNDO
        if self.target_offset_x < 0:

            self.target_offset_x = 0

        max_offset = (
            world_width - screen_width
        )

        if self.target_offset_x > max_offset:

            self.target_offset_x = max_offset

    # =========================
    # SCREEN SHAKE
    # =========================

    def shake(self, intensity, duration):

        self.shake_intensity = intensity

        self.shake_duration = duration

    # =========================
    # UPDATE
    # =========================

    def update(self, dt):

        # SMOOTH CAMERA
        self.offset_x += (
            self.target_offset_x
            - self.offset_x
        ) * 0.08

        # CONVERTIR A ENTERO
        self.offset_x = int(self.offset_x)

        # SHAKE TIMER
        if self.shake_duration > 0:

            self.shake_duration -= dt

        else:

            self.shake_intensity = 0

    # =========================
    # SHAKE OFFSET
    # =========================

    def get_shake_offset(self):

        if self.shake_intensity > 0:

            return random.randint(
                -self.shake_intensity,
                self.shake_intensity
            )

        return 0