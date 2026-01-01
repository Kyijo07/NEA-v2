import math


class Node:
    def __init__(self, x: int, y: int, walkable: bool = True):
        self.x = x
        self.y = y
        self.walkable = walkable
        self.g_cost = 0  # Distance from start node
        self.h_cost = 0  # Heuristic distance to end node
        self.f_cost = 0  # Total cost (g + h)
        self.parent = None


class Pathfinder:
    def __init__(self, grid):
        self.height = len(grid)
        self.width = len(grid[0]) if grid else 0
        self.nodes = []

        for y in range(self.height):
            row = []
            for x in range(self.width):
                walkable = grid[y][x] == 0
                row.append(Node(x, y, walkable))
            self.nodes.append(row)

    def get_node(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.nodes[y][x]
        return None

    def get_neighbors(self, node):
        neighbors = []
        directions = [
            (-1, -1), (-1, 0), (-1, 1),  # Left column
            (0, -1), (0, 1),  # Middle column (skip center)
            (1, -1), (1, 0), (1, 1)  # Right column
        ]

        for dx, dy in directions:
            neighbor = self.get_node(node.x + dx, node.y + dy)
            if neighbor and neighbor.walkable:
                neighbors.append(neighbor)

        return neighbors

    def calculate_distance(self, node_a, node_b):
        dx = abs(node_a.x - node_b.x)
        dy = abs(node_a.y - node_b.y)
        return math.sqrt(dx * dx + dy * dy)

    def calculate_heuristic(self, node, target):
        return abs(node.x - target.x) + abs(node.y - target.y)

    def reconstruct_path(self, end_node):
        path = []
        current = end_node

        while current is not None:
            path.append((current.x, current.y))
            current = current.parent

        return path[::-1]  # Reverse to get start->end path

    def find_path(self, start, end):
        start_node = self.get_node(start[0], start[1])
        end_node = self.get_node(end[0], end[1])

        if not start_node or not end_node:
            return None

        if not start_node.walkable or not end_node.walkable:
            return None

        start_node.g_cost = 0
        start_node.h_cost = self.calculate_heuristic(start_node, end_node)
        start_node.f_cost = start_node.g_cost + start_node.h_cost

        open_set = [start_node]
        closed_set = set()

        while open_set:
            current_node = min(open_set, key=lambda n: n.f_cost)
            open_set.remove(current_node)
            closed_set.add(current_node)
    
            if current_node == end_node:
                return self.reconstruct_path(current_node)

            for neighbor in self.get_neighbors(current_node):
                if neighbor in closed_set:
                    continue

                new_g_cost = current_node.g_cost + self.calculate_distance(current_node, neighbor)

                if neighbor not in open_set:
                    open_set.append(neighbor)
                elif new_g_cost >= neighbor.g_cost:
                    continue

                neighbor.parent = current_node
                neighbor.g_cost = new_g_cost
                neighbor.h_cost = self.calculate_heuristic(neighbor, end_node)
                neighbor.f_cost = neighbor.g_cost + neighbor.h_cost

        return None


def print_grid_with_path(grid, path=None):
    if path is None:
        path = []

    path_set = set(path)

    for y in range(len(grid)):
        row = ""
        for x in range(len(grid[0])):
            if (x, y) in path_set:
                if (x, y) == path[0]:
                    row += "S "  # Start
                elif (x, y) == path[-1]:
                    row += "E "  # End
                else:
                    row += "* "  # Path
            elif grid[y][x] == 1:
                row += "# "  # Wall
            else:
                row += ". "  # Empty
        print(row)
    print()


if __name__ == "__main__":
    sample_grid = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 1, 1, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 1, 1, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    pathfinder = Pathfinder(sample_grid)

    start_pos = (0, 0)
    end_pos = (3, 5)

    print("Grid layout (# = wall, . = empty):")
    print_grid_with_path(sample_grid)

    path = pathfinder.find_path(start_pos, end_pos)

    if path:
        print(f"Path found! Length: {len(path)}")
        print(f"Path coordinates: {path}")
        print("\nGrid with path (S = start, E = end, * = path):")
        print_grid_with_path(sample_grid, path)
    else:
        print("No path found!")
