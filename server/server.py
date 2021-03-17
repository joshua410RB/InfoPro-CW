# global variables
dt = 1

class Game:
    def __init__(self):
        print("Hello World!")
        self.people = []
    
    def join(self, id):
        self.people.append(Human(id))

    def calcRanking(self):
        # do something to calculate ranking
        pass

    def bomb(self):
        pass

# id should correspond to index of list
class Human:
    def __init__(self, id):
        self.id = id 
        self.dist = 0
        self.prev_speed = 0
        self.speed = 0
        self.position = 1
        self.hasBomb = False
    
    def calcDist(self, newacc):
        self.prev_speed = self.speed 
        self.speed = self.prev_speed + newacc
        self.dist += 1/2*(self.speed + self.prev_speed)*dt

    def sendRanking(self):
        pass

    def sendBomb(self):
        pass


def createGame():
    game = Game()
    game.join(0)
    return game

def calcCurrDist(game):
    while True:
        try:
            acc = int(input())
            game.people[0].calcDist(acc)
            print(game.people[0].dist)

        except EOFError:
            print(game.people[0].dist)
            break

def main():
    game = createGame()
    calcCurrDist(game)


if __name__ == '__main__': 
    main()