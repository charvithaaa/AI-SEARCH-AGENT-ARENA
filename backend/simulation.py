# simulation.py

import random
from algorithms import bfs, dfs, astar, greedy


class AgentArena:
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.grid = [[0] * width for _ in range(height)]
        self.agents = []
        self.foods = []
        self.initial_food_count = 0
        self.turn = 0

    def add_agent(self, start_pos, algorithm="BFS"):
        agent = {
            "pos": start_pos,
            "algorithm": algorithm,
            "food_collected": 0,
            "steps": 0,
            "path": [],
        }

        self.agents.append(agent)
        return agent

    def add_food(self, pos):
        if pos not in self.foods:
            self.foods.append(pos)
            self.initial_food_count = len(self.foods)

    def spawn_random_food(self, count=1):
        for _ in range(count):
            attempts = 0

            while attempts < 100:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                pos = (x, y)

                if (
                    pos not in self.foods
                    and all(agent["pos"] != pos for agent in self.agents)
                ):
                    self.foods.append(pos)
                    break

                attempts += 1

        self.initial_food_count = len(self.foods)

    def nearest_food(self, agent_pos):
        if not self.foods:
            return None

        return min(
            self.foods,
            key=lambda food: abs(food[0] - agent_pos[0])
            + abs(food[1] - agent_pos[1]),
        )

    def is_valid_move(self, pos, agent_idx):
        x, y = pos

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False

        if self.grid[y][x] == 1:
            return False

        return True

    def random_move(self, agent_idx):
        agent = self.agents[agent_idx]
        x, y = agent["pos"]

        directions = [
            (0, 1),
            (1, 0),
            (0, -1),
            (-1, 0),
        ]

        random.shuffle(directions)

        for dx, dy in directions:
            new_pos = (x + dx, y + dy)

            if self.is_valid_move(new_pos, agent_idx):
                return new_pos

        return agent["pos"]

    def get_next_move(self, agent, agent_idx):
        algorithm = agent["algorithm"]
        current_pos = agent["pos"]

        if agent["path"]:
            return agent["path"].pop(0)

        target = self.nearest_food(current_pos)

        if target is None:
            return current_pos

        if algorithm == "BFS":
            path = bfs(self.grid, current_pos, target)
        elif algorithm == "DFS":
            path = dfs(self.grid, current_pos, target)
        elif algorithm == "A*":
            path = astar(self.grid, current_pos, target)
        elif algorithm == "Greedy":
            path = greedy(self.grid, current_pos, target)
        else:
            return self.random_move(agent_idx)

        if path and len(path) > 1:
            agent["path"] = path[2:]
            return path[1]

        return current_pos

    def step(self):
        """Execute one turn for all agents."""

        for index, agent in enumerate(self.agents):
            next_pos = self.get_next_move(agent, index)

            if next_pos and self.is_valid_move(next_pos, index):
                agent["pos"] = next_pos
                agent["steps"] += 1

                if agent["pos"] in self.foods:
                    self.foods.remove(agent["pos"])
                    agent["food_collected"] += 1

        self.turn += 1
        return self.get_state()

    def get_state(self):
        return {
            "turn": self.turn,
            "agents": [
                {
                    "position": list(agent["pos"]),
                    "algorithm": agent["algorithm"],
                    "food_collected": agent["food_collected"],
                    "steps": agent["steps"],
                    "path": [
                        list(position)
                        for position in agent["path"]
                    ],
                }
                for agent in self.agents
            ],
            "foods": [
                list(food)
                for food in self.foods
            ],
            "initial_food_count": self.initial_food_count,
        }