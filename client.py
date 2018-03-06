import pygame

from PodSixNet.Connection import ConnectionListener, connection
from time import sleep
from pygame.locals import *


class GameX(ConnectionListener):
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

        # ball display
        self.ball = Ball(pygame.image.load("ball.png"))
        # self.ball = pygame.transform.scale(self.ball.img, (50, 50))
        self.ball.rect.x = width/2
        self.ball.rect.y = height/2


        self.gameID = None
        self.player = None

        self.clock = pygame.time.Clock()

        self.screen.fill(self.bg)

        self.Connect()

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

    def send_ball_once(self):
       self.Send({"action": "moveBall", "x": self.ball.rect.x, "y": self.ball.rect.y, "player": self.player, "gameID": self.gameID})

    def update(self):

        connection.Pump()
        self.Pump()

        self.check_exit()

        self.get_keys()
        self.send_ball_once()

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


if __name__ == "__main__":
    og = GameX()

    while True:
        og.update()