import pygame
import time
import random
import queue

class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.image = pygame.image.load('img/race_car.png')
        # self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
    def update(self, pos_x, pos_y):
        self.rect.center = [pos_x, pos_y]
        
    def collide(self, obstacle_group):
        hit = pygame.sprite.spritecollide(self, obstacle_group, True)
        if len(hit) >0:
            return True
        else:
            return False
    

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.image = pygame.image.load('img/normal_car.png')
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
    def update(self, pos_x, pos_y):
        self.rect.center = [pos_x, pos_y]

class Item(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.image = pygame.image.load('img/bomb.png')
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
    def update(self, pos_x, pos_y):
        self.rect.center = [pos_x, pos_y]

class Game():
    def __init__(self, x_data, y_data, ready_flag, start_flag, leaderboard_object, end_flag, display_width = 800, display_height = 600):
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
        self.bombImg = pygame.image.load('img/bomb.png')
        self.x_data = x_data
        self.y_data = y_data
        self.ready_flag = ready_flag
        self.start_flag = start_flag
        self.end_flag = end_flag
        self.gameStart = False
        self.gameExit = False
    
    def item(self, thingx, thingy, thingw, thingh, color):
        self.screen.blit(self.bombImg,(thingx,thingy))

    def text_objects(self, text, font):
        textSurface = font.render(text, True, self.black)
        return textSurface, textSurface.get_rect()

    def message_display(self, text):
        largeText = pygame.font.Font('freesansbold.ttf',115)
        TextSurf, TextRect = self.text_objects(text, largeText)
        TextRect.center = ((self.display_width/2),(self.display_height/2))
        self.screen.blit(TextSurf, TextRect)

        # pygame.display.update()

        time.sleep(2)
        # self.game_loop()    
     
    def crash(self):
        self.message_display('You Crashed')

    def game_start(self):
        self.start_screen()
        pygame.quit()
        quit()        

    def start_screen(self):
        self.screen.fill(self.white)
        self.ready_flag.clear()
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
        self.multiplayer_screen()

    def multiplayer_screen(self):
        self.screen.fill(self.white)
        while not self.ready_flag.is_set():            
            text_font = pygame.font.Font('Roboto-Regular.ttf',80)
            start_text, start_rect = self.text_objects("Multiplayer Mode", text_font)
            start_rect.center = ((self.display_width/2),(self.display_height/2-50))
    
            self.screen.blit(start_text, start_rect)

            mouse = pygame.mouse.get_pos() 
            if self.display_width/2-50 <= mouse[0] <= self.display_width/2+50 and self.display_height/2+20 <= mouse[1] <= self.display_height/2+60:
                pygame.draw.rect(self.screen, self.black, [self.display_width/2-50, self.display_height/2+20, 100, 40])
            else:
                pygame.draw.rect(self.screen, self.grey, [self.display_width/2-50, self.display_height/2+20, 100, 40])

            button_text_font = pygame.font.Font('Roboto-Regular.ttf',15)
            startbutton_text, startbutton_rect = self.text_objects("Ready", button_text_font)
            startbutton_rect.center = ((self.display_width/2),(self.display_height/2+40))
            self.screen.blit(startbutton_text, startbutton_rect)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    if self.display_width/2-50 <= mouse[0] <= self.display_width/2+50 and self.display_height/2+20 <= mouse[1] <= self.display_height/2+60: 
                        self.ready_flag.set()
        print("Out of Ready Loop")

        self.screen.fill(self.white)
        while not self.start_flag.is_set():
            text_font = pygame.font.Font('Roboto-Regular.ttf',50)
            waiting_text, waiting_rect = self.text_objects("Game is starting soon...", text_font)
            waiting_rect.center = ((self.display_width/2),(self.display_height/2-100))
            self.screen.blit(waiting_text, waiting_rect)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

        self.race_screen()

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
        
        player_group  = pygame.sprite.Group()
        player = Player(x, y)
        player_group.add(player)

        obstacle_group  = pygame.sprite.Group()
        obstacle = Obstacle(obstacle_startx, obstacle_starty)
        obstacle_group.add(obstacle)

        while (self.gameStart):
            obstacle_speed = self.y_data.get()
            if int(pygame.time.get_ticks() - start_time)//1000 > 15:
                break
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
            # bomb
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
            self.x_data.task_done()
            self.screen.fill(self.grey)
            self.item(item_startx, item_starty, item_width, item_height, self.black)
            obstacle_starty += obstacle_speed
            item_starty += obstacle_speed

            player_group.draw(self.screen)
            player_group.update(x,y)
            check = player.collide(obstacle_group)
            print(check)
            if check:
                self.crash()

            obstacle_group.draw(self.screen)
            obstacle_group.update(obstacle_startx,obstacle_starty)

            # item_group.draw(self.screen)

            self.screen.blit(currspeed_text, currspeed_rect)
            self.screen.blit(time_text, time_rect)

            if x > self.display_width - self.car_width or x < 0:
                self.crash()
                obstacle_starty = 0

            if obstacle_starty > self.display_height:
                obstacle_starty = 0 - obstacle_height
                obstacle_startx = random.randrange(0,self.display_width)


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
            self.clock.tick(120)

        self.end_flag.set()
        self.end_screen()
     
    def end_screen(self):
        self.screen.fill(self.white)
        while not self.gameExit:
            text_font = pygame.font.Font('Roboto-Regular.ttf',80)
            start_text, start_rect = self.text_objects("Awaiting Results", text_font)
            start_rect.center = ((self.display_width/2),(self.display_height/2-50))
    
            self.screen.blit(start_text, start_rect)

            mouse = pygame.mouse.get_pos() 
            if self.display_width/2-50 <= mouse[0] <= self.display_width/2+50 and self.display_height/2+20 <= mouse[1] <= self.display_height/2+60:
                pygame.draw.rect(self.screen, self.black, [self.display_width/2-50, self.display_height/2+20, 100, 40])
            else:
                pygame.draw.rect(self.screen, self.grey, [self.display_width/2-50, self.display_height/2+20, 100, 40])

            button_text_font = pygame.font.Font('Roboto-Regular.ttf',15)
            startbutton_text, startbutton_rect = self.text_objects("Exit", button_text_font)
            startbutton_rect.center = ((self.display_width/2),(self.display_height/2+40))
            self.screen.blit(startbutton_text, startbutton_rect)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    if self.display_width/2-50 <= mouse[0] <= self.display_width/2+50 and self.display_height/2+20 <= mouse[1] <= self.display_height/2+60: 
                        self.gameExit = True
        self.start_screen()


if __name__ == "__main__":
    x_data = queue.Queue()
    y_data = queue.Queue()
    new_game = Game(x_data, y_data)
    new_game.game_start()
