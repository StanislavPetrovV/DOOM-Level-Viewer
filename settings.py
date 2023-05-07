import math
from pygame.math import Vector2 as vec2

DOOM_RES = DOOM_W, DOOM_H = 320, 200

SCALE = 2.25
WIN_RES = WIDTH, HEIGHT = int(DOOM_W * SCALE), int(DOOM_H * SCALE)
H_WIDTH, H_HEIGHT = WIDTH // 2, HEIGHT // 2

FOV = 90.0
H_FOV = FOV / 2

PLAYER_SPEED = 0.3
PLAYER_ROT_SPEED = 0.12
PLAYER_HEIGHT = 41

SCREEN_DIST = H_WIDTH / math.tan(math.radians(H_FOV))

COLOR_KEY = (152, 0, 136)