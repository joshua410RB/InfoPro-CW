import socket
import threading
try: 
    import queue
except ImportError:
    import Queue as queue
from random import randint
import time
import logging
import subprocess
import pygame
import random

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

# HOST = '13.212.4.31'  # The server's hostname or IP address
HOST = '127.0.0.1'
PORT = 8000        # The port used by the server

speed_data = queue.Queue()
movement_data = [0]

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

car_width = 73
car_height = 73

display_width = 800
display_height = 600

def things(gameDisplay, thingx, thingy, thingw, thingh, color):
    pygame.draw.rect(gameDisplay, color, [thingx, thingy, thingw, thingh])

def car(gameDisplay, carImg, x,y):
    gameDisplay.blit(carImg,(x,y))

def bomb(gameDisplay, bombImg, x,y):
    gameDisplay.blit(bombImg,(x,y))

def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

def message_display(gameDisplay, text, clock, carImg):
    largeText = pygame.font.Font('freesansbold.ttf',115)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = ((display_width/2),(display_height/2))
    gameDisplay.blit(TextSurf, TextRect)

    pygame.display.update()

    time.sleep(2)

    game_loop(gameDisplay, clock, carImg)
    
def crash(gameDisplay,clock, carImg):
    message_display(gameDisplay, 'You Crashed', clock, carImg)
    
def game_loop(gameDisplay, clock, carImg):
    x = (display_width * 0.45)
    y = (display_height * 0.8)

    x_change = 0

    bomb_xy = []

    thing_startx = random.randrange(0, display_width)
    thing_starty = -600
    thing_speed = 7
    thing_width = 100
    thing_height = 100

    gameExit = False

    while not gameExit:

        #for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         pygame.quit()
        #         quit()

        if event.type == pygame.KEYDOWN:
        #         if event.key == pygame.K_LEFT:
        #             x_change = -5
        #         if event.key == pygame.K_RIGHT:
        #             x_change = 5
	    if event.key == pygame.K_SPACE:
	        if len(bomb_xy) <2:
		    bomb_x = x + car_width/2
		    bomb_y = y - car_height/4
		    bomb_xy.append([bomb_x,bomb_y])
        #     if event.type == pygame.KEYUP:
        #         if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
        #             x_change = 0

        # x += x_change
        x = movement_data[-1] 
        logging.debug(x)
        gameDisplay.fill(white)

        # things(thingx, thingy, thingw, thingh, color)
        things(gameDisplay, thing_startx, thing_starty, thing_width, thing_height, black)
        thing_starty += thing_speed
        car(gameDisplay, carImg,x,y)

        if x > display_width - car_width or x < 0:
            crash(gameDisplay, clock, carImg)

        if thing_starty > display_height:
            thing_starty = 0 - thing_height
            thing_startx = random.randrange(0,display_width)

        ####
        if y < thing_starty+thing_height:
            print('y crossover')

            if x > thing_startx and x < thing_startx + thing_width or x+car_width > thing_startx and x + car_width < thing_startx+thing_width:
                print('x crossover')
                crash(gameDisplay, clock, carImg)
        ####
	#bomb
	if len(bomb_xy) != 0:
	    for i, a_xy in enumerate(bomb_xy):
		a_xy[1] -= 10
		bomb_xy[i][1] = a_xy[1]
		if a_xy[1] <= 0:
		    try:
			bomb_xy.remove(a_xy)
		    except:
			pass

	if len(bomb_xy) != 0:
	    for a_x, a_y in bomb_xy:
		drawObject(bomb, a_x, a_y)


        pygame.display.update()
        clock.tick(60)

def game_start():

    pygame.init()

    gameDisplay = pygame.display.set_mode((display_width,display_height))
    pygame.display.set_caption('A bit Racey')
    clock = pygame.time.Clock()

    carImg = pygame.image.load('racecar.png')
    bombImg = pygame.image.load('bomb.png')

    game_loop(gameDisplay, clock, carImg)
    pygame.quit()
    quit()



def generate_random():
    logging.debug("Starting Generation")
    index = 0
    while True:
        speed_data.append(randint(0,10))
        time.sleep(0.1)
        # if (index == 1000):
        #     break
        index += 1
    logging.debug("Exiting Generation")


def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def receive_val(cmd):
    logging.debug("Starting FPGA UART")
    inputCmd = "nios2-terminal.exe <<< {}".format(cmd)
 
    process = subprocess.Popen(inputCmd, shell=True, executable='/bin/bash' , stdout=subprocess.PIPE)
    index = 0
    while True:
        output = process.stdout.readline()
        # if process.poll() is not None and output == b'':
        #     break
        output = output.decode("utf-8")
        tmp = output.split()
        try:
            
            if (len(tmp[-1]) == 8):
                out = twos_comp(int(tmp[-1],16), 32)
                absolute_out = -1 * int(out)
                speed_data.put(absolute_out)
                move = absolute_out / 300 * 800
                # print(move)
                movement_data.append(move)
                # print(tmp[-1])
                # print(speed_data)
        except:
            pass  
        # if (index == 999):
        #     break    
        index += 1
    
    logging.debug("Closing UART")

def start_client():
    logging.debug("Starting Client")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        index = 0
        while True:
            try:
                item = speed_data.get()
                # logging.debug(item)
                sent = s.send(item.to_bytes(4,"big"))
            except IndexError:
                logging.debug("Waiting")
                time.sleep(0.01)
                # sent = s.send(speed_data[index].to_bytes(4,"big"))
                
            # data = s.recv(1024)
            # print('Received', int.from_bytes(data, "big"))
            index += 1
            # if (index == 1000):
            #     break
    logging.debug("Exiting Client")


def main():
    x = threading.Thread(target=receive_val, args={'o'})
    # x = threading.Thread(target=generate_random)
    # receive_val("o")
    y = threading.Thread(target=start_client)
    x.start()
    y.start()
    game_start()
    x.join()
    y.join()

if __name__ == '__main__':
    main()
