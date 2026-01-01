import pygame
import math


class Light:
    def __init__(self, x, y, radius, colour=(255, 255, 255)):
        self.x = x
        self.y = y
        self.radius = radius
        self.colour = colour


class Wall:
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2


def line_intersect(x1, y1, x2, y2, x3, y3, x4, y4):
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 0.001:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    if t >= 0 and 0 <= u <= 1:
        return x1 + t * (x2 - x1), y1 + t * (y2 - y1)
    return None


def is_in_shadow(light_x, light_y, px, py, walls):
    for wall in walls:
        hit = line_intersect(light_x, light_y, px, py, wall.x1, wall.y1, wall.x2, wall.y2)
        if hit:
            wall_dx, wall_dy = hit[0] - light_x, hit[1] - light_y
            px_dx, px_dy = px - light_x, py - light_y
            if wall_dx * wall_dx + wall_dy * wall_dy < px_dx * px_dx + px_dy * px_dy:
                return True
    return False


def render_lightmap(screen, lights, walls, step=12):
    width, height = screen.get_size()
    # Small surface for pixelated lighting
    light_surface = pygame.Surface((width // step, height // step))
    light_surface.fill((20, 20, 20))  # ambient
    light_surface.lock()

    # Precompute wall segments for faster access
    wall_segments = [(w.x1, w.y1, w.x2, w.y2) for w in walls]

    for x in range(0, width, step):
        for y in range(0, height, step):
            total_r, total_g, total_b = 20, 20, 20  # ambient

            for light in lights:
                dx = x - light.x
                dy = y - light.y
                dist_sq = dx * dx + dy * dy

                if dist_sq < light.radius ** 2:
                    in_shadow = False
                    for x1, y1, x2, y2 in wall_segments:
                        hit = line_intersect(light.x, light.y, x, y, x1, y1, x2, y2)
                        if hit:
                            wx, wy = hit
                            if (wx - light.x) ** 2 + (wy - light.y) ** 2 < dist_sq:
                                in_shadow = True
                                break
                    if not in_shadow:
                        distance = math.sqrt(dist_sq)
                        falloff = 1.0 - (distance / light.radius)
                        intensity = falloff * falloff * 0.6
                        total_r = min(255, total_r + light.colour[0] * intensity)
                        total_g = min(255, total_g + light.colour[1] * intensity)
                        total_b = min(255, total_b + light.colour[2] * intensity)

            light_surface.set_at((x // step, y // step), (int(total_r), int(total_g), int(total_b)))

    light_surface.unlock()
    scaled = pygame.transform.scale(light_surface, (width, height))
    screen.blit(scaled, (0, 0), special_flags=pygame.BLEND_MULT)
