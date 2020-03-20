# small network game that has differnt blobs
# moving around the screen

import contextlib

with contextlib.redirect_stdout(None):
    import pygame
from pygame.locals import *
from client import Network
import random
import os

import PAdLib.occluder as occluder
import PAdLib.shadow as shadow


pygame.font.init()

# Constants
PLAYER_RADIUS = 10
START_VEL = 3

W, H = 800, 600

COLORS = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (128, 255, 0), (0, 255, 0), (0, 255, 128), (0, 255, 255),
          (0, 128, 255), (0, 0, 255), (0, 0, 255), (128, 0, 255), (255, 0, 255), (255, 0, 128), (128, 128, 128),
          (0, 0, 0)]

# Dynamic Variables
players = {}


NAME_FONT = pygame.font.SysFont("comicsans", 20)
# FUNCTIONS
def draw_player(players):
    """
    draws each frame
    :return: None
    """
    #WIN.fill((255, 255, 255))  # fill screen white, to clear old frames

    # draw each player in the list
    for player in players:
        p = players[player]

        shad.set_light_position((p["x"], p["y"])) #TODO Draw Plaer() and draw_opponents()

        pygame.draw.circle(WIN, p["color"], (p["x"], p["y"]), PLAYER_RADIUS)
        # render and draw name for each player
        text = NAME_FONT.render(p["name"], 1, (0, 0, 0))
        WIN.blit(text, (p["x"] - text.get_width() / 2, p["y"] - text.get_height() / 2))


def main(name):
    """
    function for running the game,
    includes the main loop of the game
    :param players: a list of dicts represting a player
    :return: None
    """
    global players

    # start by connecting to the network
    server = Network()
    current_id = server.connect(name)
    players = server.send("get")

    # setup the clock, limit to 30fps
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(60)  # 60 fps max
        player = players[current_id]
        vel = START_VEL
        if vel <= 1:
            vel = 1

        # get key presses
        keys = pygame.key.get_pressed()

        data = ""
        # movement based on key presses
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if player["x"] - vel - PLAYER_RADIUS >= 0:
                player["x"] = player["x"] - vel

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if player["x"] + vel + PLAYER_RADIUS <= W:
                player["x"] = player["x"] + vel

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if player["y"] - vel - PLAYER_RADIUS >= 0:
                player["y"] = player["y"] - vel

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if player["y"] + vel + PLAYER_RADIUS <= H:
                player["y"] = player["y"] + vel

        data = "move " + str(player["x"]) + " " + str(player["y"])

        # send data to server and recieve back all players information
        players = server.send(data)

        for event in pygame.event.get():
            # if user hits red x button close window
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                # if user hits a escape key close program
                if event.key == pygame.K_ESCAPE:
                    run = False


        # ======First compute the lighting information======

        #   Returns a greyscale surface of the shadows and the coordinates to draw it at.
        #   False tell it to not consider the occluders' interiors to be shadowed.  True
        #   means that the occluders' interiors are shadowed.  Note that if the light is
        #   within any occluder, everything is always shadowed.
        mask, draw_pos = shad.get_mask_and_position(False)

        #   Falloff (just multiplies the black and white mask by the falloff to make it
        #   look smoother).  Disabling "with_falloff" might make the algorithm more clear.
        mask.blit(surf_falloff, (0, 0), special_flags=BLEND_MULT)

        #   Ambient light
        surf_lighting.fill((50, 50, 50))
        #   Add the contribution from the shadowed light source
        surf_lighting.blit(mask, draw_pos, special_flags=BLEND_MAX)

        # ======Now actually draw the scene======
        #   Draw the background xor clear the screen
        WIN.fill((110, 170, 140))

        # ======Now multiply the lighting information onto the scene======

        #   If you comment this out, you'll see the scene without any lighting.
        #   If you comment out just the special flags part, the lighting surface
        #   will overwrite the scene, and you'll see the lighting information.
        WIN.blit(surf_lighting, (0, 0), special_flags=BLEND_MULT)

        # ======Post processing======

        #   Hack to outline the occluders.  Don't use this yourself.
        for occluder in occluders:
            pygame.draw.lines(WIN, (255, 255, 255), True, occluder.points)

        # redraw window then update the frame
        draw_player(players)
        pygame.display.update()

    server.disconnect()
    pygame.quit()
    quit()


# get users name
while True:
    name = input("Please enter your name: ")
    if 0 < len(name) < 20:
        break
    else:
        print("Error, this name is not allowed (must be between 1 and 19 characters [inclusive])")

# make window start in top left hand corner
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 30)

# setup pygame window
WIN = pygame.display.set_mode([W, H])
pygame.display.set_caption("Networking Test")

#Holds all the lighting information
surf_lighting = pygame.Surface([W, H])

#Our shadowing object
shad = shadow.Shadow()
occluders = [occluder.Occluder([[350,350],[160,150],[400,500]]),occluder.Occluder([[500,200],[450,200],[350,300]])]
shad.set_occluders(occluders)
shad.set_radius(200.0)

#Falloff multiplier
surf_falloff = pygame.image.load("light_falloff100.png")
#surf_falloff = pygame.transform.scale(surf_falloff,[1800,1800])
surf_falloff.convert()



# start game
main(name)