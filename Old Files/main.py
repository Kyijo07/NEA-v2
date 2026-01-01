import pygame
import sys
import random
import json
import os
from worldGenerator import PerlinNoise
from Pathfinding import Pathfinder
from Lighting import Light, Wall, render_lightmap

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WORLD_WIDTH = 1000
WORLD_HEIGHT = 1000
TILE_SIZE = 32
FPS = 60
SAVE_FILE = "savegame.json"

WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 150, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
SANDY = (238, 203, 173)
BLACK = (0, 0, 0)


def save_game(player, follower, seed):
    data = {
        "seed": seed,
        "player": {"x": player.x, "y": player.y},
        "follower": {"x": follower.x, "y": follower.y}
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)
    print("Game saved!")


def load_game():
    if not os.path.exists(SAVE_FILE):
        print("No save file found!")
        return None
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    return data


class World:
    def __init__(self, width, height, seed=None):
        self.width = width
        self.height = height
        self.seed = seed or random.randint(1, 1000000)
        self.perlin = PerlinNoise(self.seed)
        self.tile_map = self.generate_world()

    def generate_world(self):
        elevation_map = self.perlin.generate_noise_map(self.width, self.height, 20.0)
        moisture_map = self.perlin.generate_noise_map(self.width, self.height, 15.0)
        tile_map = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                elevation = elevation_map[y][x]
                moisture = moisture_map[y][x]
                if elevation < 0.3:
                    tile_type = 'water'
                elif elevation < 0.4:
                    tile_type = 'sand'
                elif elevation < 0.7:
                    if moisture > 0.6:
                        tile_type = 'forest'
                    elif moisture > 0.3:
                        tile_type = 'grass'
                    else:
                        tile_type = 'dirt'
                else:
                    tile_type = 'mountain'
                row.append(tile_type)
            tile_map.append(row)
        return tile_map

    def get_tile_color(self, tile_type):
        colors = {
            'water': LIGHT_BLUE,
            'sand': SANDY,
            'grass': GREEN,
            'forest': DARK_GREEN,
            'dirt': BROWN,
            'mountain': GRAY
        }
        return colors.get(tile_type, WHITE)

    def is_passable(self, tile_type):
        return tile_type not in ['mountain']


class Camera:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height

    def update(self, target_x, target_y):
        self.x = target_x - self.width // 2
        self.y = target_y - self.height // 2
        self.x = max(0, min(self.x, WORLD_WIDTH * TILE_SIZE - self.width))
        self.y = max(0, min(self.y, WORLD_HEIGHT * TILE_SIZE - self.height))


class Player:
    def __init__(self, x, y, world):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.speed = 3
        self.color = RED
        self.world = world

    def can_move_to(self, new_x, new_y):
        if new_x < 0 or new_x + self.width > WORLD_WIDTH * TILE_SIZE:
            return False
        if new_y < 0 or new_y + self.height > WORLD_HEIGHT * TILE_SIZE:
            return False
        corners = [
            (new_x, new_y),
            (new_x + self.width - 1, new_y),
            (new_x, new_y + self.height - 1),
            (new_x + self.width - 1, new_y + self.height - 1)
        ]
        for cx, cy in corners:
            tile_x = cx // TILE_SIZE
            tile_y = cy // TILE_SIZE
            if 0 <= tile_x < WORLD_WIDTH and 0 <= tile_y < WORLD_HEIGHT:
                if not self.world.is_passable(self.world.tile_map[tile_y][tile_x]):
                    return False
        return True

    def move(self, dx, dy):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        if self.can_move_to(new_x, self.y):
            self.x = new_x
        if self.can_move_to(self.x, new_y):
            self.y = new_y

    def draw(self, screen, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        pygame.draw.rect(screen, self.color, (screen_x, screen_y, self.width, self.height))


class Follower:
    def __init__(self, x, y, world):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.speed = 5
        self.color = BLUE
        self.world = world
        self.path = []
        self.target_index = 0

    def update_path(self, target_x, target_y):
        grid = [[0 if self.world.is_passable(self.world.tile_map[y][x]) else 1
                 for x in range(self.world.width)]
                for y in range(self.world.height)]
        pathfinder = Pathfinder(grid)
        start = (int(self.x) // TILE_SIZE, int(self.y) // TILE_SIZE)
        end = (int(target_x) // TILE_SIZE, int(target_y) // TILE_SIZE)
        new_path = pathfinder.find_path(start, end)
        if new_path:
            self.path = new_path
            self.target_index = 0

    def move_along_path(self):
        if not self.path or self.target_index >= len(self.path):
            return
        tx, ty = self.path[self.target_index]
        target_px = tx * TILE_SIZE + TILE_SIZE // 2
        target_py = ty * TILE_SIZE + TILE_SIZE // 2
        dx = target_px - self.x
        dy = target_py - self.y
        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        self.x += self.speed * dx / dist
        self.y += self.speed * dy / dist
        if abs(dx) < 2 and abs(dy) < 2:
            self.target_index += 1

    def draw(self, screen, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        pygame.draw.rect(screen, self.color, (screen_x, screen_y, self.width, self.height))


def draw_world(screen, world, camera):
    start_x = max(0, camera.x // TILE_SIZE)
    end_x = min(world.width, (camera.x + camera.width) // TILE_SIZE + 1)
    start_y = max(0, camera.y // TILE_SIZE)
    end_y = min(world.height, (camera.y + camera.height) // TILE_SIZE + 1)
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            tile_type = world.tile_map[y][x]
            color = world.get_tile_color(tile_type)
            screen_x = x * TILE_SIZE - camera.x
            screen_y = y * TILE_SIZE - camera.y
            pygame.draw.rect(screen, color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("World with Follower Light & Save/Load")
    clock = pygame.time.Clock()

    world_seed = random.randint(1, 1000000)
    world = World(WORLD_WIDTH, WORLD_HEIGHT, world_seed)

    start_x, start_y = WORLD_WIDTH * TILE_SIZE // 2, WORLD_HEIGHT * TILE_SIZE // 2
    player = Player(start_x, start_y, world)
    follower = Follower(start_x + 50, start_y + 50, world)
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:
                    save_game(player, follower, world_seed)
                elif event.key == pygame.K_l:
                    data = load_game()
                    if data:
                        world_seed = data["seed"]
                        world = World(WORLD_WIDTH, WORLD_HEIGHT, world_seed)
                        player.x = data["player"]["x"]
                        player.y = data["player"]["y"]
                        follower.x = data["follower"]["x"]
                        follower.y = data["follower"]["y"]

        # Player movement
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1
        player.move(dx, dy)
        camera.update(player.x + player.width // 2, player.y + player.height // 2)

        # Follower path & movement
        if pygame.time.get_ticks() % 30 == 0:
            follower.update_path(player.x, player.y)
        follower.move_along_path()

        # Draw world & characters
        screen.fill(BLACK)
        draw_world(screen, world, camera)
        player.draw(screen, camera)
        follower.draw(screen, camera)

        walls = []
        margin = 2
        start_x = max(0, camera.x // TILE_SIZE - margin)
        end_x = min(world.width, (camera.x + camera.width) // TILE_SIZE + 1 + margin)
        start_y = max(0, camera.y // TILE_SIZE - margin)
        end_y = min(world.height, (camera.y + camera.height) // TILE_SIZE + 1 + margin)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = world.tile_map[y][x]
                if tile_type in ['mountain', 'forest']:
                    wx = x * TILE_SIZE - camera.x
                    wy = y * TILE_SIZE - camera.y
                    walls.append(Wall(wx, wy, wx + TILE_SIZE, wy))
                    walls.append(Wall(wx + TILE_SIZE, wy, wx + TILE_SIZE, wy + TILE_SIZE))
                    walls.append(Wall(wx + TILE_SIZE, wy + TILE_SIZE, wx, wy + TILE_SIZE))
                    walls.append(Wall(wx, wy + TILE_SIZE, wx, wy))

        # Lights (player, follower, mouse)
        lights = [
            Light(follower.x - camera.x, follower.y - camera.y, 120, (50, 50, 255))
        ]

        render_lightmap(screen, lights, walls, step=20)

        # Instructions
        font = pygame.font.Font(None, 24)
        instructions = ["Arrow Keys/WASD to move", "K: Save | L: Load"]
        for i, text in enumerate(instructions):
            rendered_text = font.render(text, True, WHITE)
            screen.blit(rendered_text, (10, 10 + i * 25))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
