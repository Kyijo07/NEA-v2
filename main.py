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


"""
Name: save_game
Parameters: player (Player), follower (Follower), seed (int)
Returns: None
Purpose: Saves the current game state to disk.
"""
def save_game(player, follower, seed):
    data = {
        "seed": seed,
        "player": {"x": player.x, "y": player.y},
        "follower": {"x": follower.x, "y": follower.y}
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)
    print("Game saved!")


"""
Name: load_game
Parameters: None
Returns: dict | None
Purpose: Loads the saved game state from disk.
"""
def load_game():
    if not os.path.exists(SAVE_FILE):
        print("No save file found!")
        return None
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    return data


class World:
    """
    Name: __init__
    Parameters: width (int), height (int), seed (int | None)
    Returns: None
    Purpose: Initializes the game world and generates terrain.
    """
    def __init__(self, width, height, seed=None):
        self.width = width
        self.height = height
        self.seed = seed or random.randint(1, 1000000)
        self.perlin = PerlinNoise(self.seed)
        self.tile_map = self.generate_world()

    """
    Name: generate_world
    Parameters: None
    Returns: list[list[str]]
    Purpose: Generates a tile map using Perlin noise for elevation and moisture.
    """
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

    """
    Name: get_tile_color
    Parameters: tile_type (str)
    Returns: tuple[int, int, int]
    Purpose: Returns the display color associated with a tile type.
    """
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

    """
    Name: is_passable
    Parameters: tile_type (str)
    Returns: bool
    Purpose: Determines whether an entity can move onto a given tile.
    """
    def is_passable(self, tile_type):
        return tile_type not in ['mountain']


class Camera:
    """
    Name: __init__
    Parameters: width (int), height (int)
    Returns: None
    Purpose: Controls the visible portion of the world.
    """
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height

    """
    Name: update
    Parameters: target_x (float), target_y (float)
    Returns: None
    Purpose: Centers the camera on a target position while clamping to world bounds.
    """
    def update(self, target_x, target_y):
        self.x = target_x - self.width // 2
        self.y = target_y - self.height // 2
        self.x = max(0, min(self.x, WORLD_WIDTH * TILE_SIZE - self.width))
        self.y = max(0, min(self.y, WORLD_HEIGHT * TILE_SIZE - self.height))


class Player:
    """
    Name: __init__
    Parameters: x (float), y (float), world (World)
    Returns: None
    Purpose: Represents the player-controlled character.
    """
    def __init__(self, x, y, world):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.speed = 3
        self.color = RED
        self.world = world

    """
    Name: can_move_to
    Parameters: new_x (float), new_y (float)
    Returns: bool
    Purpose: Checks collision and terrain passability for movement.
    """
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
            if not self.world.is_passable(self.world.tile_map[tile_y][tile_x]):
                return False

        return True

    """
    Name: move
    Parameters: dx (int), dy (int)
    Returns: None
    Purpose: Moves the player while respecting collisions.
    """
    def move(self, dx, dy):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        if self.can_move_to(new_x, self.y):
            self.x = new_x
        if self.can_move_to(self.x, new_y):
            self.y = new_y

    """
    Name: draw
    Parameters: screen (pygame.Surface), camera (Camera)
    Returns: None
    Purpose: Renders the player relative to the camera.
    """
    def draw(self, screen, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        pygame.draw.rect(screen, self.color, (screen_x, screen_y, self.width, self.height))


class Follower:
    """
    Name: __init__
    Parameters: x (float), y (float), world (World)
    Returns: None
    Purpose: Represents an AI-controlled follower using pathfinding.
    """
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

    """
    Name: update_path
    Parameters: target_x (float), target_y (float)
    Returns: None
    Purpose: Recalculates the path to a target position.
    """
    def update_path(self, target_x, target_y):
        grid = [
            [0 if self.world.is_passable(self.world.tile_map[y][x]) else 1
             for x in range(self.world.width)]
            for y in range(self.world.height)
        ]

        pathfinder = Pathfinder(grid)
        start = (int(self.x) // TILE_SIZE, int(self.y) // TILE_SIZE)
        end = (int(target_x) // TILE_SIZE, int(target_y) // TILE_SIZE)

        new_path = pathfinder.find_path(start, end)
        if new_path:
            self.path = new_path
            self.target_index = 0

    """
    Name: move_along_path
    Parameters: None
    Returns: None
    Purpose: Moves the follower toward the next path node.
    """
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

    """
    Name: draw
    Parameters: screen (pygame.Surface), camera (Camera)
    Returns: None
    Purpose: Renders the follower relative to the camera.
    """
    def draw(self, screen, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        pygame.draw.rect(screen, self.color, (screen_x, screen_y, self.width, self.height))


"""
Name: draw_world
Parameters: screen (pygame.Surface), world (World), camera (Camera)
Returns: None
Purpose: Draws visible world tiles based on the camera position.
"""
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


"""
Name: main
Parameters: None
Returns: None
Purpose: Entry point that initializes and runs the game loop.
"""
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("World with Follower Light & Save/Load")
    clock = pygame.time.Clock()

    world_seed = random.randint(1, 1000000)
    world = World(WORLD_WIDTH, WORLD_HEIGHT, world_seed)

    start_x = WORLD_WIDTH * TILE_SIZE // 2
    start_y = WORLD_HEIGHT * TILE_SIZE // 2

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

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1

        player.move(dx, dy)
        camera.update(player.x + player.width // 2, player.y + player.height // 2)

        if pygame.time.get_ticks() % 30 == 0:
            follower.update_path(player.x, player.y)
        follower.move_along_path()

        screen.fill(BLACK)
        draw_world(screen, world, camera)
        player.draw(screen, camera)
        follower.draw(screen, camera)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
