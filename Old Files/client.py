import pygame
import sys
import socket
import json
import threading
from worldGenerator import PerlinNoise
from Lighting import Light, Wall, render_lightmap

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WORLD_WIDTH = 1000
WORLD_HEIGHT = 1000
TILE_SIZE = 32
FPS = 60

HOST = '127.0.0.1'
PORT = 50000


class World:
    def __init__(self, width, height, seed):
        self.width = width
        self.height = height
        self.perlin = PerlinNoise(seed)
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
                    row.append('water')
                elif elevation < 0.4:
                    row.append('sand')
                elif elevation < 0.7:
                    if moisture > 0.6:
                        row.append('forest')
                    elif moisture > 0.3:
                        row.append('grass')
                    else:
                        row.append('dirt')
                else:
                    row.append('mountain')
            tile_map.append(row)
        return tile_map

    def get_tile_color(self, tile_type):
        colors = {
            'water': (173, 216, 230),
            'sand': (238, 203, 173),
            'grass': (0, 255, 0),
            'forest': (0, 150, 0),
            'dirt': (139, 69, 19),
            'mountain': (128, 128, 128)
        }
        return colors.get(tile_type, (255, 255, 255))


class Player:
    def __init__(self, x, y, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.speed = 3
        self.color = color

    def move(self, dx, dy, world):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        # simple boundary check
        if 0 <= new_x <= WORLD_WIDTH * TILE_SIZE - self.width:
            self.x = new_x
        if 0 <= new_y <= WORLD_HEIGHT * TILE_SIZE - self.height:
            self.y = new_y

    def draw(self, screen, camera):
        pygame.draw.rect(screen, self.color,
                         (self.x - camera.x, self.y - camera.y, self.width, self.height))


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


class NetworkClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.player_id = None
        self.world_seed = None
        self.other_players = {}  # player_id -> {"x":, "y":}

        threading.Thread(target=self.recv_loop, daemon=True).start()

    def recv_loop(self):
        buffer = ""
        while True:
            try:
                data = self.sock.recv(4096).decode()
                if not data:
                    continue
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip():
                        continue
                    packet = json.loads(line)
                    if packet["command"] == "SETUP":
                        self.player_id = packet["data"]["PlayerID"]
                        self.world_seed = packet["data"]["WorldSeed"]
                        self.x = packet["data"]["PlayerX"]
                        self.y = packet["data"]["PlayerY"]
                    elif packet["command"] == "UPDATE_POS":
                        for pid, pos in packet["data"].items():
                            self.other_players[pid] = pos
            except Exception as e:
                print("Connection lost:", e)
                break

    def send_move(self, x, y):
        if self.player_id is None:
            return
        packet = {"command": "MOVE", "data": {"x": x, "y": y}}
        try:
            self.sock.send((json.dumps(packet) + "\n").encode())
        except:
            pass


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Multiplayer World with Lighting")
    clock = pygame.time.Clock()

    network = NetworkClient()

    # Wait for world seed from server
    while network.world_seed is None:
        pygame.time.wait(10)

    world = World(WORLD_WIDTH, WORLD_HEIGHT, network.world_seed)
    player = Player(network.x, network.y)
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1

        player.move(dx, dy, world)
        camera.update(player.x + player.width // 2, player.y + player.height // 2)
        network.send_move(player.x, player.y)

        screen.fill((0, 0, 0))
        start_x = max(0, camera.x // TILE_SIZE)
        end_x = min(world.width, (camera.x + camera.width) // TILE_SIZE + 1)
        start_y = max(0, camera.y // TILE_SIZE)
        end_y = min(world.height, (camera.y + camera.height) // TILE_SIZE + 1)
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                color = world.get_tile_color(world.tile_map[y][x])
                screen.fill(color, rect=(x * TILE_SIZE - camera.x, y * TILE_SIZE - camera.y, TILE_SIZE, TILE_SIZE))

        walls = []
        margin = 2
        for y in range(start_y - margin, end_y + margin):
            for x in range(start_x - margin, end_x + margin):
                if 0 <= x < world.width and 0 <= y < world.height:
                    tile = world.tile_map[y][x]
                    if tile in ['mountain', 'forest']:
                        wx = x * TILE_SIZE - camera.x
                        wy = y * TILE_SIZE - camera.y
                        walls.extend([
                            Wall(wx, wy, wx + TILE_SIZE, wy),
                            Wall(wx + TILE_SIZE, wy, wx + TILE_SIZE, wy + TILE_SIZE),
                            Wall(wx + TILE_SIZE, wy + TILE_SIZE, wx, wy + TILE_SIZE),
                            Wall(wx, wy + TILE_SIZE, wx, wy)
                        ])

        lights = [
            Light(player.x - camera.x + player.width // 2,
                  player.y - camera.y + player.height // 2, 150, (255, 255, 255))
        ]
        for pid, pos in network.other_players.items():
            if pid != network.player_id:
                lights.append(Light(pos["x"] - camera.x + 12,
                                    pos["y"] - camera.y + 12, 120, (255, 255, 255)))

        render_lightmap(screen, lights, walls, step=25)

        for pid, pos in network.other_players.items():
            if pid != network.player_id:
                pygame.draw.rect(screen, (255, 255, 255),
                                 (pos["x"] - camera.x, pos["y"] - camera.y, 24, 24))
        player.draw(screen, camera)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
