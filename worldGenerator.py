import pygame
import math
import random


class Tiles:
    def __init__(self, tile_size):
        self.tile_size = tile_size
        self.tiles = []
        self.load()


class PerlinNoise:
    def __init__(self, seed):
        random.seed(seed)
        self.permutation_table = list(range(256))
        random.shuffle(self.permutation_table)
        self.permutation_table += self.permutation_table
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

    def _fade(self, distance):
        return distance * distance * distance * (distance * (distance * 6 - 15) + 10)

    def _lerp(self, start_value, end_value, interpolation_factor):
        return start_value + interpolation_factor * (end_value - start_value)

    def _dot_product(self, gradient, x, y):
        return gradient[0] * x + gradient[1] * y

    def _get_gradient(self, x, y):
        hash_value = self.permutation_table[(self.permutation_table[x % 256] + y) % 256] % 8
        return self.gradients[hash_value]

    def noise(self, x, y):
        grid_x0 = math.floor(x)
        grid_y0 = math.floor(y)
        grid_x1 = grid_x0 + 1
        grid_y1 = grid_y0 + 1

        delta_x = x - grid_x0
        delta_y = y - grid_y0

        fade_x = self._fade(delta_x)
        fade_y = self._fade(delta_y)

        grad_bottom_left = self._get_gradient(grid_x0, grid_y0)
        grad_bottom_right = self._get_gradient(grid_x1, grid_y0)
        grad_top_left = self._get_gradient(grid_x0, grid_y1)
        grad_top_right = self._get_gradient(grid_x1, grid_y1)

        dot_bottom_left = self._dot_product(grad_bottom_left, delta_x, delta_y)
        dot_bottom_right = self._dot_product(grad_bottom_right, delta_x - 1, delta_y)
        dot_top_left = self._dot_product(grad_top_left, delta_x, delta_y - 1)
        dot_top_right = self._dot_product(grad_top_right, delta_x - 1, delta_y - 1)

        interp_x_bottom = self._lerp(dot_bottom_left, dot_bottom_right, fade_x)
        interp_x_top = self._lerp(dot_top_left, dot_top_right, fade_x)

        final_noise_value = self._lerp(interp_x_bottom, interp_x_top, fade_y)

        return (final_noise_value + 1) * 0.5

    def generate_noise_map(self, map_width, map_height, scale_factor=1.0):
        if scale_factor <= 0:
            scale_factor = 0.0001

        noise_map = [[0 for _ in range(map_width)] for _ in range(map_height)]

        for y in range(map_height):
            for x in range(map_width):
                sample_x = x / scale_factor
                sample_y = y / scale_factor

                noise_value = self.noise(sample_x, sample_y)

                noise_map[y][x] = noise_value

        return noise_map


if __name__ == "__main__":
    pygame.init()
    screen_width, screen_height = 20, 20
    screen = pygame.display.set_mode((screen_width, screen_height))
    seed_value = None
    perlin = PerlinNoise(seed_value)

    map_width, map_height = 100, 100
    world_surface = pygame.Surface((map_width, map_height))

    scale_factor = 10.0
    print(seed_value)

    noise_map = perlin.generate_noise_map(map_width, map_height, scale_factor)
    with open('example.txt', 'w') as output_file:
        output_file.write(str(noise_map))

    clock = pygame.time.Clock()
    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
        world_surface.fill((0, 0, 0))
        pygame.display.flip()
        pygame.display.update()
        clock.tick(60)
        print(clock.get_fps())
    pygame.quit()
