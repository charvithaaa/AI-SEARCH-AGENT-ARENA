# simulation.py
import random
from algorithms import bfs, dfs, astar, greedy

class AgentArena:
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.grid = [[0]*width for _ in range(height)]  # 0=empty, 1=wall
        self.agents = []
        self.foods = []
        self.turn = 0

    def add_agent(self, start_pos, algorithm="BFS"):
        agent = {
            'pos': start_pos,
            'algorithm': algorithm,
            'food_collected': 0,
            'steps': 0,
            'path': []
        }
        self.agents.append(agent)
        return agent

    def add_food(self, pos):
        if pos not in self.foods:
            self.foods.append(pos)

    def spawn_random_food(self, count=1):
        for _ in range(count):
            attempts = 0
            while attempts < 100:
                x = random.randint(0, self.width-1)
                y = random.randint(0, self.height-1)
                pos = (x, y)
                if pos not in self.foods and all(agent['pos'] != pos for agent in self.agents):
                    self.foods.append(pos)
                    break
                attempts += 1

    def nearest_food(self, agent_pos):
        if not self.foods:
            return None
        return min(self.foods, key=lambda f: abs(f[0]-agent_pos[0]) + abs(f[1]-agent_pos[1]))

    def is_valid_move(self, pos, agent_idx):
        x, y = pos
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        if self.grid[x][y] == 1:  # wall
            return False
        # Optional: prevent agents from occupying same cell? We'll allow for now.
        return True

    def random_move(self, agent_idx):
        agent = self.agents[agent_idx]
        x, y = agent['pos']
        directions = [(0,1),(1,0),(0,-1),(-1,0)]
        random.shuffle(directions)
        for dx, dy in directions:
            new_pos = (x+dx, y+dy)
            if self.is_valid_move(new_pos, agent_idx):
                return new_pos
        return agent['pos']  # no move possible

    def get_next_move(self, agent, agent_idx):
        algo = agent['algorithm']
        pos = agent['pos']

        # If we have a precomputed path, follow it
        if agent['path']:
            next_pos = agent['path'].pop(0)
            return next_pos

        # Find nearest food
        target = self.nearest_food(pos)
        if not target:
            return self.random_move(agent_idx)

        # Compute path using selected algorithm
        if algo == 'BFS':
            path = bfs(self.grid, pos, target)
        elif algo == 'DFS':
            path = dfs(self.grid, pos, target)
        elif algo == 'A*':
            path = astar(self.grid, pos, target)
        elif algo == 'Greedy':
            path = greedy(self.grid, pos, target)
        else:
            return self.random_move(agent_idx)

        if path and len(path) > 1:
            # path[0] is current position, so next is path[1]
            # Store the rest for future steps
            agent['path'] = path[2:]  # remaining steps after the next one
            return path[1]
        else:
            return self.random_move(agent_idx)

    def step(self):
        """Execute one turn for all agents"""
        for i, agent in enumerate(self.agents):
            next_pos = self.get_next_move(agent, i)
            if next_pos and self.is_valid_move(next_pos, i):
                agent['pos'] = next_pos
                agent['steps'] += 1

                # Check if agent landed on food
                if agent['pos'] in self.foods:
                    self.foods.remove(agent['pos'])
                    agent['food_collected'] += 1
                    self.spawn_random_food(1)  # keep food count constant

        self.turn += 1
        return self.get_state()

    def get_state(self):
        return {
            'turn': self.turn,
            'agents': [{'pos': a['pos'], 'food': a['food_collected']} for a in self.agents],
            'foods': self.foods
        }