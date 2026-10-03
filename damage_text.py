import pygame


class DamageText:

    def __init__(self, x, y, damage, crit=False):

        self.x = x
        self.y = y

        self.damage = damage

        self.crit = crit

        self.timer = 0.9 if crit else 0.8

        self.max_timer = self.timer

        size = 44 if crit else 32

        self.font = pygame.font.Font(None, size)

    def update(self, dt):

        self.timer -= dt

        self.y -= 40 * dt

    def draw(self, screen, camera):

        alpha = int(
            255 * (self.timer / self.max_timer)
        )

        if alpha < 0:
            alpha = 0

        text = self.font.render(
            str(self.damage),
            True,
            (255, 215, 0) if self.crit else (255, 255, 255)
        )

        text.set_alpha(alpha)

        text_rect = text.get_rect(
            center=(
                int(self.x - camera.offset_x),
                int(self.y)
            )
        )

        screen.blit(
            text,
            text_rect
        )

    def is_finished(self):

        return self.timer <= 0