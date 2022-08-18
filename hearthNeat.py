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
        data = []
        
        numGames = 3
        netNum = 0
        for genome, net in nets:
            step = 0
            self.fireplace.InitGame()
            
            netNum += 1 
            numwin = 0
            numloss = 0
            numMaxActionDupes = 3
            numCurDupes = 0

            while step != numGames:              
                input = self.fireplace.testgame(self.fireplace.game)
                #actions = self.fireplace.GetValidMoves(self.fireplace.game)

                #print("INPUT=================\n")
                #print(input)
                #print("ACTIONS===============\n")
                #print(actions)
                print("\n")
                if input is not None:
                    #for i in input:
                    output = net.activate(input)
                    print("OUTPUT\n")
                    print(output)

                    '''
                    outputs = action (play card, attack with minion/weapon/hero power, end turn)
                              target (minion (either side), hero, none (e.g. summon minion))

                    '''
                    # TODO add "retries" if it attempts invalid move
                    # with max num in which case it ends turn

                    testd = self.fireplace.PerformAction(output, self.fireplace.game)
                    
                    if testd == 0:
                        step +=1
                    if testd == 1:
                        numCurDupes += 1
                    
                    if numCurDupes == numMaxActionDupes:
                        self.fireplace.ForceEndTurn(self.fireplace.game)
                        numCurDupes = 0
                    

                else:
                    result = self.fireplace.GameEnded()
                    if result is not None:
                        if result == 0 or -1:
                            numloss+=1
                        elif result == 1:
                            numwin+= 1
                        print("testing !!!!!!!!!!")
                        print("wins: {}".format(numwin))
                        print("loss: {}".format(numloss))
                        step +=1
                        if step == numGames:
                            result = (netNum, numloss, numwin)
                            data.append(result) 
                            break  

        if data is not None:
            return data
                            



    def EvalGenomes(self, genomes, config):
        self.generation = 1

        t0 = time.time()
        nets = []

        for gid, g in genomes:
            g.fitness = 0.0
            nets.append((g, neat.nn.RecurrentNetwork.create(g, config)))
        
        print("network creation time {0}".format(time.time() - t0))
        t0 = time.time()

        results = self.SimulateState(nets)

        for i in range(len(nets)):
            g = nets[i][0]
            net = nets[i][1]

            netnum = results[i][0]
            numloss = results[i][1]
            numwin = results[i][2]
            print("Net: {}".format(netnum))
            print(g.fitness)
            g.fitness = Fitness(g, net, float(numloss), float(numwin))
            print(g.fitness)

        


def Fitness(genome, net, loss, win):
    fit = 0.0
    fit += win
    fit -= loss
    return fit


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
            gen_best = population.run(arena.EvalGenomes, 3)

        except KeyboardInterrupt:
            print("stop")
            break

    


if __name__ == '__main__':
    run()
    


