# algorithms.py
from collections import deque

def bfs(grid, start, goal):
    """Breadth-First Search"""
    rows, cols = len(grid), len(grid[0])
    queue = deque([(start, [start])])
    visited = set([start])
    
    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == goal:
            return path
        
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] != 1 and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))
    return None

def dfs(grid, start, goal):
    """Depth-First Search"""
    rows, cols = len(grid), len(grid[0])
    stack = [(start, [start])]
    visited = set([start])
    
    while stack:
        (x, y), path = stack.pop()
        if (x, y) == goal:
            return path
        
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] != 1 and (nx, ny) not in visited:
                visited.add((nx, ny))
                stack.append(((nx, ny), path + [(nx, ny)]))
    return None

def heuristic(a, b):
    """Manhattan distance"""
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(grid, start, goal):
    """A* Search"""
    rows, cols = len(grid), len(grid[0])
    open_set = [(0, start, [start])]  # (f_score, position, path)
    visited = set()
    
    while open_set:
        # Sort by f_score (simplified; use priority queue for efficiency)
        open_set.sort()
        f, (x, y), path = open_set.pop(0)
        
        if (x, y) == goal:
            return path
        
        if (x, y) in visited:
            continue
        visited.add((x, y))
        
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] != 1 and (nx, ny) not in visited:
                g = len(path)  # cost so far
                h = heuristic((nx, ny), goal)
                f = g + h
                open_set.append((f, (nx, ny), path + [(nx, ny)]))
    return None

def greedy(grid, start, goal):
    """Greedy Best-First Search (uses only heuristic)"""
    rows, cols = len(grid), len(grid[0])
    open_set = [(heuristic(start, goal), start, [start])]
    visited = set()
    
    while open_set:
        open_set.sort()
        h, (x, y), path = open_set.pop(0)
        
        if (x, y) == goal:
            return path
        
        if (x, y) in visited:
            continue
        visited.add((x, y))
        
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] != 1 and (nx, ny) not in visited:
                open_set.append((heuristic((nx, ny), goal), (nx, ny), path + [(nx, ny)]))
    return None