import pygame
import math
import random
from typing import List, Tuple


class Tiles:
    def __init__(self, size, colour):
        self.file = file
        self.size = size
        self.image = pygame.image.load(file)
        self.rect = self.image.get_rect()
        self.tiles = []
        self.load()
        self.colour = colour


class PerlinNoise:
    def __init__(self, seed: int = None):
        random.seed(seed)
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm += self.perm
        self.gradients = [
            (1, 1),
            (-1, 1),
            (1, -1),
            (-1, -1),
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1)
        ]

    def _fade(self, t: float) -> float:
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _lerp(self, a: float, b: float, t: float) -> float:
        return a + t * (b - a)

    def _dot_product(self, grad: Tuple[int, int], x: float, y: float) -> float:
        return grad[0] * x + grad[1] * y

    def _get_gradient(self, x: int, y: int) -> Tuple[int, int]:
        hash_val = self.perm[(self.perm[x % 256] + y) % 256] % 8
        return self.gradients[hash_val]

    def noise(self, x: float, y: float) -> float:
        x0 = math.floor(x)
        y0 = math.floor(y)
        x1 = x0 + 1
        y1 = y0 + 1

        sx = x - x0
        sy = y - y0

        u = self._fade(sx)
        v = self._fade(sy)

        g00 = self._get_gradient(x0, y0)
        g10 = self._get_gradient(x1, y0)
        g01 = self._get_gradient(x0, y1)
        g11 = self._get_gradient(x1, y1)

        n00 = self._dot_product(g00, sx, sy)
        n10 = self._dot_product(g10, sx - 1, sy)
        n01 = self._dot_product(g01, sx, sy - 1)
        n11 = self._dot_product(g11, sx - 1, sy - 1)
        nx0 = self._lerp(n00, n10, u)
        nx1 = self._lerp(n01, n11, u)
        result = self._lerp(nx0, nx1, v)

        return (result + 1) * 0.5

    def generate_noise_map(self, width: int, height: int, scale: float = 1.0) -> List[List[float]]:
        if scale <= 0:
            scale = 0.0001

        noise_map = [[0 for _ in range(width)] for _ in range(height)]

        for y in range(height):
            for x in range(width):
                sample_x = x / scale
                sample_y = y / scale

                noise_value = self.noise(sample_x, sample_y)

                noise_map[y][x] = noise_value

        return noise_map


if __name__ == "__main__":
    pygame.init()
    s_width, s_height = 20, 20
    screen = pygame.display.set_mode((s_width, s_height))
    seed = None
    perlin = PerlinNoise(seed)

    width, height = 20, 20
    world = pygame.Surface((width, height))

    scale = 10.0
    print(seed)

    noise_map = perlin.generate_noise_map(width, height, scale)
    with open('../Prototype (no need to look)/World Generation/example.txt', 'w') as file:
        file.write(str(noise_map))
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        world.fill((0, 0, 0))
        pygame.display.flip()
        pygame.display.update()
        clock.tick(60)
        print(clock.get_fps())
    pygame.quit()
