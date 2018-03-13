import pygame

from PodSixNet.Connection import ConnectionListener, connection
from time import sleep
from pygame.locals import *


class GameX(ConnectionListener):

    # player variable
    play = 0

    def __init__(self):
        pygame.init()
        size = width, height = 600, 600

        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Setup")

        self.bg = (200, 200, 200)

        self.players = []
        self.players.append(Player(pygame.image.load("player1.png")))
        self.players.append(Player(pygame.image.load("player2.png")))
        self.players[1].rect.x = width - self.players[1].rect.width
        # print(self.players[1].rect.x)

        # ball display
        self.ball = Ball(pygame.image.load("ball.png"))
        self.ball.rect.x = width/3
        self.ball.rect.y = height/4 + height/2
        self.positiveX = 1
        self.positiveY = 1
        self.ball.out = 0

        self.gameID = None
        self.player = None

        self.clock = pygame.time.Clock()

        self.screen.fill(self.bg)

        # self.Connect()
        # Trying multi PC
        address = raw_input('Address os server: ')
        try:
            if not address:
                host, port = "localhost", 8000
            else:
                host, port = address.split(":")
            self.Connect((host, int(port)))
        except:
            print("Error Connecting to server")
            exit()

        print("Connection Done")

        self.running = False

        while not self.running:
            self.check_exit()

            self.Pump()
            connection.Pump()
            sleep(0.01)

        pygame.display.set_caption("Gameid: {} - player:{}".format(self.gameID, self.player))

    def get_keys(self):
        keys = pygame.key.get_pressed()

        if keys[K_UP]:
            self.players[self.player].rect.y -= self.velocity
            self.Send({"action": "move", "x": 0, "y": -self.velocity, "player":self.player, "gameID": self.gameID})

        if keys[K_DOWN]:
            self.players[self.player].rect.y += self.velocity
            self.Send({"action": "move", "x": 0, "y": +self.velocity, "player": self.player, "gameID": self.gameID})

    def send_ball(self):

        # variable to recognise player
        global play

        if self.ball.rect.x >= 600 or self.ball.rect.x <= -100:
            self.ball.out = 1
        if self.ball.rect.y >= 500:
            self.positiveY = 0
        if self.ball.rect.y <= 0:
            self.positiveY = 1

        # player contact

        if self.ball.rect.x == self.players[1].rect.x - 90: # -10 to look good
            print("in player 1 " + str(self.ball.rect.y) + " " + str(self.players[1].rect.y))
            # if self.ball.rect.y >= self.players[1].rect.y-20 and self.ball.rect.y <= self.players[1].rect.y + 20
            if self.players[1].rect.y - 100 <= self.ball.rect.y <= self.players[1].rect.y + 100:
                print("Contact")
                self.play = 1

        if self.ball.rect.x == self.players[0].rect.x :
            print("in player 0")
            if self.players[0].rect.y - 100 <= self.ball.rect.y <= self.players[0].rect.y + 100:
                print("Contact")
                self.play = 0

        # print(self.play)
        # print(play)
        self.Send({"action": "moveBall", "x": self.ball.rect.x, "y": self.ball.rect.y, "player": self.player, "gameID": self.gameID, "out": self.ball.out, "positiveY": self.positiveY, "play": self.play})

    def update(self):

        connection.Pump()
        self.Pump()

        self.check_exit()

        self.get_keys()

        # asking for ball update
        self.send_ball()

        self.clock.tick(60)

        self.screen.fill(self.bg)

        for p in self.players:
            self.screen.blit(p.img, p.rect)

        self.screen.blit(self.ball.img, self.ball.rect)

        pygame.display.flip()

    def Network_startgame(self, data):
        self.gameID = data['gameID']
        self.player = data['player']
        self.running = True
        self.velocity = data['velocity']
        w, h = pygame.display.get_surface().get_size()
        #print(str(w)+" "+str(h))

    def Network_position(self, data):
        p = data['player']

        self.players[p].rect.y = data['y']

    # info of ball comes here
    def Network_ball(self, data):
        self.ball.rect.x = data['x']
        self.ball.rect.y = data['y']

    def check_exit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()


class Player(object):
    def __init__(self, img):
        self.img = img
        self.rect = img.get_rect()


class Ball(object):
    def __init__(self, img):
        self.img = img
        self.rect = img.get_rect()
        self.dir_x = 1
        self.dir_y = 1

        # Consider Top Left as (0,0)
        self.positiveX = 1
        self.positiveY = 1

        self.out = 0


if __name__ == "__main__":
    og = GameX()
    # print("Asdasd")
    while True:
        og.update()