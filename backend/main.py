import asyncio

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from arena_manager import arena_manager


app = FastAPI(
    title="NAVIGENT API",
    description="AI Navigation & Search Laboratory",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ArenaConfig(BaseModel):
    algorithm_1: str = "BFS"
    algorithm_2: str = "A*"
    width: int = 10
    height: int = 10
    food_count: int = 5


@app.on_event("startup")
async def startup_event():
    arena_manager.loop = asyncio.get_running_loop()


@app.get("/")
def root():
    return {
        "name": "NAVIGENT",
        "message": "AI Navigation & Search Laboratory API",
        "status": "online",
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/api/algorithms")
def get_algorithms():
    return {
        "algorithms": [
            {
                "id": "BFS",
                "name": "Breadth-First Search",
                "description": (
                    "Explores nodes level by level and "
                    "finds the shortest path on an unweighted grid."
                ),
            },
            {
                "id": "DFS",
                "name": "Depth-First Search",
                "description": (
                    "Explores deeply before backtracking."
                ),
            },
            {
                "id": "A*",
                "name": "A* Search",
                "description": (
                    "Uses path cost and a heuristic "
                    "to efficiently find a path."
                ),
            },
            {
                "id": "Greedy",
                "name": "Greedy Best-First Search",
                "description": (
                    "Uses a heuristic to move toward the target."
                ),
            },
        ]
    }


@app.post("/api/arena/create")
def create_arena(config: ArenaConfig):
    try:
        arena = arena_manager.create_arena(
            algorithm_1=config.algorithm_1,
            algorithm_2=config.algorithm_2,
            width=config.width,
            height=config.height,
            food_count=config.food_count,
        )

        return {
            "message": "Arena created successfully",
            "state": arena.get_state(),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@app.post("/api/arena/start")
def start_arena():
    try:
        arena_manager.start()

        return {
            "message": "Arena started",
            "state": arena_manager.get_state(),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@app.post("/api/arena/stop")
def stop_arena():
    arena_manager.stop()

    return {
        "message": "Arena stopped",
        "state": arena_manager.get_state(),
    }


@app.get("/api/arena/state")
def get_arena_state():
    state = arena_manager.get_state()

    if state is None:
        raise HTTPException(
            status_code=404,
            detail="No arena exists.",
        )

    return state


@app.websocket("/ws/arena")
async def arena_websocket(websocket: WebSocket):
    await websocket.accept()

    arena_manager.add_client(websocket)

    try:
        state = arena_manager.get_state()

        if state:
            await websocket.send_json({
                "type": "state",
                "data": state,
            })

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        arena_manager.remove_client(websocket)