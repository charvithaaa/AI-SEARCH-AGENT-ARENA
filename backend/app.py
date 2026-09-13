# app.py
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from simulation import AgentArena
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

arena = None
game_thread = None
running = False

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('start_game')
def handle_start(data):
    global arena, game_thread, running
    algo1 = data.get('algo1', 'BFS')
    algo2 = data.get('algo2', 'BFS')

    arena = AgentArena(10, 10)
    arena.add_agent((0, 0), algo1)
    arena.add_agent((9, 9), algo2)
    arena.spawn_random_food(5)

    running = True

    def game_loop():
        while running and arena.turn < 200:  # max 200 turns
            time.sleep(0.5)  # half second per turn
            state = arena.step()
            socketio.emit('game_update', state)
        # Game over
        winner = 'agent1' if arena.agents[0]['food_collected'] > arena.agents[1]['food_collected'] else 'agent2'
        socketio.emit('game_over', {'winner': winner})

    game_thread = threading.Thread(target=game_loop)
    game_thread.daemon = True
    game_thread.start()

@socketio.on('stop_game')
def handle_stop():
    global running
    running = False

@socketio.on('reset')
def handle_reset():
    global arena, running
    running = False
    arena = None

@socketio.on('add_food')
def handle_add_food(data):
    if arena:
        arena.add_food((data['x'], data['y']))
        socketio.emit('game_update', arena.get_state())

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)