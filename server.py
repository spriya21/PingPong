from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
import time

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
        out = data['out']
        positiveY = data['positiveY']
        play = data['play']
        dif_x = 2
        dif_y = 2

        self._server.ball(ball_x, ball_y, gameID, out, positiveY, play)


class GameServer(Server):
    channelClass = ClientChannel

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
            time.sleep(2)

    def move_player(self, x, y, gameId, player):

        g = self.games[gameId]
        g.players[player].move(x, y)

        for i in range(0, len(g.player_channels)):
            if not i == player:
                g.player_channels[i].Send({"action": "position", "player": player, "x": g.players[player].x, "y": g.players[player].y})

    # function to move ball on screen
    def ball(self, ball_x, ball_y, gameID, out, positiveY, play):

        if out == 1:
            print("Out of bound")
            print(play)
            # s.close()
        else:
            if play == 0:
                ball_x += 2
            if play == 1:
                ball_x -= 2

            if positiveY == 1:
                ball_y += 2
            if positiveY == 0:
                ball_y -= 2
                print(ball_x, ball_y)

        g = self.games[gameID]

        # hardcoding width height of 600, 600

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

















