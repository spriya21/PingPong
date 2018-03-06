from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

from time import sleep


class ClientChannel(Channel):

    def Network_move(self, data):
        gameID = data['gameID']
        player = data['player']

        x = data['x']
        y = data['y']

        self._server.move_player(x, y, gameID, player)

    def Network_moveBall(self, data):
        gameID = data['gameID']
        player = data['player']
        ball_x = data['x']
        ball_y = data['y']
        # dif_x = 2
        # dif_y = 2

        self._server.ball(ball_x, ball_y, gameID, player)


class GameServer(Server):
    channelClass = ClientChannel
    dif_x = 2
    dif_y = 2

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)

        # Objects to hold in-case of multi instance;
        self.games = []
        self.queue = None
        self.gameIndex = 0

        self.velocity = 5

    def Connected(self, channel, addr):
        print("New Connection: {}".format(channel))

        if self.queue == None:
            channel.gameID = self.gameIndex
            self.queue = Game(channel, self.gameIndex)

        else:
            channel.gameID = self.gameIndex

            # Dont know what this does
            self.queue.player_channels.append(channel)

            for i in range(0, len(self.queue.player_channels)):
                self.queue.player_channels[i].Send({"action": "startgame", "player": i, "gameID": self.queue.gameID, "velocity": self.velocity})

            self.games.append(self.queue)
            self.queue = None
            self.gameIndex += 1


    def move_player(self, x, y, gameId, player):

        g = self.games[gameId]
        g.players[player].move(x, y)

        for i in range(0, len(g.player_channels)):
            if not i == player:
                g.player_channels[i].Send({"action": "position", "player": player, "x": g.players[player].x, "y": g.players[player].y})

            # g.player_channels[i].Send({"action":"ball", "player":player, "ball_x":ball.x, "ball_y":ball.y})

    #function to move ball on screen
    def ball(self, ball_x, ball_y, gameID, player):
        dif_x = 2
        dif_y = 2
        g = self.games[gameID]

        # hardcoding width height of 600, 600
        if ball_x >= 500:
            ball_x = 450
            dif_x *= -1

        if ball_x <= 0:
            dif_x *= -1

        if ball_y >= 500:
            dif_y *= -1

        if ball_y <= 0:
            dif_y *= 1

        ball_x += dif_x
        ball_y += dif_y

        print(ball_x, ball_y)
        sleep(0.0001)

        for i in range(0, len(g.player_channels)):
            g.player_channels[i].Send({"action": "ball", "x": ball_x, "y": ball_y})
        
        

class Game(object):

    def __init__(self, player, gameIndex):
        self.players = []
        self.players.append(Player(0, 0))
        self.players.append(Player(550, 0))

        self.player_channels = [player]

        self.gameID = gameIndex


class Player(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, x, y):
        self.x += x
        self.y += y


if __name__ == "__main__":
    print("Server starting ")

    s = GameServer()

    while True:
        s.Pump()
        sleep(0.0001)

















