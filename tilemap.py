import pygame


class TileMap:

    def __init__(self):

        self.tileset = pygame.image.load(
            "assets/tiles/ground.png"
        ).convert_alpha()

        self.tile_size = 32

        self.tiles = []

        self.load_tiles()

    # =========================
    # CUT TILESET
    # =========================

    def load_tiles(self):

        tileset_width = self.tileset.get_width()
        tileset_height = self.tileset.get_height()

        for y in range(0, tileset_height, self.tile_size):

            for x in range(0, tileset_width, self.tile_size):

                tile = pygame.Surface(
                    (self.tile_size, self.tile_size),
                    pygame.SRCALPHA
                )

                tile.blit(
                    self.tileset,
                    (0, 0),
                    (
                        x,
                        y,
                        self.tile_size,
                        self.tile_size
                    )
                )

                self.tiles.append(tile)

    # =========================
    # DRAW TILE
    # =========================

    def draw_tile(
        self,
        screen,
        tile_index,
        x,
        y,
        camera
    ):

        if tile_index < 0:
            return

        if tile_index >= len(self.tiles):
            return

        screen.blit(
            self.tiles[tile_index],
            (
                x - int(camera.offset_x),
                y
            )
        )