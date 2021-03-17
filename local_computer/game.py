import pygame
import time
import random
import sys

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

car_width = 73
car_height = 73

pygame.init()

display_width = 800
display_height = 600


gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('A bit Racey')
clock = pygame.time.Clock()

carImg = pygame.image.load('racecar.png')
bombImg = pygame.image.load('bomb.png')

def things(thingx, thingy, thingw, thingh, color):
    pygame.draw.rect(gameDisplay, color, [thingx, thingy, thingw, thingh])

def car(x,y):
    gameDisplay.blit(carImg,(x,y))

def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

def message_display(text):
    largeText = pygame.font.Font('freesansbold.ttf',115)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = ((display_width/2),(display_height/2))
    gameDisplay.blit(TextSurf, TextRect)

    pygame.display.update()

    time.sleep(2)

    game_loop()
    
    

def crash():
    message_display('You Crashed')
    
def game_loop(gameDisplay, display_height, display_width):
    bomb_xy = []
    x = (display_width * 0.45)
    y = (display_height * 0.8)

    x_change = 0

    thing_startx = random.randrange(0, display_width)
    thing_starty = -600
    thing_speed = 7
    thing_width = 100
    thing_height = 100

    gameExit = False

    while not gameExit:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -5
                if event.key == pygame.K_RIGHT:
                    x_change = 5
		#bomb
		if event.key == pygame.K_SPACE:
		    if len(bomb_xy) <2:
			bomb_x = x + car_width/2
			bomb_y = y - car_height/4
			bomb_xy.append([bomb_x,bomb_y])

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    x_change = 0

        x += x_change
        gameDisplay.fill(white)

        # things(thingx, thingy, thingw, thingh, color)
        things(thing_startx, thing_starty, thing_width, thing_height, black)
        thing_starty += thing_speed
        car(x,y)

        if x > display_width - car_width or x < 0:
            crash()

        if thing_starty > display_height:
            thing_starty = 0 - thing_height
            thing_startx = random.randrange(0,display_width)

        ####
        if y < thing_starty+thing_height:
            print('y crossover')

            if x > thing_startx and x < thing_startx + thing_width or x+car_width > thing_startx and x + car_width < thing_startx+thing_width:
                print('x crossover')
                crash()
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
    
    game_loop(gameDisplay, display_height, display_width)
    pygame.quit()
    quit()


if __name__ == "__main__":
    game_start()
