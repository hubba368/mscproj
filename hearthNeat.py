import multiprocessing
import os
import pickle
import random
import time

import neat
import neatArena



class Arena(object):

    def __init__(self, num_workers, fireplace):
        self.num_workers = num_workers
        self.testEps = []
        self.generation = 0
        self.fireplace = fireplace

        self.min = -100
        self.max = 100

        self.epScore = []
        self.epLen = []
        #print(fireplace.GetValidMoves(self.fireplace.game))

    def SimulateState(self, nets):
        scores = []

        self.fireplace.InitGame()
        numGames = 1
        for genome, net in nets:
            step = 0
            data = []
            genome.fitness = 0
            
            numwin = 0
            numloss = 0

            while 1:
                if step == numGames:
                    return numloss, numwin
                input = self.fireplace.testgame(self.fireplace.game)
                #actions = self.fireplace.GetValidMoves(self.fireplace.game)

                #print(input)
                print("ACTIONS===============\n")
                #print(actions)
                print("\n")
                if input is not None:
                    #for i in input:
                    output = net.activate(input)
                    print("OUTPUT\n")
                    print(output)

                    self.fireplace.PerformAction(output, self.fireplace.game)

                    result = self.fireplace.GameEnded()
                    if result is not None:
                        if result == 0 or -1:
                            numloss+=1
                        elif result == 1:
                            numwin+= 1
                        step +=1
                #print(self.fireplace.GetValidMoves(self.fireplace.game))

    def EvalGenomes(self, genomes, config):
        self.generation = 1

        t0 = time.time()
        nets = []

        for gid, g in genomes:
            nets.append((g, neat.nn.FeedForwardNetwork.create(g, config)))
        
        print("network creation time {0}".format(time.time() - t0))
        t0 = time.time()

        loss, win = self.SimulateState(nets)
        
        if self.num_workers < 2:
            for g, net in nets:
                g.fitness = Fitness(g, net, float(loss), float(win))


        


def Fitness(genome, net, loss, win):
    genome.fitness += val



def run():

    dir = os.path.dirname(__file__)
    configPath = os.path.join(dir, 'config')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                    configPath)

    population = neat.Population(config)
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    population.add_reporter(neat.StdOutReporter(True))

    tester = neatArena.NeatArena(True)
    arena = Arena(1, tester)

    while 1:
        try:
            gen_best = population.run(arena.EvalGenomes, 1)

        except KeyboardInterrupt:
            print("stop")
            break

    


if __name__ == '__main__':
    run()
    


