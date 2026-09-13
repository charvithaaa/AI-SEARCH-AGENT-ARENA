# arena_manager.py

import asyncio
import threading
import time

from simulation import AgentArena


class ArenaManager:
    def __init__(self):
        self.arena = None
        self.running = False
        self.thread = None

        self.loop = None
        self.clients = set()

    def create_arena(
        self,
        algorithm_1="BFS",
        algorithm_2="A*",
        width=10,
        height=10,
        food_count=5,
    ):
        self.stop()

        self.arena = AgentArena(width, height)

        self.arena.add_agent(
            (0, 0),
            algorithm_1,
        )

        self.arena.add_agent(
            (width - 1, height - 1),
            algorithm_2,
        )

        self.arena.spawn_random_food(food_count)

        return self.arena

    def start(self):
        if self.arena is None:
            raise ValueError("No arena has been created.")

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

        self.thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        while (
            self.running
            and self.arena is not None
            and self.arena.turn < 200
            and len(self.arena.foods) > 0
        ):
            time.sleep(0.5)

            if not self.running or self.arena is None:
                break

            state = self.arena.step()

            self._broadcast(
                {
                    "type": "state",
                    "data": state,
                }
            )

        self.running = False

        if self.arena is not None:
            self._broadcast(
                {
                    "type": "game_over",
                    "data": self._get_winner(),
                }
            )

    def _get_winner(self):
        if not self.arena or len(self.arena.agents) < 2:
            return {
                "winner": None,
                "scores": {
                    "agent1": 0,
                    "agent2": 0,
                },
            }

        agent_1 = self.arena.agents[0]
        agent_2 = self.arena.agents[1]

        if agent_1["food_collected"] > agent_2["food_collected"]:
            winner = "agent1"
        elif agent_2["food_collected"] > agent_1["food_collected"]:
            winner = "agent2"
        else:
            winner = "draw"

        return {
            "winner": winner,
            "scores": {
                "agent1": agent_1["food_collected"],
                "agent2": agent_2["food_collected"],
            },
        }

    def get_state(self):
        if self.arena is None:
            return None

        return self.arena.get_state()

    def add_client(self, websocket):
        self.clients.add(websocket)

    def remove_client(self, websocket):
        self.clients.discard(websocket)

    def _broadcast(self, message):
        if not self.loop:
            return

        for websocket in list(self.clients):
            try:
                future = asyncio.run_coroutine_threadsafe(
                    websocket.send_json(message),
                    self.loop,
                )

                future.add_done_callback(
                    self._handle_broadcast_result
                )

            except Exception:
                self.clients.discard(websocket)

    def _handle_broadcast_result(self, future):
        try:
            future.result()
        except Exception:
            # Remove disconnected clients safely.
            pass


arena_manager = ArenaManager()