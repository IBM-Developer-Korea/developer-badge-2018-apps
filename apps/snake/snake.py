### Author: EMF Badge team
### Description: Snake!
### Category: Games
### License: MIT
### Appname: Snake!
### Built-in: yes
### Ported by Sebastius

import ugfx
import time
import urandom
import math
import util

ugfx.init()

dir_y=1;
dir_x=0;
orient=270

def head(pressed, x, y, o):
    global dir_x
    global dir_y
    global orient
    if(pressed):
        dir_x = x
        dir_y = y
        orient = o

def one_round():
    global dir_x
    global dir_y
    global orient
    grid_size = 8;
    body_colour = ugfx.RED
    back_colour = ugfx.BLACK
    food_colour = ugfx.YELLOW
    wall_colour = ugfx.BLUE
    score = 0;
    edge_x = math.floor(ugfx.width()/grid_size)-2;
    edge_y = math.floor(ugfx.height()/grid_size)-2;

    def disp_square(x,y,colour):
        ugfx.area((x+1)*grid_size, (y+1)*grid_size, grid_size, grid_size, colour)

    def disp_body_straight(x,y,rotation,colour):
        if (rotation == 0):
            ugfx.area((x+1)*grid_size+1, (y+1)*grid_size+1, grid_size-2, grid_size, colour)
        elif (rotation == 90):
            ugfx.area((x+1)*grid_size+1, (y+1)*grid_size+1, grid_size, grid_size-2, colour)
        elif (rotation == 180):
            ugfx.area((x+1)*grid_size+1, (y+1)*grid_size-1, grid_size-2, grid_size, colour)
        else:
            ugfx.area((x+1)*grid_size-1, (y+1)*grid_size+1, grid_size, grid_size-2, colour)

    def disp_eaten_food(x,y,colour):
        ugfx.area((x+1)*grid_size, (y+1)*grid_size, grid_size, grid_size, colour)

    def randn_square():
        return  [urandom.getrandbits(16)%edge_x, urandom.getrandbits(16)%edge_y]

    body_x = [12,13,14,15,16]
    body_y = [2,2,2,2,2]

    ugfx.clear(back_colour)
    ugfx.area(0,0,grid_size*(edge_x+1),grid_size,wall_colour)
    ugfx.area(0,0,grid_size,grid_size*(edge_y+1),wall_colour)
    ugfx.area(grid_size*(edge_x+1),0,grid_size,grid_size*(edge_y+1),wall_colour)
    ugfx.area(0,grid_size*(edge_y+1),grid_size*(edge_x+2),grid_size,wall_colour)

    keepgoing = 1;

    food = [20,20]
    disp_square(food[0],food[1],food_colour)

    dir_x = 1
    dir_y = 0
    orient = 270

	#for i in range(0,len(body_x)):
	#   disp_body_straight(body_x[i],body_y[i],orient,body_colour)

    while keepgoing:
        body_x.append(body_x[-1]+dir_x)
        body_y.append(body_y[-1]+dir_y)

        for i in range(0,len(body_x)-1):
            if (body_x[i] == body_x[-1]) and (body_y[i] == body_y[-1]):
                keepgoing = 0

        if not((body_x[-1] == food[0]) and (body_y[-1] == food[1])):
            x_del = body_x.pop(0)
            y_del = body_y.pop(0)
            disp_eaten_food(x_del,y_del,back_colour)
        else:
            disp_eaten_food(food[0],food[1],body_colour)
            food = randn_square()
            disp_square(food[0],food[1],food_colour)
            score = score + 1

        disp_body_straight(body_x[-1],body_y[-1],orient,body_colour)


        if ((body_x[-1] >= edge_x) or (body_x[-1] < 0) or (body_y[-1] >= edge_y) or (body_y[-1] < 0)):
            break

        time.sleep_ms(100)
    return score

ugfx.input_init()
ugfx.input_attach(ugfx.JOY_UP, lambda pressed: head(pressed, 0, -1, 0))
ugfx.input_attach(ugfx.JOY_DOWN, lambda pressed: head(pressed, 0, 1, 180))
ugfx.input_attach(ugfx.JOY_LEFT, lambda pressed: head(pressed, -1, 0, 90))
ugfx.input_attach(ugfx.JOY_RIGHT, lambda pressed: head(pressed, 1, 0, 270))

next_game = False

def cb_next(pressed):
    global next_game
    if pressed:
        next_game = True


ugfx.input_attach(ugfx.BTN_A, cb_next)
ugfx.input_attach(ugfx.BTN_B, util.reboot)

playing = 1
while playing:
    score = one_round()
    ugfx.area(0,0,ugfx.width(),ugfx.height(),0)
    ugfx.text(30, 30, "GAME OVER Score: %d" % (score), 0xFFFF)
    ugfx.text(30, 60, "Press A to play again", 0xFFFF)
    ugfx.text(30, 90, "Press MENU to quit" , 0xFFFF)

    next_game = False
    while not next_game:
        time.sleep_ms(100)
