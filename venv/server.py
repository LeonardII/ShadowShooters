
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
import socket
from _thread import *
import _pickle as pickle
import time
import random
import math

# setup sockets
S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
S.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Set constants
PORT = 5555

START_RADIUS = 10


W, H = 800, 600

HOST_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(HOST_NAME)

# try to connect to server
try:
    S.bind((SERVER_IP, PORT))
except socket.error as e:
    print(str(e))
    print("[SERVER] Server could not start")
    quit()

S.listen()  # listen for connections

print(f"[SERVER] Server Started with local ip {SERVER_IP}")

# dynamic variables
players = {}
connections = 0
_id = 0
colors = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (128, 255, 0), (0, 255, 0), (0, 255, 128), (0, 255, 255),
          (0, 128, 255), (0, 0, 255), (0, 0, 255), (128, 0, 255), (255, 0, 255), (255, 0, 128), (128, 128, 128),
          (0, 0, 0)]


# FUNCTIONS
def player_collision(players):
    """
    checks for player collision and handles that collision
    :param players: dict
    :return: None
    """

    for x, player1 in players.items():
        for y, player2 in players.items():

            p1 = pygame.Vector2(player1["x"],player1["y"])
            p2 = pygame.Vector2(player2["x"],player2["y"])
            delta = p1 - p2

            if delta.length() < 2*START_RADIUS and delta.length() > 0.01:
                midpoint = p2 + delta/2
                dir = delta.normalize()
                p1 = midpoint + dir * START_RADIUS
                p2 = midpoint - dir * START_RADIUS
                player1["x"] = int(p1.x)
                player1["y"] = int(p1.y)
                player2["x"] = int(p2.x)
                player2["y"] = int(p2.y)


def get_start_location(players):
    """
    picks a start location for a player based on other player
    locations. It wiill ensure it does not spawn inside another player
    :param players: dict
    :return: tuple (x,y)
    """
    while True:
        stop = True
        x = random.randrange(0, W)
        y = random.randrange(0, H)
        for player in players:
            p = players[player]
            dis = math.sqrt((x - p["x"]) ** 2 + (y - p["y"]) ** 2)
            if dis <= START_RADIUS:
                stop = False
                break
        if stop:
            break
    return (x, y)


def threaded_client(conn, _id):
    """
    runs in a new thread for each player connected to the server
    :param con: ip address of connection
    :param _id: int
    :return: None
    """
    global connections, players

    current_id = _id

    # recieve a name from the client
    data = conn.recv(16)
    name = data.decode("utf-8")
    print("[LOG]", name, "connected to the server.")

    # Setup properties for each new player
    color = colors[current_id]
    x, y = get_start_location(players)
    players[current_id] = {"x": x, "y": y, "color": color, "name": name, "direction": 0.0}  # direction in Radians

    # pickle data and send initial info to clients
    conn.send(str.encode(str(current_id)))
    print("send", current_id)

    # server will recieve basic commands from client
    # it will send back all of the other clients info
    '''
    commands start with:
    move
    jump
    get
    id - returns id of client
    '''
    while True:
        try:
            # Recieve data from client
            data = conn.recv(64)

            if not data:
                break

            data = data.decode("utf-8")
            # print("[DATA] Recieved", data, "from client id:", current_id)

            # look for specific commands from recieved data
            if data.split(" ")[0] == "move":
                split_data = data.split(" ")
                x = int(split_data[1])
                y = int(split_data[2])
                direction = float(split_data[3])
                players[current_id]["x"] = x
                players[current_id]["y"] = y
                players[current_id]["direction"] = direction

                player_collision(players)

                send_data = pickle.dumps((players))

            elif data.split(" ")[0] == "id":
                send_data = str.encode(str(current_id))  # if user requests id then send it

            elif data.split(" ")[0] == "jump":
                send_data = pickle.dumps((players))
            else:
                # any other command just send back list of players
                send_data = pickle.dumps((players))

            # send data back to clients
            conn.send(send_data)

        except Exception as e:
            print(e)
            break  # if an exception has been reached disconnect client

        time.sleep(0.001)

    # When user disconnects
    print("[DISCONNECT] Name:", name, ", Client Id:", current_id, "disconnected")

    connections -= 1
    del players[current_id]  # remove client information from players list
    conn.close()  # close connection


# MAINLOOP

print("[GAME] Setting up level")
print("[SERVER] Waiting for connections")

# Keep looping to accept new connections
while True:

    host, addr = S.accept()
    print("[CONNECTION] Connected to:", addr)

    # start game when a client on the server computer connects
    if addr[0] == SERVER_IP:
        print("[STARTED] Game Started")

    # increment connections start new thread then increment ids
    connections += 1
    start_new_thread(threaded_client, (host, _id))
    _id += 1

# when program ends
print("[SERVER] Server offline")