import math


class Node:
    """
    Name: __init__
    Parameters: x (int), y (int), walkable (bool)
    Returns: None
    Purpose: Represents a single grid node used in pathfinding.
    """
    def __init__(self, x: int, y: int, walkable: bool = True):
        self.x = x  # X-coordinate of the node
        self.y = y  # Y-coordinate of the node
        self.walkable = walkable  # Whether the node is walkable
        self.g_cost = 0  # Cost from start node
        self.h_cost = 0  # Heuristic cost to target
        self.f_cost = 0  # Total cost (g + h)
        self.parent = None  # Parent node for path reconstruction


class Pathfinder:
    """
    Name: __init__
    Parameters: grid (list[list[int]])
    Returns: None
    Purpose: Initializes the grid and converts it into Node objects.
    """
    def __init__(self, grid):
        self.grid_height = len(grid)
        self.grid_width = len(grid[0]) if grid else 0
        self.grid_nodes = []

        for y in range(self.grid_height):
            row = []
            for x in range(self.grid_width):
                walkable = grid[y][x] == 0
                row.append(Node(x, y, walkable))
            self.grid_nodes.append(row)

    """
    Name: get_node_at
    Parameters: x (int), y (int)
    Returns: Node | None
    Purpose: Safely retrieves a node at the given coordinates.
    """
    def get_node_at(self, x, y):
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            return self.grid_nodes[y][x]
        return None

    """
    Name: get_neighbors
    Parameters: current_node (Node)
    Returns: list[Node]
    Purpose: Retrieves all walkable neighboring nodes (including diagonals).
    """
    def get_neighbors(self, current_node):
        neighbors = []
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for dx, dy in directions:
            neighbor = self.get_node_at(current_node.x + dx, current_node.y + dy)
            if neighbor and neighbor.walkable:
                neighbors.append(neighbor)

        return neighbors

    """
    Name: calculate_distance
    Parameters: node_a (Node), node_b (Node)
    Returns: float
    Purpose: Calculates the movement cost between two nodes using Euclidean distance.
    """
    def calculate_distance(self, node_a, node_b):
        dx = abs(node_a.x - node_b.x)
        dy = abs(node_a.y - node_b.y)
        return math.sqrt(dx * dx + dy * dy)

    """
    Name: calculate_heuristic
    Parameters: current_node (Node), target_node (Node)
    Returns: int
    Purpose: Estimates the cost from the current node to the target using Manhattan distance.
    """
    def calculate_heuristic(self, current_node, target_node):
        return abs(current_node.x - target_node.x) + abs(current_node.y - target_node.y)

    """
    Name: reconstruct_path
    Parameters: end_node (Node)
    Returns: list[tuple[int, int]]
    Purpose: Reconstructs the path from end node back to start.
    """
    def reconstruct_path(self, end_node):
        path = []
        current = end_node
        while current is not None:
            path.append((current.x, current.y))
            current = current.parent
        return path[::-1]

    """
    Name: find_path
    Parameters: start_position (tuple[int, int]), end_position (tuple[int, int])
    Returns: list[tuple[int, int]] | None
    Purpose: Finds a path using the A* pathfinding algorithm.
    """
    def find_path(self, start_position, end_position):
        start_node = self.get_node_at(*start_position)
        end_node = self.get_node_at(*end_position)

        if not start_node or not end_node:
            return None

        if not start_node.walkable or not end_node.walkable:
            return None

        start_node.g_cost = 0
        start_node.h_cost = self.calculate_heuristic(start_node, end_node)
        start_node.f_cost = start_node.h_cost

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


"""
Name: display_grid_with_path
Parameters: grid (list[list[int]]), path (list[tuple[int, int]] | None)
Returns: None
Purpose: Prints the grid to the console with an optional path overlay.
"""
def display_grid_with_path(grid, path=None):
    if path is None:
        path = []

    path_set = set(path)

    for y in range(len(grid)):
        row = ""
        for x in range(len(grid[0])):
            if (x, y) in path_set:
                if (x, y) == path[0]:
                    row += "S "
                elif (x, y) == path[-1]:
                    row += "E "
                else:
                    row += "¬ "
            elif grid[y][x] == 1:
                row += "# "
            else:
                row += ". "
        print(row)
    print()
