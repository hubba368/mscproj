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
        

    def SimulateState(self, nets):
        data = []
        
        numGames = 10
        netNum = 0
        print(len(nets))
        for genome, net in nets:
            step = 0
            self.StartNewGame(self.fireplace)
            
            netNum += 1 
            numwin = 0
            numloss = 0
            numMaxActionDupes = 3
            numCurDupes = 0

            print("\nStarting new game for Net {}.\n".format(netNum))

            while step != numGames:              
                input = self.fireplace.testgame(self.fireplace.game)

                if input is not None:
                    #for i in input:
                    output = net.activate(input)
                    print("OUTPUT\n")
                    print(output)

                    '''
                    outputs = action (play card, attack with minion/weapon/hero power, end turn)
                              target (minion (either side), hero, none (e.g. summon minion))

                    '''
                    testd = self.fireplace.PerformAction(output, self.fireplace.game)
                    
                    # if attempting move when game is over force end
                    if testd == 0:                       
                        res = self.CheckIfGameEnded(self.fireplace, step,
                        numGames, numloss, numwin, netNum)
                        if res != -1:
                            step +=1
                            numloss += 1 if res == 0 else 0
                            numwin += 1 if res == 1 else 0
                    
                    # force end turn if turn errors
                    if testd == 1:
                        numCurDupes += 1
                    
                    if numCurDupes == numMaxActionDupes:
                        self.fireplace.ForceEndTurn(self.fireplace.game)
                        numCurDupes = 0
                                   
                else:
                    # start new
                    if step != numGames:
                        res = self.CheckIfGameEnded(self.fireplace, step,
                        numGames, numloss, numwin, netNum)
                        if res != -1:
                            step +=1
                            numloss += 1 if res == 0 else 0
                            numwin += 1 if res == 1 else 0
                            self.StartNewGame(self.fireplace)

            final = []
            print("Net: {}".format(netNum))
            print("wins: {}".format(numwin))
            print("losses: {}".format(numloss))
            final.append(netNum)
            final.append(numloss)
            final.append(numwin)
            data.append(final)
            
        if len(data) > 0:
            print(len(data))
            return data
                            
    def CheckIfGameEnded(self, instance, curGameCount, maxGameCount, numloss, numwin, netNum):
        endCheck = instance.GameEnded()
        
        if endCheck is not None:
            print("End Check: {}".format(endCheck))
            if endCheck == 0 or -1:
                print("LOSS")                      
                return 0                   
            elif endCheck == 1:
                print("WIN")            
                return 1
        else:
            print("not done yet")
            return -1

    def StartNewGame(self, fireplace):
        fireplace.InitGame()
    

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
            print(gen_best)
        except KeyboardInterrupt:
            print("stop")
            break

    


if __name__ == '__main__':
    run()
    


