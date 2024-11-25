from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from pygame.locals import *
import time
import sys
import sqlite3
from sqlite3 import Error
import easygui as eg

pygame.init()

#sets the screen dimensions and the score variable
screen_w = 600
screen_h = 600
score = 0

screen = pygame.display.set_mode((screen_w, screen_h))
pygame.display.set_caption('SmashPaddle')

#creates and defines the font style and size
font = pygame.font.SysFont('Constantia', 20)

#defines background colours
bg = (234, 218, 184)
#defines block colours
block_r = (242, 85, 96)
block_o = (255, 165, 0)
block_y = (255, 255, 0)
#defines paddle colours
paddle_colour = (142, 135, 123)
paddle_outl = (100, 100, 100)
#defines text colour
txt_colour = (78, 81, 139)

#defines game variables
columns = 6
rows = 6
clock = pygame.time.Clock()
fps = 60
global live_b
live_b = False
game_ovr = 0

#function for outputting the text onto the screen
def draw_txt(txt, font, txt_colour, x, y):
    img = font.render(txt, True, txt_colour)
    screen.blit(img, (x, y))

#wall class
class wall():
    def __init__(self):
        self.width = screen_w // columns
        self.height = 50

    def create_wall(self):
        self.blocks = []
        #creates an empty list for each individual block
        block_individ = []
        for row in range(rows):
            #reset the block row
            block_row = []
            #goes through each column in that row
            for column in range(columns):
                #generate x and y positions for each block and creates a rectangle from it
                block_x = column * self.width
                block_y = row * self.height
                rect = pygame.Rect(block_x, block_y, self.width, self.height)
                #gives each block a strength based on what row they are in
                if row < 2:
                    strength = 3
                elif row < 4:
                    strength = 2
                elif row < 6:
                    strength = 1
                #creates a list to store the rect and strength
                block_individ = [rect, strength]
                #appends the block to the block row
                block_row.append(block_individ)
            #appends the row to the wall of blocks
            self.blocks.append(block_row)

    def draw_wall(self):
        for row in self.blocks:
            for block in row:
                #gives each block a colour based on their strength
                if block[1] == 3:
                    block_colour = block_y #yellow = strength 3
                elif block[1] == 2:
                    block_colour = block_o #orange = strength 2
                elif block[1] == 1:
                    block_colour = block_r #red = strength 1
                pygame.draw.rect(screen, block_colour, block[0])
                pygame.draw.rect(screen, bg, (block[0]), 3)

class paddle():
    def __init__(self):
        self.reset()

    def move(self):
        #resets movement direction
        self.direction= 0
        key = pygame.key.get_pressed()
        #if left key is pressed then paddle moves left
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.velocity
            self.direction = -1
        #if right key is pressed then paddle moves right
        if key[pygame.K_RIGHT] and self.rect.right < screen_w:
            self.rect.x += self.velocity
            self.direction = 1

    def draw(self):
        #draws the paddle onto the screen with an outline around it
        pygame.draw.rect(screen, paddle_colour, self.rect)
        pygame.draw.rect(screen, paddle_outl, self.rect, 3)

    def reset(self):
        self.height = 20
        self.width = int(screen_w / columns)
        self.x = int((screen_w / 2) - (self.width / 2))
        self.y = screen_h - (self.height * 2)
        self.velocity = 10
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.direction = 0



#ball class
class ball():

    def __init__(self, x, y):

        #set score
        score = 0
        self.score = score
        #asks for player name at the start of the game
        self.name = eg.enterbox("What is your name?")
        while len(self.name) < 1:
            error1 = eg.msgbox("Error: Name is too short, please enter a longer name")
            self.name = eg.enterbox("What is your name?")
            while len(self.name) > 20:
                error2 = eg.msgbox("Error: Name is too long, please enter a shorter name")
                self.name = eg.enterbox("What is your name?")

        index = -1
        self.index = index


        #sets ball characteristics
        self.ball_radius = 10
        self.x = x - self.ball_radius
        self.y = y
        self.rect = Rect(self.x, self.y, self.ball_radius * 2, self.ball_radius * 2)
        self.velocity_x = 4
        self.velocity_y = -4
        self.velocity_m = 5
        self.game_ovr = 0


    def move(self):

        #used for debugging to see if score changes when hitting blocks, uncomment to check it out
        #draw_txt((str(self.score)), font, txt_colour, 350, screen_h // 2 + 150)
        collision_thresh = 5

        #starts off thinking that the wall is completely broken
        wall_destroyed = 1
        row_count = 0
        for row in wall.blocks:
            item_count = 0
            for item in row:
                #checks for collision
                if self.rect.colliderect(item[0]):

                    #checks if collision was from above the ball's location
                    while abs(self.rect.bottom - item[0].top) < collision_thresh and self.velocity_y > 0:
                        self.velocity_y *= -1

                    #checks if collision was from below the ball's location
                    while abs(self.rect.top - item[0].bottom) < collision_thresh and self.velocity_y < 0:
                        self.velocity_y *= -1

                    #checks if collision was from the left of the ball's location
                    while abs(self.rect.right - item[0].left) < collision_thresh and self.velocity_x > 0:
                        self.velocity_x *= -1

                    #checks if collision was from the right of the ball's location
                    while abs(self.rect.left - item[0].right) < collision_thresh and self.velocity_x < 0:
                        self.velocity_x *= -1

                    #lowers the blocks strength if it has been hit by the ball
                    if wall.blocks[row_count][item_count][1] > 1:
                        wall.blocks[row_count][item_count][1] -= 1

                        self.score += 5 # adds 5 points when a block is damaged but not broken
                    else:
                        wall.blocks[row_count][item_count][0] = (0, 0, 0, 0)

                        self.score += 20 #add 20 points when a block is broken

                #checks if the block is still there, in which case the wall is not broken
                if wall.blocks[row_count][item_count][0] != (0, 0, 0, 0):
                    wall_destroyed = 0

                #increases item counter
                item_count += 1

            #increases row counter
            row_count += 1

        #after going through all the blocks, checks if the wall is broken
        if wall_destroyed == 1:
            self.game_ovr = 1

        #sees if ball has hit any of the walls
        if self.rect.left < 0 or self.rect.right > screen_w:
            self.velocity_x *= -1

        #sees if the ball has hit the top or bottom of the screen
        if self.rect.top < 0:
            self.velocity_y *= -1
        if self.rect.bottom > screen_h:
            #if it has hit the bottom, the game is over
            self.game_ovr = -1


        #look for collision with paddle
        if self.rect.colliderect(player_pad):
            #checks if colliding from the top of the paddle
            if abs(self.rect.bottom - player_pad.rect.top) < collision_thresh and self.velocity_y > 0:
                self.velocity_y *= -1
                self.velocity_x += player_pad.direction
                if self.velocity_x > self.velocity_m:
                    self.velocity_x = self.velocity_m
                elif self.velocity_x < 0 and self.velocity_x < -self.velocity_m:
                    self.velocity_x = -self.velocity_m
            else:
                self.velocity_x *= -1 #reverses the ball's speed

        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        return self.game_ovr

    def draw(self):
         pygame.draw.circle(screen, paddle_colour, (self.rect.x + self.ball_radius, self.rect.y + self.ball_radius), self.ball_radius)
         pygame.draw.circle(screen, paddle_outl, (self.rect.x + self.ball_radius, self.rect.y + self.ball_radius), self.ball_radius, 3)

    def reset(self, x, y):
        self.ball_radius = 10
        self.x = x - self.ball_radius
        self.y = y
        self.rect = Rect(self.x, self.y, self.ball_radius * 2, self.ball_radius *2)
        self.velocity_x = 4
        self.velocity_y = -4
        self.velocity_m = 5
        self.game_ovr = 0



    def sql_connection():
        try:
            con = sqlite3.connect('mydatabase.db') #tries connecting to database called 'mydatabase.db'
            return con
        except Error:
            print(Error)

    def sql_table():
        try:
            con = sqlite3.connect('mydatabase.db') #tries connecting to database called 'mydatabase.db'
            cursorObj = con.cursor()
            #if database doesnt exist, it creates a new one
            cursorObj.execute("CREATE TABLE Scores(id int, name str PRIMARY KEY, score int)")
            con.commit()
        except:
            print("Table already exists")
            #if table already exists, it will notify the player

    def InsertData(self):
        global con
        con = sqlite3.connect('mydatabase.db')
        name = str(self.name)
        score = str(self.score)
        index = self.index
        cursor = con.cursor()
        try:
            count = cursor.execute("INSERT or REPLACE INTO Scores VALUES (?, ?, ?)", (index, name, score))
            con.commit()
            #tries to enter values into the database like the player's name and score
            print("Record inserted successfully into Scores table", cursor.rowcount)
            cursor.close()
        except sqlite3.Error as error:
            #if it does not go through, it prints an error
            print("Failed to insert data into sqlite table", error)
        finally:
            if con:
                con.close()
                #closes the connection with the database
                print("The SQLite connection is closed")

#creates a wall
wall = wall()
wall.create_wall()

#creates the paddle
player_pad = paddle()

#creating the ball
ball = ball(player_pad.x + (player_pad.width // 2), player_pad.y - player_pad.height)

##def unpause():
##        global pause
##        pause = False

def text_objects(text, font):
    textSurface = font.render(text, True, block_o)
    return textSurface, textSurface.get_rect()

#I have created these variables so that the buttons can disappear when the game is started
global start_button_visible
start_button_visible = True
global quit_button_visible
quit_button_visible = True
global starty11
starty11 = False

def button(msg, x, y, w, h, ic, ac, action = None):
    global starty11
    global start_button_visible
    global quit_button_visible



    if (starty11 == True):
        start()
        pygame.display.update()

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    ic = pygame.Color('red')
    ac = pygame.Color('yellow')
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, ac, (x, y, w, h))

        if click[0] and action is not None:
            if action == start:#when start button is clicked, game starts
                starty11 = True
                start_button_visible = False
                action()
            if action == quitgame:
                quitgame()#when quit button is clicked, game closes

    else:
        pygame.draw.rect(screen, ic, (x, y, w, h))

    smallText = pygame.font.SysFont('Constantia', 20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = (x + (w / 2), y + (h / 2))
    screen.blit(textSurf, textRect)


#quit game function
def quitgame():
        pygame.quit()
        sys.exit()

#start game function
def start():
        global intro
        global quit_button_visible
        global start_button_visible
        global starty11
        global live_b

        intro = False
        quit_button_visible = False
        start_button_visible = False #when the start button is clicked and the game begins,
        live_b = True                    #the buttons will disappear


        while live_b:
            clock.tick(fps)


            screen.fill(bg)


            wall.draw_wall()
            player_pad.draw()
            ball.draw()


            player_pad.move()

            game_ovr = ball.move()

            if game_ovr != 0:
                live_b = False


            if game_ovr == 1:
                draw_txt('CONGRATS, YOU WON!' , font, txt_colour, 240, screen_h // 2 + 50)
                draw_txt('CLICK ANYWHERE ON THE SCREEN TO START' , font, txt_colour, 100, screen_h // 2 + 100)

            elif game_ovr == -1:
                draw_txt('BETTER LUCK NEXT TIME! :(' , font, txt_colour, 175, screen_h // 2 + 50)
                draw_txt('CLICK ANYWHERE ON THE SCREEN TO START' , font, txt_colour, 100, screen_h // 2 + 100)

            if game_ovr == 1:
                draw_txt('YOUR SCORE WAS:', font, txt_colour, 150, screen_h // 2 + 150)
                draw_txt((str(ball.score)), font, txt_colour, 350, screen_h // 2 + 150)
                ball.index += 1
                ball.InsertData()

            if game_ovr == -1:
                draw_txt('YOUR SCORE WAS:', font, txt_colour, 150, screen_h // 2 + 150)
                draw_txt((str(ball.score)), font, txt_colour, 350, screen_h // 2 + 150)
                ball.index += 1
                ball.InsertData()


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()


        quit_button_visible = True
        start_button_visible = True
        starty11 = False


#game intro function
def game_intro():
        global intro
        intro = True

        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            #fills the screen and displays the title of the game and buttons
            screen.fill(bg)
            largeText = pygame.font.SysFont('Constantia', 60) #defines large text
            TextSurf, TextRect = text_objects("SMASH PADDLE", largeText) #draws the title onto the main menu screen
            TextRect.center = ((screen_w / 2), (screen_h / 2))
            screen.blit(TextSurf, TextRect)

            button("QUIT", 350, 450, 100, 50, pygame.Color('red'), pygame.Color('yellow'), quitgame) #dimensions for quit button
            button("START", 150, 450, 100, 50, pygame.Color('red'), pygame.Color('yellow'), start) # dimensions for start button

            pygame.display.update()
            clock.tick(fps)

##def paused():
##        largeText = pygame.font.SysFont('Constantia', 115)
##        TextSurf, TextRect = text_objects("PAUSED", largeText)
##        TextRect.center = ((screen_w / 2), (screen_h / 2))
##        screen.blit(TextSurf, TextRect)
##
##        while pause:
##            for event in pygame.event.get():
##                if event.type == pygame.QUIT:
##                    quit()
##
##            button("RESUME", 150, 450, 100, 50, block_r, unpause)
##            button("QUIT", 550, 450, 100, 50, block_y, quitgame)
##            clock.tick(fps)

def ReadData():
    global con
    con = sql_connection()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM 'Scores'")
    results = cursor.fetchall()
    for x in results:
        print(x)
    con.close()


global name
game_intro() #runs the game intro procedure before the main loop
run = True
while run:
    if live_b == False:
        time.sleep(10000)
        live_b = True
        ball.index += 1
        ball.InsertData() #inserts data when the ball is out of play

        ball.score = 0 # reset score everytime the player dies

        ball.reset(player_pad.x + (player_pad.width // 2), player_pad.y - player_pad.height)
        player_pad.reset()
        wall.create_wall()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False


    pygame.display.update()

pygame.quit()


