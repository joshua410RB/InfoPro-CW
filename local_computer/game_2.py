import pygame
import time
import random
import queue

class Game():
    def __init__(self, x_data, y_data, display_width = 800, display_height = 600):
        self.display_width = display_width
        self.display_height = display_height 
        self.car_width = 73
        self.car_height = 73    
        self.black = (0,0,0)
        self.white = (255,255,255)
        self.grey = (128,128,128)
        self.red = (255,0,0)
        pygame.init()
        # Create Screen Display
        self.screen = pygame.display.set_mode((self.display_width,self.display_height))
        pygame.display.set_caption('Multiplayer Racing Game')
        self.icon = pygame.image.load('img/checkered-flag.png') #  icon from: Flaticon.com
        pygame.display.set_icon(self.icon)
        self.clock = pygame.time.Clock()
        # Set game objects
        self.carImg = pygame.image.load('img/race_car.png')
        self.obstacleImg = pygame.image.load('img/normal_car.png')
        self.bombImg = pygame.image.load('img/bomb.png')
        self.x_data = x_data
        self.y_data = y_data
        self.gameStart = False
        self.gameExit = False

    def obstacles(self, thingx, thingy, thingw, thingh, color):
        self.screen.blit(self.obstacleImg,(thingx,thingy))
        # pygame.draw.rect(self.screen, color, [thingx, thingy, thingw, thingh])

    def item(self, thingx, thingy, thingw, thingh, color):
        self.screen.blit(self.bombImg,(thingx,thingy))

    def car(self, x,y):
        self.screen.blit(self.carImg,(x,y))

    def text_objects(self, text, font):
        textSurface = font.render(text, True, self.black)
        return textSurface, textSurface.get_rect()

    def message_display(self, text):
        largeText = pygame.font.Font('freesansbold.ttf',115)
        TextSurf, TextRect = self.text_objects(text, largeText)
        TextRect.center = ((self.display_width/2),(self.display_height/2))
        self.screen.blit(TextSurf, TextRect)

        pygame.display.update()

        time.sleep(2)
        self.game_loop()
        
    def start_screen(self):
        self.screen.fill(self.white)
        while not self.gameStart:            
            text_font = pygame.font.Font('Roboto-Regular.ttf',80)
            start_text, start_rect = self.text_objects("Racing Game", text_font)
            start_rect.center = ((self.display_width/2),(self.display_height/2-50))
    
            self.screen.blit(start_text, start_rect)

            mouse = pygame.mouse.get_pos() 
            if self.display_width/2-50 <= mouse[0] <= self.display_width/2+50 and self.display_height/2+20 <= mouse[1] <= self.display_height/2+60:
                pygame.draw.rect(self.screen, self.black, [self.display_width/2-50, self.display_height/2+20, 100, 40])
            else:
                pygame.draw.rect(self.screen, self.grey, [self.display_width/2-50, self.display_height/2+20, 100, 40])
            button_text_font = pygame.font.Font('Roboto-Regular.ttf',15)
            startbutton_text, startbutton_rect = self.text_objects("Start Game", button_text_font)
            startbutton_rect.center = ((self.display_width/2),(self.display_height/2+40))
            self.screen.blit(startbutton_text, startbutton_rect)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    if self.display_width/2-50 <= mouse[0] <= self.display_width/2+50 and self.display_height/2+20 <= mouse[1] <= self.display_height/2+60: 
                        self.gameStart =True 
        self.race_screen()


    def crash(self):
        self.message_display('You Crashed')

    def game_loop(self):
        self.start_screen()

    def race_screen(self):
        start_time = pygame.time.get_ticks()
        bomb_xy = []        

        x = (self.display_width * 0.45)
        y = (self.display_height * 0.8)

        x_change = 0

        obstacle_startx = random.randrange(0, self.display_width)
        item_startx = random.randrange(0, self.display_width)
        obstacle_starty = item_starty = -self.display_height
        obstacle_speed = 7
        obstacle_width = obstacle_height =100
        item_width = item_height = 50
        text_font = pygame.font.Font('Roboto-Regular.ttf',15)

        while (self.gameStart and not self.gameExit):
            obstacle_speed = self.y_data.get()//30
            currspeed_text, currspeed_rect = self.text_objects("Current Speed: "+str(obstacle_speed), text_font)
            currspeed_rect.center = ((self.display_width-700),(self.display_height-500))
            time_text, time_rect = self.text_objects("Time Elapsed: "+str(int(pygame.time.get_ticks() - start_time)//1000)+"s", text_font)
            time_rect.center = ((self.display_width-700),(self.display_height-450))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                # if event.type == pygame.KEYDOWN:
                #     if event.key == pygame.K_LEFT:
                #         x_change = -5
                #     if event.key == pygame.K_RIGHT:
                #         x_change = 5
                #     if event.key == pygame.K_UP:
                #         obstacle_speed += 3                   
                #     if event.key == pygame.K_DOWN:
                #         obstacle_speed -= 3
            #bomb
            # if event.type == pygame.K_SPACE:
            #     if len(bomb_xy) <2:
            #         bomb_x = x + car_width/2
            #         bomb_y = y - car_height/4
            #         bomb_xy.append([bomb_x,bomb_y])

            #     if event.type == pygame.KEYUP:
            #         if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            #             x_change = 0

            # x += x_change
            x = self.x_data.get()
            print("Test")
            self.screen.fill(self.grey)
            # obstacles(thingx, thingy, thingw, thingh, color)
            self.obstacles(obstacle_startx, obstacle_starty, obstacle_width, obstacle_height, self.black)
            self.item(item_startx, item_starty, item_width, item_height, self.black)
            obstacle_starty += obstacle_speed
            item_starty += obstacle_speed

            self.car(x,y)
            self.screen.blit(currspeed_text, currspeed_rect)
            self.screen.blit(time_text, time_rect)

            if x > self.display_width - self.car_width or x < 0:
                self.crash()

            if obstacle_starty > self.display_height:
                obstacle_starty = 0 - obstacle_height
                obstacle_startx = random.randrange(0,self.display_width)

            ####
            if y < obstacle_starty+obstacle_height:
                print('y crossover')

                if x > obstacle_startx and x < obstacle_startx + obstacle_width or x+self.car_width > obstacle_startx and x + self.car_width < obstacle_startx+obstacle_width:
                    print('x crossover')
                    self.crash()
            ####

        # #bomb
        # if len(bomb_xy) != 0:
        #     for i, a_xy in enumerate(bomb_xy):
        #         a_xy[1] -= 10
        #         bomb_xy[i][1] = a_xy[1]

        #     if a_xy[1] <= 0:
        #         try:
        #             bomb_xy.remove(a_xy)
        #         except:
        #             pass
        # if len(bomb_xy) != 0:
        #     for a_x, a_y in bomb_xy:
        #         drawObject(bomb, a_x, a_y)

            pygame.display.update()
            self.clock.tick(60)

    def game_start(self):
        self.game_loop()
        pygame.quit()
        quit()


if __name__ == "__main__":
    x_data = queue.Queue()
    y_data = queue.Queue()
    new_game = Game(x_data, y_data)
    new_game.game_start()
