import pygame
import time
import random
import queue
import logging
from pygame.locals import *
import config

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

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

    def item_collect(self, item_group):
        item_hit = pygame.sprite.spritecollide(self, item_group, True)
        if len(item_hit)>0:
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
        self.image = pygame.image.load('img/item.png')
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
    def update(self, pos_x, pos_y):
        self.rect.center = [pos_x, pos_y]


class Game():
    def __init__(self, x_data1, y_data1, 
                 ready_flag, start_flag, start_queue_flag, final_flag, 
                 leaderboard_object, ready_object, end_flag, bp_flag, send_bomb_flag, bombed_flag,
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
        self.screen = pygame.display.set_mode((self.display_width,self.display_height), DOUBLEBUF)
        self.screen.set_alpha(None)
        pygame.display.set_caption('Multiplayer Racing Game')
        self.icon = pygame.image.load('img/checkered-flag.png') #  icon from: Flaticon.com
        pygame.display.set_icon(self.icon)
        self.clock = pygame.time.Clock()
        # Set game objects
        self.x_data = x_data1
        self.y_data = y_data1
        self.ready_flag = ready_flag
        self.start_flag = start_flag
        self.start_queue_flag = start_queue_flag
        self.final_flag = final_flag
        self.end_flag = end_flag
        self.bp_flag = bp_flag
        self.bombed_flag = bombed_flag
        self.send_bomb_flag = send_bomb_flag
        self.gameStart = False
        self.gameExit = False
        self.leaderboard = leaderboard_object
        self.ready = ready_object
        self.text_font = pygame.font.Font('assets/Roboto-Regular.ttf',30)
        self.text_font_small = pygame.font.Font('assets/Roboto-Regular.ttf',15)
        self.largeText = pygame.font.Font('freesansbold.ttf',40)

        self.obstacle_starty = -self.display_height
        self.obstacle_startx = random.randrange(0, self.display_width)
        self.Bg1 = pygame.image.load('img/startscreen.png').convert()
        self.Bg2 = pygame.image.load('img/multiplayer_screen.png').convert()
        self.Bg3 = pygame.image.load('img/ready_screen.png').convert()
        self.Bg4 = pygame.image.load('img/countdown_screen.png').convert()
        self.roadBg = pygame.image.load('img/road.png').convert()
        self.calculatingBg = pygame.image.load('img/calculating.png').convert()
        self.finalBg = pygame.image.load('img/final_result.png').convert()
        self.leaderboardBg = pygame.image.load('img/leaderboard.png').convert()
        self.bombnumber = 0

        # Pre rendering text
        self.slow_text = self.text_objects("You are slowed!", self.largeText, self.white)
        self.crash_text = self.text_objects("You have crashed!", self.largeText, self.white)

        #### START SCREEN features rendering ####

        # Multiplayer mode button
        self.start_white_m = pygame.draw.rect(self.screen, self.white, [self.display_width/2+20, self.display_height/2-20, 100, 40])
        self.start_grey_m = pygame.draw.rect(self.screen, self.grey, [self.display_width/2+20, self.display_height/2-20, 100, 40])
        self.start_m_text = self.text_objects("Multiplayer", self.text_font_small, self.white)

        # Singleplayer mode
        self.start_white_s = pygame.draw.rect(self.screen, self.white, [self.display_width/2-120, self.display_height/2-20, 100, 40])
        self.start_grey_s = pygame.draw.rect(self.screen, self.grey, [self.display_width/2-120, self.display_height/2-20, 100, 40])
        self.start_s_text = self.text_objects("Single Player", self.text_font_small, self.white)


        #### MULTIPLAYER SCREEN ####
        # Ready
        self.multiplayer_title_text = self.text_objects("Multiplayer Mode", self.text_font, self.white)
        self.ready_text = self.text_objects("Ready", self.text_font_small, self.black)
        self.ready_button_w = pygame.draw.rect(self.screen, self.white, [self.display_width/2-50, self.display_height/2-40, 100, 40])
        self.ready_button_g = pygame.draw.rect(self.screen, self.grey, [self.display_width/2-50, self.display_height/2-40, 100, 40])

        #### LOBBY SCREEN ####
        self.lobby_text = self.text_objects("In Lobby", self.text_font, self.white)

        #### LEADERBOARD SCREEN ####
        self.leaderboard_text = self.text_objects("Leaderboard", self.text_font_small, self.white)

        #### ENDSCREEN ####
        self.exit_button_w = pygame.draw.rect(self.screen, self.white, [self.display_width/2-50, self.display_height/2+80, 100, 40])
        self.exit_button_g = pygame.draw.rect(self.screen, self.grey, [self.display_width/2-50, self.display_height/2+80, 100, 40])
        self.exit_text = self.text_objects("Exit", self.text_font_small, self.white)       

    def text_objects(self, text, font, color):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()


    def score_display(self, text) :
        TextSurf, TextRect = self.text_objects("Bombcount: " + text, self.text_font_small, self.white)
        TextRect.center = ((self.display_width/2),(self.display_height*1/5))
        self.screen.blit(TextSurf, TextRect)

    def queue_empty(self):
        # for _ in range(self.x_data.qsize()):
        self.x_data.clear()
        # for _ in range(self.y_data.qsize()):
        self.y_data.clear()
        logging.debug("Queues Emptied")

    def crash(self, obstacle_group, create_new):
        self.start_queue_flag.clear()        
        TextSurf, TextRect = self.crash_text 
        TextRect.center = ((self.display_width/2),(self.display_height/2))
        self.screen.blit(TextSurf, TextRect)

        # so that it resets and triggers a new obstacle at the top
        if (create_new):
            self.obstacle_starty = -200
            obstacle = Obstacle(self.obstacle_startx, self.obstacle_starty)
            obstacle_group.add(obstacle)
        pygame.display.update()

        # Emptying queue
        self.queue_empty()

        time.sleep(2)
        self.start_queue_flag.set()
        time.sleep(0.5)

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
            # start_rect.center = ((self.display_width/2),(self.display_height/2-50))
    
            self.screen.blit(start_text, start_rect)

            mouse = pygame.mouse.get_pos() 
            if self.display_width/2+20 <= mouse[0] <= self.display_width/2+120 and self.display_height/2-20 <= mouse[1] <= self.display_height/2+20:
                self.start_white_m
            else:
                self.start_grey_m

            if self.display_width/2-120 <= mouse[0] <= self.display_width/2-20 and self.display_height/2-20 <= mouse[1] <= self.display_height/2+20:
                self.start_white_s
            else:
                self.start_grey_s

            mult_button_text, mult_button_rect = self.start_m_text
            mult_button_rect.center = ((self.display_width/2+70),(self.display_height/2))
            self.screen.blit(mult_button_text, mult_button_rect)
            
            single_button_text, single_button_rect = self.start_s_text
            single_button_rect.center = ((self.display_width/2-70),(self.display_height/2))
            self.screen.blit(single_button_text, single_button_rect)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    if self.display_width/2+20 <= mouse[0] <= self.display_width/2+120 and self.display_height/2-20 <= mouse[1] <= self.display_height/2+20: 
                        self.gameStart =True 
                    if self.display_width/2-120 <= mouse[0] <= self.display_width/2-20 and self.display_height/2-20 <= mouse[1] <= self.display_height/2+20: 
                        self.gameStart =True 
                        self.start_queue_flag.set()
                        self.end_flag.clear()
                        # self.race_screen("single")
                        self.countdown_screen()

        self.multiplayer_screen()

    def multiplayer_screen(self):
        # Ready Button Screen
        while not self.ready_flag.is_set():            
            self.screen.blit(self.Bg2, (0,0))
            start_text, start_rect = self.multiplayer_title_text
            start_rect.center = ((self.display_width/2),(self.display_height/2-80))
            self.screen.blit(start_text, start_rect)
            #self.update_readystatus(self.display_width/2, self.display_height/2)
            mouse = pygame.mouse.get_pos() 
            if self.display_width/2-50 <= mouse[0] <= self.display_width/2+50 and self.display_height/2-40 <= mouse[1] <= self.display_height/2:
                self.ready_button_w
            else:
                self.ready_button_g

            startbutton_text, startbutton_rect = self.ready_text
            startbutton_rect.center = ((self.display_width/2),(self.display_height/2-20))
            self.screen.blit(startbutton_text, startbutton_rect)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    if self.display_width/2-50 <= mouse[0] <= self.display_width/2+50 and self.display_height/2-40 <= mouse[1] <= self.display_height/2: 
                        self.ready_flag.set()
                        logging.debug("Ready")

        # Waiting for Start Screen
        while not self.start_flag.is_set():
            self.screen.fill(self.white)
            self.screen.blit(self.Bg3, (0,0))
            #waiting_text, waiting_rect = self.text_objects("Game is starting soon...", self.text_font, self.black)
            #waiting_rect.center = ((self.display_width/2),(self.display_height/2-120))
            #self.screen.blit(waiting_text, waiting_rect)
            self.update_readystatus(self.display_width/2, self.display_height/2+120)
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
        
        countdown = 3
        while int(pygame.time.get_ticks() - start_time)//1000 < 4:
            self.screen.blit(self.Bg4, (0,0))
            text = "START!" if (countdown == 0) else str(countdown)
            countdown_text, countdown_rect = self.text_objects(text, self.text_font, self.black)
            countdown_rect.center = ((self.display_width/2),(self.display_height/2))
            self.screen.blit(countdown_text, countdown_rect)
            if int(pygame.time.get_ticks() - start_time)//1000 > (3-countdown):
                countdown -= 1
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit() 
        self.start_queue_flag.set()
        self.race_screen("mult")

    def update_readystatus(self, width_margin, height_margin):
        lb_title, lb_rect = self.lobby_text
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

            lb_text, lb_rect = self.text_objects(str(name)+": "+status_string, self.text_font, self.white)
            lb_rect.center = ((self.display_width-width_margin),(self.display_height-height_margin+margin))
            self.screen.blit(lb_text, lb_rect)
            margin += 40

    def update_leaderboard(self, width_pos, height_pos):
        lb_title, lb_rect = self.leaderboard_text
        lb_rect.center = ((self.display_width*width_pos),(self.display_height*height_pos))
        self.screen.blit(lb_title, lb_rect)
        position = 1
        margin = 40 
        for _, vals in self.leaderboard.items():
            lb_text, lb_rect = self.text_objects(str(position) + ". "+ str(vals[0])+": "+str(vals[1])+"m", self.text_font_small, self.white)
            lb_rect.center = ((self.display_width*width_pos),(self.display_height*height_pos+margin))
            self.screen.blit(lb_text, lb_rect)
            margin += 40
            position += 1

    def race_screen(self, mode):
        logging.debug("Go into race screen, "+ mode)
        start_time = pygame.time.get_ticks()
        start_slow_time = 0
        slowed = False

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
        self.obstacle_startx = item_startx = random.randrange(10, self.display_width-10)
        self.obstacle_starty=item_starty = -self.display_height
        item_group  = pygame.sprite.Group()        
        item = Item(item_startx, item_starty)
        item_group.add(item)

        while (self.gameStart):
            self.screen.blit(self.roadBg,(0,0))  
            try:
                obstacle_speed = config.y_game_data
                logging.debug("Taking from y queue")
            except IndexError:
                logging.debug("Y queue empty")
            item_speed = obstacle_speed - 2

            
            if (int(pygame.time.get_ticks() - start_time)//1000 > 30):
                break
                
            currspeed_text, currspeed_rect = self.text_objects("Current Speed: "+str(obstacle_speed), self.text_font_small, self.white)
            currspeed_rect.center = ((self.display_width*1/4),(self.display_height*1/5 ))
            time_text, time_rect = self.text_objects("Time Elapsed: "+str(int(pygame.time.get_ticks() - start_time)//1000)+"s", self.text_font_small, self.white)
            time_rect.center = ((self.display_width*1/4),(self.display_height*1/5 + 40))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            # x = self.x_data[-1]
            try:
                x = config.x_data
                logging.debug("Taking from queue")
            except IndexError:
                logging.debug("Queue Empty")
            self.obstacle_starty += obstacle_speed
            item_starty += item_speed

            player_group.draw(self.screen)
            player_group.update(x,y)

            obstacle_group.draw(self.screen)
            obstacle_group.update(self.obstacle_startx,self.obstacle_starty)


            item_group.draw(self.screen)
            item_group.update(item_startx, item_starty)

            #show score
            self.score_display(str(self.bombnumber))
            self.update_leaderboard(0.75, 0.2)
            self.screen.blit(currspeed_text, currspeed_rect)
            self.screen.blit(time_text, time_rect)

            # Bomb Logic
            if mode == "mult":
                if self.bp_flag.is_set():
                    logging.debug("Button is Pressed!")
                    if self.bombnumber > 0:
                        logging.debug("Bomb Sent from game!")
                        self.bombnumber -= 1
                        self.bp_flag.clear()
                        self.send_bomb_flag.set()
                        logging.debug("Sent bomb")

                if self.bombed_flag.is_set():
                    start_slow_time = pygame.time.get_ticks()
                    self.bombed_flag.clear()
                    slowed = True

                if (slowed):
                    if int(pygame.time.get_ticks() - start_slow_time)//1000 < 3:
                        TextSurf, TextRect = self.slowed_text 
                        TextRect.center = ((self.display_width/2),(self.display_height/2))
                        self.screen.blit(TextSurf, TextRect)
                    else:
                        slowed = False

            # Check for crashes
            if player.collide(obstacle_group):
                self.crash(obstacle_group, True)

            if player.item_collect(item_group):
                item_starty = 0
                item_startx = random.randrange(0,self.display_width)
                item = Item(item_startx, item_starty)
                item_group.add(item)
                self.bombnumber += 1

            if x > self.display_width - self.car_width or x < 0:
                self.crash(obstacle_group, False)

            if self.obstacle_starty > self.display_height:
                self.obstacle_starty = 0 - obstacle_height
                self.obstacle_startx = random.randrange(10,self.display_width-10)

            if item_starty > self.display_height:
                item_starty = 0
                item_startx = random.randrange(10,self.display_width-10)

            pygame.display.update()
            self.clock.tick(120)

        self.end_flag.set()
        self.end_screen()
     
    def end_screen(self):
        logging.debug("End Screen")
        while not self.gameExit:
            self.screen.blit(self.leaderboardBg, (0,0))
            self.screen.blit(self.calculatingBg, (250, 505)) 

            self.update_leaderboard(0.5,0.25)
            mouse = pygame.mouse.get_pos() 
            if self.display_width/2-50 <= mouse[0] <= self.display_width/2+50 and self.display_height/2+80 <= mouse[1] <= self.display_height/2+120:
                self.exit_button_w
            else:
                self.exit_button_g

            startbutton_text, startbutton_rect = self.text_objects("Exit", self.text_font_small, self.black)
            startbutton_rect.center = ((self.display_width/2),(self.display_height/2+100))
            self.screen.blit(startbutton_text, startbutton_rect)

            if (self.final_flag.is_set()):
                #final_text, final_rect = self.text_objects("CONGRATULATIONS!", self.text_font, self.black)
                #final_rect.center = ((self.display_width/2),60)
                #self.screen.blit(final_text, final_rect)
                self.screen.blit(self.finalBg, (250, 505))           
            
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    if self.display_width/2-50 <= mouse[0] <= self.display_width/2+50 and self.display_height/2+80 <= mouse[1] <= self.display_height/2+120: 
                        self.gameExit = True
                        self.start_queue_flag.clear()
        self.gameExit = False
        self.gameStart = False
        self.end_flag.clear()
        self.ready_flag.clear()
        self.queue_empty()
        self.game_start()


if __name__ == "__main__":
    x_data = queue.Queue()
    y_data = queue.Queue()
    new_game = Game(x_data, y_data)
    new_game.game_start()