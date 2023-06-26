import multiprocessing
import os
import pickle
import random
import time
import Utils
import neat
import neatArena
import EvalChamber



class Arena(object):

    def __init__(self, num_workers, fireplace, isTraining):
        self.num_workers = num_workers
        self.testEps = []
        self.generation = 0
        self.fireplace = fireplace
        self.IsTraining = isTraining
        self.rewards = {}

        self.trainingRandomMaxCount = 125

        self.bestRewardFuncCurrentGen = None # dict of current species with fitness weights
        self.RewardWeightMutationRate = 0.07
        self.RewardImportanceMutationRate = 0.02

        if self.IsTraining is True:
            self.fireplace.PreInitGameForRewardGen()
            # select reward funcs/modify one from best NN(per species) from prev gen
            if self.bestRewardFuncCurrentGen != None:
                self.rewards = self.SelectRewardImportance(self.bestRewardFuncCurrentGen)
            else:
                self.rewards = self.SelectRewardImportance(None)

    def InitForTesting(self, loadedNet=None, netConfig=None):
        if loadedNet is not None and netConfig is not None:
            net = neat.nn.RecurrentNetwork.create(loadedNet, netConfig)
            print(net)
            test = [(3, net)]
            results = self.SimulateState(test, Utils.BotType.MIDRANGE, True)
            Utils.WriteTestingStatsToFile(results)

    def SimulateState(self, nets, opponentType, loadedNet=False):
        data = []
        
        numGames = 501 # put to 501
        netNum = 0
        rf = self.rewards


        for genome, net in nets:
            step = 0
            if loadedNet is True:
                self.fireplace.InitGame(genome, opponentType)
            else:
                self.fireplace.InitGame(opponentType)
            genomeGameStats = {}          
            gameStats = {}
            #self.fireplace.currentStats = genomeGameStats

            netNum += 1 
            cumWins = 0
            cumLoss = 0
            numMaxActionDupes = 3
            numCurDupes = 0

            print("\nStarting new game for Net {}.\n".format(netNum))

            while step != numGames:              
                input = self.fireplace.testgame(self.fireplace.game)

                if input is not None:
                    #for i in input:
                    output = net.activate(input)
                    #print("OUTPUT\n")
                    s = sum(output)
                    norm = [float(x)/s for x in output]
                    #print(norm)
                    #print(output)

                    '''
                    outputs = action (play card, attack with minion/weapon/hero power, end turn)
                              target (self hero, enemy hero, minions (1-7))

                    '''
                    #chosenAction = self.fireplace.CheckFutureStates()

                    testd = self.fireplace.PerformAction(norm, 
                    self.fireplace.game)

                    # if attempting move when game is over force end
                    if testd == 0:                       
                        res = self.CheckIfGameEnded(self.fireplace)
                        if res is not None:                
                            '''step +=1
                            #genomeGameStats[step+1] = self.fireplace.currentGameStats
                            if res > 0:
                                cumWins += res
                            else:
                                cumLoss += res   '''    
                            continue                          
                    
                    # force end turn if turn errors
                    if testd == 1:
                        numCurDupes += 1
                    
                    if numCurDupes == numMaxActionDupes:
                        self.fireplace.ForceEndTurn(self.fireplace.game)
                        numCurDupes = 0                                  
                else:
                    # start new
                    res = self.CheckIfGameEnded(self.fireplace)
                    if res is not None:               
                        step +=1
                        genomeGameStats[step] = self.fireplace.currentGameStats
                        if res > 0:
                            cumWins += res
                        else:
                            cumLoss += res  
                        print("Starting New Game.\n")
                        if loadedNet is False:
                            self.StartNewGame(self.fireplace, opponentType)
                        else:
                            self.fireplace.InitGame(genome, opponentType)
                    #else:
            print("\nFinal Game Complete.")
            genomeGameStats[step] = self.fireplace.currentGameStats

            final = []
            #print(genomeGameStats.keys())
            #print(genomeGameStats)
            final.append(netNum)
            final.append(cumWins)
            final.append(cumLoss)
            final.append(rf)     
            final.append(genomeGameStats)
            data.append(final)           

        if len(data) > 0:
            return data
                            
    def CheckIfGameEnded(self, instance):
        endCheck = instance.GameEnded()
        
        if endCheck is not None:
            print("End Check: {}".format(endCheck))
            if endCheck == -1:
                print("LOSS")                      
                return -1                   
            elif endCheck == 1:
                print("WIN")            
                return 1
            elif endCheck == 0.5:
                print("DRAW")
                return 0.5
        else:
            print("Game In Progress.")
            return None

    def StartNewGame(self, fireplace, botType):
        fireplace.InitGame(botType)
    

    def EvalGenomes(self, genomes, config):
        self.generation += 1

        t0 = time.time()
        nets = []

        for gid, g in genomes:
            g.fitness = 0.0            
            nets.append((g, neat.nn.RecurrentNetwork.create(g, config)))
        
        print("network creation time {0}".format(time.time() - t0))
        t0 = time.time()

        opponentAI = Utils.BotType.AGGRO

        #if self.generation >= self.trainingRandomMaxCount:
            #opponentAI = Utils.BotType.MIDRANGE

        results = self.SimulateState(nets, opponentAI)
        
        # write stuff to files
        Utils.MakeNewGenDirectory(self.generation, True)

        if self.IsTraining:
            Utils.WriteFitnessFuncsToFile(results[0][3], self.generation)

            for i in range(len(nets)):
                g = nets[i][0]
                net = nets[i][1]

                netnum = results[i][0]
                cumWins = results[i][1]
                cumLoss = results[i][2]
                rewards = results[i][3]    
                gameStats = results[i][4]       
                print("Net: {}".format(netnum))
                print("Current Gen Fitness: {}".format(g.fitness))
                print("Gen Game Statistics:\n")
                print(self.generation)

                g.fitness = Fitness(self.generation, i, rewards, gameStats, float(cumWins), float(cumLoss))
                print("\nNew Fitness: {}".format(g.fitness))  
        
            Utils.WriteTrainingStatsToFile(results, self.generation, nets)

        #GetSpecies(self.stats)  

            

    def SelectRewardImportance(self, prevFuncs):

        if prevFuncs is None: # or species has worse fitness than prev
            results = {}
            deckStats = Utils.CalcEvaulationFunctionsFromDeck(self.fireplace)       
            weight = 0.0      

            evals  = Utils.CalcRewardImportance(deckStats)

            for i in range(1, 7):
                imp = Utils.Importance(evals[i-1]).name
                if imp == 'VERYHIGH':
                    weight = random.uniform(8,10)
                elif imp == 'HIGH':
                    weight = random.uniform(6,8)
                elif imp == 'MEDIUM':
                    weight = random.uniform(3, 6)
                elif imp == 'LOW':
                    weight = random.uniform(1,2)
                elif imp == 'VERYLOW':
                    weight = 0.01

                results[Utils.FitnessRewardType(i).name] = [imp, weight]

            print(results) 

            return results
        #else:
            # mutation? e.g. only change based on a randval
            #for i in range(1,7):
                #action = Utils.Importance(evals[i-1]).name 

    def InitialiseStats(self):
        statsObj = {}      
        return statsObj

def GetSpecies(stats):
    print(stats.get_species_sizes())
    print(stats.get_species_fitness())

def Fitness(genNum, indNum, rf, gameStats, cumWins, cumLoss):
    fit = 0.0
    compact = {'PLAYMINIONCARD': [],
             'PLAYSPELLCARD': [],
             'PLAYWEAPONCARD': [],
             'ATKMINTOMIN': [],
             'ATKHEROTOMIN': [],
             'ATKMINTOHERO': [],
             'ATKHEROTOHERO': [],
             'HEROPWR': [],
             'NUMTURNS': [],
             'BOARDADV': [],
             'ENEMYMINDEATHS': [],
             'SELFHERODMG': [],
             'ENEMYHERODMG': [],
             'MANASPENTPERTURN': [],
             'MANASPENTPERGAME': [],
             'MANAREMAININGPERTURN': []}
    weights = []

    for ind, tenGames in gameStats.items():
        print("getting stats from game: ", ind)
        compact['NUMTURNS'].append(len(tenGames))
        temp = {'PLAYMINIONCARD': [],
             'PLAYSPELLCARD': [],
             'PLAYWEAPONCARD': [],
             'ATKMINTOMIN': [],
             'ATKHEROTOMIN': [],
             'ATKMINTOHERO': [],
             'ATKHEROTOHERO': [],
             'HEROPWR': [],
             'BOARDADV': [],
             'ENEMYMINDEATHS': [],
             'SELFHERODMG': [],
             'ENEMYHERODMG': [],
             'MANASPENTPERTURN': [],
             'MANAREMAININGPERTURN': []}

        for turns in tenGames:          
            temp['PLAYMINIONCARD'].append(tenGames[turns]['PLAYMINIONCARD'])
            temp['PLAYSPELLCARD'].append(tenGames[turns]['PLAYSPELLCARD'])
            temp['PLAYWEAPONCARD'].append(tenGames[turns]['PLAYWEAPONCARD'])
            temp['ATKMINTOMIN'].append(tenGames[turns]['ATKMINTOMIN'])
            temp['ATKHEROTOMIN'].append(tenGames[turns]['ATKHEROTOMIN'])
            temp['ATKMINTOHERO'].append(tenGames[turns]['ATKMINTOHERO'])
            temp['ATKHEROTOHERO'].append(tenGames[turns]['ATKHEROTOHERO'])
            temp['HEROPWR'].append(tenGames[turns]['HEROPWR'])
            temp['BOARDADV'].append(tenGames[turns]['BOARDADV'])
            temp['ENEMYMINDEATHS'].append(tenGames[turns]['ENEMYMINDEATHS'])
            temp['SELFHERODMG'].append(tenGames[turns]['SELFHERODMG'])
            temp['ENEMYHERODMG'].append(tenGames[turns]['ENEMYHERODMG'])
            temp['MANASPENTPERTURN'].append(tenGames[turns]['MANASPENTPERTURN'])
            temp['MANAREMAININGPERTURN'].append(tenGames[turns]['MANAREMAININGPERTURN'])

        compact['PLAYMINIONCARD'].append(sum(temp['PLAYMINIONCARD']))
        compact['PLAYSPELLCARD'].append(sum(temp['PLAYSPELLCARD']))
        compact['PLAYWEAPONCARD'].append(sum(temp['PLAYWEAPONCARD']))
        compact['ATKMINTOMIN'].append(sum(temp['ATKMINTOMIN']))
        compact['ATKHEROTOMIN'].append(sum(temp['ATKHEROTOMIN']))
        compact['ATKMINTOHERO'].append(sum(temp['ATKMINTOHERO']))
        compact['ATKHEROTOHERO'].append(sum(temp['ATKHEROTOHERO']))
        compact['HEROPWR'].append(sum(temp['HEROPWR']))
        compact['BOARDADV'].append(sum(temp['BOARDADV']))
        compact['ENEMYMINDEATHS'].append(sum(temp['ENEMYMINDEATHS']))
        compact['SELFHERODMG'].append(sum(temp['SELFHERODMG']))
        compact['ENEMYHERODMG'].append(sum(temp['ENEMYHERODMG']))
        compact['MANASPENTPERTURN'].append(sum(temp['MANASPENTPERTURN']))
        compact['MANAREMAININGPERTURN'].append(sum(temp['MANAREMAININGPERTURN']))

        temp = {'PLAYMINIONCARD': [],
             'PLAYSPELLCARD': [],
             'PLAYWEAPONCARD': [],
             'ATKMINTOMIN': [],
             'ATKHEROTOMIN': [],
             'ATKMINTOHERO': [],
             'ATKHEROTOHERO': [],
             'HEROPWR': [],
             'BOARDADV': [],
             'ENEMYMINDEATHS': [],
             'SELFHERODMG': [],
             'ENEMYHERODMG': [],
             'MANASPENTPERTURN': [],
             'MANAREMAININGPERTURN': []}

    print(compact)

    weights.append(rf['ATKMINTOHERO'])
    weights.append(rf['ATKHEROTOHERO'])
    weights.append(rf['NUMTURNS'])
    weights.append(rf['BOARDCONTROL'])
    weights.append(rf['ATKMINTOMIN'])
    weights.append(rf['ATKHEROTOMIN'])

    fitStats = []
    fitStats.append(sum(compact['ATKMINTOHERO'])/30)
    fitStats.append(sum(compact['ATKHEROTOHERO'])/30)
    fitStats.append(sum(compact['NUMTURNS'])/30)
    fitStats.append(sum(compact['BOARDADV'])/30) # num of turns with board adv
    fitStats.append(sum(compact['ATKMINTOMIN'])/30)
    fitStats.append(sum(compact['ATKHEROTOMIN'])/30)

    print("averages: ", fitStats)

    #zscores = Utils.CalcZScore(stats)
    #print("\nzscores")
    #print(zscores)

    weighted = []
    weighted.append(weights[0][1]*fitStats[0])
    weighted.append(weights[1][1]*fitStats[1])
    weighted.append(weights[2][1]*fitStats[2])
    weighted.append(weights[3][1]*fitStats[3])
    weighted.append(weights[4][1]*fitStats[4])
    weighted.append(weights[5][1]*fitStats[5])
    #for i in range(len(stats)):
    #    var = zscores[i] * weights[i]
    #    weighted.append(var)

    print("\nweights")
    print(weights)
    print("\nweighted averages")
    print(weighted)

    fit = cumWins + cumLoss + weighted[0]+weighted[1]+weighted[3]+ weighted[4] + weighted[5] - weighted[2] 
    print(fit)
    compact['WINS'] = cumWins
    compact['LOSSES'] = cumLoss

    #Utils.WriteTrainingStatsToFile(compact, genNum, indNum, fit)
    #Utils.WriteCompactStatsToFile(compact, genNum, indNum, fit)

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
    #population.add_reporter(neat.Checkpointer(1))

    tester = None
    training = False
    arena = None
    
    if training:
        tester = neatArena.NeatArena(True)
        arena = Arena(1, tester, True)
        gen_best = population.run(arena.EvalGenomes, 50)
        SaveNetwork("Midrange", gen_best)
    else:
        tester = EvalChamber.EvalChamber()
        arena = Arena(1, tester, False)
        net = LoadNetwork()
        print(net)
        arena.InitForTesting(net, config)
    

def SaveNetwork(netName, network):
    with open(os.getcwd() + '\\Pickles\\' + netName + '.pickle', "wb") as f:
        pickle.dump(network, f)

def LoadNetwork():
    for fileName in os.listdir(os.getcwd() + '\\Pickles'):
        if fileName.endswith('.pickle'):
            path = os.getcwd() + '\\Pickles\\' + fileName
            with open(path, "rb") as f:
                net = pickle.load(f)
                return net


if __name__ == '__main__':
    run()
    


