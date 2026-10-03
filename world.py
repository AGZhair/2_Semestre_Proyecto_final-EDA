import pygame


class Platform:

    def __init__(self, x, y, width, height):

        self.rect = pygame.Rect(
            x,
            y,
            width,
            height
        )

    # =========================
    # DRAW PLATFORM WITH TILES
    # =========================

    def draw(
        self,
        screen,
        camera,
        tilemap
    ):

        tile_size = tilemap.tile_size

        tiles_x = self.rect.width // tile_size

        tiles_y = self.rect.height // tile_size

        # TILE INDICES
        top_tile = 0
        middle_tile = 24
        grass_tile = -1

        for row in range(tiles_y):

            for col in range(tiles_x):

                draw_x = (
                    self.rect.x
                    + col * tile_size
                )

                draw_y = (
                    self.rect.y
                    + row * tile_size
                )

                # TOP
                if row == 0:

                    tile_index = top_tile

                else:

                    tile_index = middle_tile

                tilemap.draw_tile(
                    screen,
                    tile_index,
                    draw_x,
                    draw_y,
                    camera
                )

        # GRASS DECORATION
        for col in range(tiles_x):

            draw_x = (
                self.rect.x
                + col * tile_size
            )

            draw_y = self.rect.y - 12

            tilemap.draw_tile(
                screen,
                grass_tile,
                draw_x,
                draw_y,
                camera
            )