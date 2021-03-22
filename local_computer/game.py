import pygame
import time
import random
try: 
    import queue
except ImportError:
    import Queue as queue


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.image = pygame.image.load('img/race_car.png')
        # self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        self.bombnumber = 0

    def update(self, pos_x, pos_y):
        self.rect.center = [pos_x, pos_y]
        
    def collide(self, obstacle_group):
        hit = pygame.sprite.spritecollide(self, obstacle_group, True)
        if len(hit) >0:
            return True
        else:
            return False

    #JEONGIN
    def item_collect(self, item_group):
        item_hit = pygame.sprite.spritecollide(self, item_group, True)
        print("Item Hit")
        print(item_hit)
        if len(item_hit)>0:
            self.bombnumber +=1
    
    def get_bombcount(self):
        return self.bombnumber

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
    def __init__(self, x_data, y_data, 
                 ready_flag, start_flag, start_queue_flag, final_flag, 
                 leaderboard_object, ready_object, end_flag, 
                 display_width = 800, display_height = 600):
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
        self.start_queue_flag = start_queue_flag
        self.final_flag = final_flag
        self.end_flag = end_flag
        self.gameStart = False
        self.gameExit = False
        self.leaderboard = leaderboard_object
        self.ready = ready_object
        self.text_font = pygame.font.Font('assets/Roboto-Regular.ttf',20)

        self.obstacle_starty = -self.display_height
        self.obstacle_startx = random.randrange(0, self.display_width)
        self.Bg1 = pygame.image.load('img/startscreen.png')
        self.Bg2 = pygame.image.load('img/multiplayer_screen.png')
        self.Bg3 = pygame.image.load('img/ready_screen.png')
        self.Bg4 = pygame.image.load('img/countdown_screen.png')

    def text_objects(self, text, font, color):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()

    def score_display(self, text) :
        TextSurf, TextRect = self.text_objects("Bombcount: " + text, self.text_font, self.black)
        TextRect.center = ((self.display_width/2),(self.display_height*1/5))
        self.screen.blit(TextSurf, TextRect)


    def crash(self, obstacle_group, create_new):
        self.start_queue_flag.clear()        
        largeText = pygame.font.Font('freesansbold.ttf',40)
        TextSurf, TextRect = self.text_objects("You have crashed!", largeText, self.white)
        TextRect.center = ((self.display_width/2),(self.display_height/2))
        self.screen.blit(TextSurf, TextRect)

        # so that it resets and triggers a new obstacle at the top
        if (create_new):
            self.obstacle_starty = -200
            obstacle = Obstacle(self.obstacle_startx, self.obstacle_starty)
            obstacle_group.add(obstacle)
        pygame.display.update()
        time.sleep(2)
        self.start_queue_flag.set()

    def game_start(self):
        self.start_screen()
        pygame.quit()
        quit()        

    def start_screen(self):
        self.ready_flag.clear()
        self.end_flag.clear()
        while not self.gameStart:            
            self.screen.fill(self.white)
            self.screen.blit(self.Bg1,(0,0))
            start_text, start_rect = self.text_objects("Racing Game", self.text_font, self.black)
            start_rect.center = ((self.display_width/2),(self.display_height/2-50))
    
            self.screen.blit(start_text, start_rect)

            mouse = pygame.mouse.get_pos() 
            if self.display_width/2-50 <= mouse[0] <= self.display_width/2+50 and self.display_height/2+20 <= mouse[1] <= self.display_height/2+60:
                pygame.draw.rect(self.screen, self.white, [self.display_width/2-50, self.display_height/2+20, 100, 40])
            else:
                pygame.draw.rect(self.screen, self.grey, [self.display_width/2-50, self.display_height/2+20, 100, 40])

            button_text_font = pygame.font.Font('assets/Roboto-Regular.ttf',15)
            startbutton_text, startbutton_rect = self.text_objects("Start Game", button_text_font, self.black)
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
        # Ready Button Screen
        while not self.ready_flag.is_set():            
            self.screen.blit(self.Bg2, (0,0))
            start_text, start_rect = self.text_objects("Multiplayer Mode", self.text_font, self.black)
            start_rect.center = ((self.display_width/2),(self.display_height/2-50))
            self.screen.blit(start_text, start_rect)
            self.update_readystatus(self.display_width/2, self.display_height/2-100)
            mouse = pygame.mouse.get_pos() 
            if self.display_width/2-50 <= mouse[0] <= self.display_width/2+50 and self.display_height/2+20 <= mouse[1] <= self.display_height/2+60:
                pygame.draw.rect(self.screen, self.white, [self.display_width/2-50, self.display_height/2+20, 100, 40])
            else:
                pygame.draw.rect(self.screen, self.grey, [self.display_width/2-50, self.display_height/2+20, 100, 40])

            button_text_font = pygame.font.Font('assets/Roboto-Regular.ttf',15)
            startbutton_text, startbutton_rect = self.text_objects("Ready", button_text_font, self.black)
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

        # Waiting for Start Screen
        while not self.start_flag.is_set():
            self.screen.fill(self.white)
            self.screen.blit(self.Bg3, (0,0))
            waiting_text, waiting_rect = self.text_objects("Game is starting soon...", self.text_font, self.black)
            waiting_rect.center = ((self.display_width/2),(self.display_height/2-100))
            self.screen.blit(waiting_text, waiting_rect)
            self.update_readystatus(self.display_width/2, self.display_height/2-100)
            # add players ready status

            
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

        self.countdown_screen()

    def countdown_screen(self):
        # Countdown screen
        start_time = pygame.time.get_ticks()
        
        countdown = 5 
        while int(pygame.time.get_ticks() - start_time)//1000 < 6:
            self.screen.blit(self.Bg4, (0,0))
            text = "START!" if (countdown == 0) else str(countdown)
            countdown_text, countdown_rect = self.text_objects(text, self.text_font, self.white)
            countdown_rect.center = ((self.display_width/2),(self.display_height/2))
            self.screen.blit(countdown_text, countdown_rect)
            if int(pygame.time.get_ticks() - start_time)//1000 > (5-countdown):
                countdown -= 1
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit() 
        self.start_queue_flag.set()
        self.race_screen()

    def update_readystatus(self, width_margin, height_margin):
        lb_title, lb_rect = self.text_objects("In Lobby", self.text_font, self.white)
        lb_rect.center = ((self.display_width-width_margin),(self.display_height-height_margin))
        self.screen.blit(lb_title, lb_rect)
        margin = 40 
        for name, status in self.ready.items():
            status_string=""
            if (status == 0):
                status_string = "Not Ready"
            elif (status == 1):
                status_string = "Ready"
            else:
                status_string = "Ended Game"

            lb_text, lb_rect = self.text_objects(str(name)+": "+status_string, self.text_font, self.black)
            lb_rect.center = ((self.display_width-width_margin),(self.display_height-height_margin+margin))
            self.screen.blit(lb_text, lb_rect)
            margin += 40

    def update_leaderboard(self, width_pos, height_pos):
        lb_title, lb_rect = self.text_objects("Leaderboard", self.text_font, self.black)
        lb_rect.center = ((self.display_width*width_pos),(self.display_height*height_pos))
        self.screen.blit(lb_title, lb_rect)
        position = 1
        margin = 40 
        for name, dist in self.leaderboard.items():
            lb_text, lb_rect = self.text_objects(str(position) + ". "+ str(name)+": "+str(dist)+"m", self.text_font, self.black)
            lb_rect.center = ((self.display_width*width_pos),(self.display_height*height_pos+margin))
            self.screen.blit(lb_text, lb_rect)
            margin += 40
            position += 1

    def race_screen(self):
        print("Go into race screen")
        start_time = pygame.time.get_ticks()

        # Create Player Sprite
        x = (self.display_width * 0.45)
        y = (self.display_height * 0.8)
        player_group  = pygame.sprite.Group()
        player = Player(x, y)
        player_group.add(player)

        # Create Obstacle Sprite
        obstacle_speed = 7
        obstacle_width = obstacle_height =100
        obstacle_group  = pygame.sprite.Group()
        obstacle = Obstacle(self.obstacle_startx, self.obstacle_starty)
        obstacle_group.add(obstacle)      

        # Create Item Sprite
        item_startx = random.randrange(0, self.display_width)
        item_starty = -self.display_height
        item_group  = pygame.sprite.Group()        
        # if (item_startx >= self.obstacle_startx -100) and (item_startx <= self.obstacle_startx + 100):
        item = Item(item_startx, item_starty)
        item_group.add(item)

        while (self.gameStart):         
            obstacle_speed = self.y_data.get()
            item_speed = self.y_data.get() - 2

            if int(pygame.time.get_ticks() - start_time)//1000 > 15:
                break
                
            currspeed_text, currspeed_rect = self.text_objects("Current Speed: "+str(obstacle_speed), self.text_font, self.black)
            currspeed_rect.center = ((self.display_width*1/4),(self.display_height*1/5 ))
            time_text, time_rect = self.text_objects("Time Elapsed: "+str(int(pygame.time.get_ticks() - start_time)//1000)+"s", self.text_font, self.black)
            time_rect.center = ((self.display_width*1/4),(self.display_height*1/5 + 40))

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
            x = self.x_data[-1]
            # self.x_data.task_done()
            self.screen.fill(self.grey)
            self.obstacle_starty += obstacle_speed
            item_starty += item_speed

            player_group.draw(self.screen)
            player_group.update(x,y)

            obstacle_group.draw(self.screen)
            obstacle_group.update(self.obstacle_startx,self.obstacle_starty)


            item_group.draw(self.screen)
            item_group.update(item_startx, item_starty)

            #show score
            self.score_display(str(player.bombnumber))
            self.update_leaderboard(0.75, 0.2)
            self.screen.blit(currspeed_text, currspeed_rect)
            self.screen.blit(time_text, time_rect)


            # Check for crashes
            if player.collide(obstacle_group):
                self.crash(obstacle_group, True)

            player.item_collect(item_group)
            if x > self.display_width - self.car_width or x < 0:
                self.crash(obstacle_group, False)

            if self.obstacle_starty > self.display_height:
                self.obstacle_starty = 0 - obstacle_height
                self.obstacle_startx = random.randrange(0,self.display_width)

            if item_starty > self.display_height:
                item_starty = 0
                item_startx = random.randrange(0,self.display_width)
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
        print("End Screen")
        while not self.gameExit:
            self.screen.fill(self.white)
            start_text, start_rect = self.text_objects("Awaiting Results", self.text_font, self.black)
            start_rect.center = ((self.display_width/2),(self.display_height/2-50))
    
            self.screen.blit(start_text, start_rect)
            self.update_leaderboard(0.5,0.75)
            mouse = pygame.mouse.get_pos() 
            if self.display_width/2-50 <= mouse[0] <= self.display_width/2+50 and self.display_height/2+20 <= mouse[1] <= self.display_height/2+60:
                pygame.draw.rect(self.screen, self.black, [self.display_width/2-50, self.display_height/2+20, 100, 40])
            else:
                pygame.draw.rect(self.screen, self.grey, [self.display_width/2-50, self.display_height/2+20, 100, 40])

            button_text_font = pygame.font.Font('assets/Roboto-Regular.ttf',15)
            startbutton_text, startbutton_rect = self.text_objects("Exit", button_text_font, self.black)
            startbutton_rect.center = ((self.display_width/2),(self.display_height/2+40))
            self.screen.blit(startbutton_text, startbutton_rect)

            if (self.final_flag.is_set()):
                final_text, final_rect = self.text_objects("Final", self.text_font, self.black)
                final_rect.center = ((self.display_width/2),60)
                self.screen.blit(final_text, final_rect)            
            
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    if self.display_width/2-50 <= mouse[0] <= self.display_width/2+50 and self.display_height/2+20 <= mouse[1] <= self.display_height/2+60: 
                        self.gameExit = True
        self.game_start()


if __name__ == "__main__":
    x_data = queue.Queue()
    y_data = queue.Queue()
    new_game = Game(x_data, y_data)
    new_game.game_start()
