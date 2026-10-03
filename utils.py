import pygame

def load_spritesheet(path, frame_width, frame_height):
    sheet = pygame.image.load(path).convert_alpha()

    sheet_width = sheet.get_width()

    frames = []

    for i in range(sheet_width // frame_width):

        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)

        frame.blit(
            sheet,
            (0, 0),
            (i * frame_width, 0, frame_width, frame_height)
        )

        frames.append(frame)

    return frames