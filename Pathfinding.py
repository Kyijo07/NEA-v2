import math


class Node:
    def __init__(self, x: int, y: int, walkable: bool = True):
        self.x = x  # X-coordinate of the node
        self.y = y  # Y-coordinate of the node
        self.walkable = walkable  # Whether the node is walkable (True or False)
        self.g_cost = 0  # The cost from the start node to this node
        self.h_cost = 0  # Heuristic cost: estimated cost from this node to the target
        self.f_cost = 0  # Total cost (g_cost + h_cost)
        self.parent = None  # The parent node to reconstruct the path


class Pathfinder:
    def __init__(self, grid):
        self.grid_height = len(grid)  # Number of rows in the grid
        self.grid_width = len(grid[0]) if grid else 0  # Number of columns in the grid
        self.grid_nodes = []

        # Convert the grid into a 2D list of nodes
        for y in range(self.grid_height):
            row = []
            for x in range(self.grid_width):
                walkable = grid[y][x] == 0  # 0 = walkable, 1 = wall
                row.append(Node(x, y, walkable))
            self.grid_nodes.append(row)

    def get_node_at(self, x, y):
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            return self.grid_nodes[y][x]
        return None

    def get_neighbors(self, current_node):
        neighbors = []
        directions = [
            (-1, -1), (-1, 0), (-1, 1),  # Top-left, top, top-right
            (0, -1), (0, 1),  # Left, right
            (1, -1), (1, 0), (1, 1)  # Bottom-left, bottom, bottom-right
        ]

        for dx, dy in directions:
            neighbor = self.get_node_at(current_node.x + dx, current_node.y + dy)
            if neighbor and neighbor.walkable:
                neighbors.append(neighbor)

        return neighbors

    def calculate_distance(self, node_a, node_b):
        dx = abs(node_a.x - node_b.x)
        dy = abs(node_a.y - node_b.y)
        return math.sqrt(dx * dx + dy * dy)  # Euclidean distance

    def calculate_heuristic(self, current_node, target_node):
        return abs(current_node.x - target_node.x) + abs(current_node.y - target_node.y)  # Manhattan distance

    def reconstruct_path(self, end_node):
        path = []
        current = end_node
        while current is not None:
            path.append((current.x, current.y))
            current = current.parent
        return path[::-1]  # Return the path from start to end (reversed)

    def find_path(self, start_position, end_position):
        start_node = self.get_node_at(start_position[0], start_position[1])
        end_node = self.get_node_at(end_position[0], end_position[1])

        if not start_node or not end_node:
            return None  # No valid start or end node

        if not start_node.walkable or not end_node.walkable:
            return None  # Start or end node is blocked

        # Initialize the start node
        start_node.g_cost = 0
        start_node.h_cost = self.calculate_heuristic(start_node, end_node)
        start_node.f_cost = start_node.g_cost + start_node.h_cost

        open_set = [start_node]  # Nodes to explore
        closed_set = set()  # Explored nodes

        while open_set:
            # Get the node with the lowest f_cost from the open set
            current_node = min(open_set, key=lambda n: n.f_cost)
            open_set.remove(current_node)
            closed_set.add(current_node)

            # If we've reached the target node, reconstruct the path
            if current_node == end_node:
                return self.reconstruct_path(current_node)

            # Explore neighbors
            for neighbor in self.get_neighbors(current_node):
                if neighbor in closed_set:
                    continue  # Skip already explored neighbors

                new_g_cost = current_node.g_cost + self.calculate_distance(current_node, neighbor)

                if neighbor not in open_set:
                    open_set.append(neighbor)
                elif new_g_cost >= neighbor.g_cost:
                    continue  # Skip if a worse path is found

                neighbor.parent = current_node
                neighbor.g_cost = new_g_cost
                neighbor.h_cost = self.calculate_heuristic(neighbor, end_node)
                neighbor.f_cost = neighbor.g_cost + neighbor.h_cost

        return None  # No path found


def display_grid_with_path(grid, path=None):
    if path is None:
        path = []

    path_set = set(path)

    for y in range(len(grid)):
        row = ""
        for x in range(len(grid[0])):
            if (x, y) in path_set:
                if (x, y) == path[0]:
                    row += "S "  # Start point
                elif (x, y) == path[-1]:
                    row += "E "  # End point
                else:
                    row += "* "  # Path points
            elif grid[y][x] == 1:
                row += "# "  # Wall
            else:
                row += ". "  # Empty space
        print(row)
    print()

# Testing the algorithm
if __name__ == "__main__":
    # Example grid (0 = walkable, 1 = wall)
    example_grid = [
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

    # Create Pathfinder instance with the grid
    pathfinder = Pathfinder(example_grid)

    # Start and end positions (x, y)
    start_pos = (0, 0)
    end_pos = (3, 5)

    # Display the grid
    print("Grid layout (# = wall, . = empty):")
    display_grid_with_path(example_grid)

    # Find the path
    path = pathfinder.find_path(start_pos, end_pos)

    if path:
        print(f"Path found! Length: {len(path)}")
        print(f"Path coordinates: {path}")
        print("\nGrid with path (S = start, E = end, * = path):")
        display_grid_with_path(example_grid, path)
    else:
        print("No path found!")
