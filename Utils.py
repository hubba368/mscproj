import math
from enum import Enum
import struct
import copy
import csv
import os
from hearthstone.enums import CardType
from operator import itemgetter
import AggroScoreWarrior
from collections import defaultdict
import MidrangeScoreHunter

class StatType(Enum):
    PLAYMINIONCARD = 1
    PLAYSPELLCARD = 2
    PLAYWEAPONCARD = 3
    ATKMINTOMIN = 4
    ATKHEROTOMIN = 5
    ATKMINTOHERO = 6
    ATKHEROTOHERO = 7
    HEROPWR = 8
    NUMTURNS = 9
    BOARDADV = 10
    ENEMYMINDEATHS = 11
    SELFHERODMG = 12
    ENEMYHERODMG = 13
    MANASPENTPERTURN = 14
    MANASPENTPERGAME = 15
    MANAREMAININGPERTURN = 16

class FitnessRewardType(Enum):
    ATKMINTOHERO = 1
    ATKHEROTOHERO = 2
    NUMTURNS = 3
    BOARDCONTROL = 4 # num of mins - num of enemy mins per turn avg?
    ATKMINTOMIN = 5
    ATKHEROTOMIN = 6


class Importance(Enum):
    VERYHIGH = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    VERYLOW = 5

class BotType(Enum):
    RANDOM = 1
    AGGRO = 2
    MIDRANGE = 3
    AGGRONEAT = 4
    MIDRANGENEAT = 5


def AddToStats(values, key):
    score = 0.0
    score = values

    return score

# returns a byte string of the array (game state)
def ArrayToString(array):
    string = ""
    temp = []

    for i in array:
        for j in i:
            temp.append(bytes(struct.pack("f", j)))
    for i in temp:
        string += str(i)
    return string

# parameter estimation
# take the average from previous best gen and compare

def GetOpponent(botType):
    if(botType == BotType.RANDOM):
        return None
    elif(botType == BotType.AGGRO):
        bot = AggroScoreWarrior.AggroScoreWarrior("AggroBot", 10)
        return bot
    elif(botType == BotType.MIDRANGE):
        bot = MidrangeScoreHunter.MidrangeScoreHunter("MidrangeBot", 7)
        return bot


def CalcEvaulationFunctionsFromDeck(gameInstance):
    p1d = gameInstance.player1Deck
    p1h = gameInstance.players[0].hand

    avgCardCostSum = []
    avgTotalDmgSum = []
    minionWithKeywordSum = {"DivineShield":0,"taunt":0,"deathrattle":0,
                            "battlecry":0,"combo":0,"inspire":0}
    minionSum = 0
    spellSum = 0
    weaponSum = 0

    for i in range(len(p1d)):
        card = p1d[i]

        if card.type == 4:
            minionSum+=1
            avgTotalDmgSum.append(card.atk)
            # get keyworded cards
            if card.divine_shield:
                minionWithKeywordSum["DivineShield"] += 1

            if card.has_deathrattle:
               minionWithKeywordSum["deathrattle"] += 1
                
            if card.taunt:
                minionWithKeywordSum["taunt"] += 1
                
            if card.has_battlecry:
                minionWithKeywordSum["battlecry"] += 1

            if card.has_combo: 
                minionWithKeywordSum["combo"] += 1

            if card.has_inspire:
                minionWithKeywordSum["inspire"] += 1

        elif card.type == 5:
            spellSum+=1
        elif card.type == 7:
            weaponSum+=1
            if card.atk > 0:
                avgTotalDmgSum.append(card.atk)

        avgCardCostSum.append(card.cost)

    # check hand cos cards are removed from deck
    if len(p1h) > 0:
        for card in p1h:
            if card.type == 4:
                minionSum+=1
                avgTotalDmgSum.append(card.atk)
                if card.divine_shield:
                    minionWithKeywordSum["DivineShield"] += 1
                if card.has_deathrattle:
                    minionWithKeywordSum["deathrattle"] += 1          
                if card.taunt:
                    minionWithKeywordSum["taunt"] += 1              
                if card.has_battlecry:
                    minionWithKeywordSum["battlecry"] += 1
                if card.has_combo: 
                    minionWithKeywordSum["combo"] += 1
                if card.has_inspire:
                    minionWithKeywordSum["inspire"] += 1

            elif card.type == 5:
                spellSum+=1
            elif card.type == 7:
                weaponSum+=1
                if card.atk > 0:
                    avgTotalDmgSum.append(card.atk)

            avgCardCostSum.append(card.cost)

    avgCardCostSum = sum(avgCardCostSum) / 30
    avgTotalDmgSum = sum(avgTotalDmgSum) / len(avgTotalDmgSum)

    print(avgCardCostSum)
    print(avgTotalDmgSum)
    print(minionSum)
    print(spellSum)
    print(weaponSum)
    print(minionWithKeywordSum)

    return avgCardCostSum, avgTotalDmgSum, minionSum, spellSum, weaponSum, minionWithKeywordSum
        

def CalcRewardImportance(stats):
    avgCost = stats[0]
    avgDmg = stats[1]
    totalMins = stats[2]
    totalSpells = stats[3]
    weaponSum = stats[4]
    minionWithKeywordSum = stats[5]

    SmhWeight = 5
    ShhWeight = 5
    SmmWeight = 5
    ShmWeight = 5
    BoardAdv = 5
    Turns = 5
    results = []

    if avgCost < 3:
        # probably aggro focused
        Turns -= 4
        SmhWeight -= 3
        BoardAdv -= 1
        # high weapons 
        if weaponSum > 2:
            ShhWeight -= 3
            ShmWeight -= 2

        if (abs(totalMins) - abs(totalSpells)) >= 10:
            # probs minion heavy/zoo type 
            SmhWeight -= 1
            ShhWeight -= 1
            BoardAdv -= 1
            SmmWeight -= 1
            
            
        results.append(SmhWeight) #1
        results.append(ShhWeight) #1
        results.append(Turns) #1
        results.append(BoardAdv) #3
        results.append(SmmWeight) #4
        results.append(ShmWeight) #4

    elif avgCost >= 3:
        # probs midrange
        Turns -= 3
        SmhWeight -= 1
        SmmWeight -= 1
        BoardAdv -= 3
        # high weapons 
        if weaponSum >= 2:
            ShhWeight -= 2
            ShmWeight -= 3

        if (abs(totalMins) - abs(totalSpells)) >= 10:
            # minion heavy/zoo type 
            SmhWeight -= 2
            ShhWeight -= 1
            SmmWeight -= 1
        
        elif (abs(totalMins) - abs(totalSpells)) < 10:
            # probs more focus on spell use to clear
            SmhWeight -= 1
            BoardAdv -= 1
            ShmWeight -= 1
            
            
        results.append(SmhWeight) #1
        results.append(ShhWeight) #1
        results.append(Turns) #1
        results.append(BoardAdv) #3
        results.append(SmmWeight) #4
        results.append(ShmWeight) #4        

    #else:
        # probs control

    return results

def MakeNewGenDirectory(genNum, training):
    parentDir = ""
    dirName = ""
    if training:
        parentDir = "C:/Users/Elliott/Desktop/msc project/projectdir/Training/"
        dirName = "Generation " + str(genNum)
    else:
        parentDir = "C:/Users/Elliott/Desktop/msc project/projectdir/Testing/"
        dirName = "AggroNEAT"

    path = os.path.join(parentDir, dirName)
    os.mkdir(path)

def WriteTrainingStatsToFile(stats, genNum, nets):
    parentDir = "C:/Users/Elliott/Desktop/msc project/projectdir/Training/"
    #dirName = "Generation " + str(genNum)
    
    index = 1
    temp = []
    worstFit = 0
    bestFit = 0
    avgFit = 0
    worstWR = 0
    bestWR = 0
    avgWR = 0
    keys = ["Gen Num", "Worst Fitness", "Best Fitness", "Average Fitness", "Worst WR", "Best WR", "Average WR"]
    data = []

    for net in nets:
        temp.append([index, net[0].fitness])
        index+=1
        avgFit += net[0].fitness

    worstFit = min(temp, key=itemgetter(1))[1]
    bestFit = max(temp, key=itemgetter(1))[1]
    avgFit = avgFit / len(nets)

    temp = []
    index = 1
    for s in stats:
        if s[1] != 0:
            wins = s[1] / 30
            temp.append([index, wins])
            avgWR += wins
        index+=1
    
    worstWR = min(temp, key=itemgetter(1))[1]
    bestWR = max(temp, key=itemgetter(1))[1]   
    avgWR = avgWR / 50

    data.append(genNum) 
    data.append(worstFit) 
    data.append(bestFit)
    data.append(avgFit) 
    data.append(worstWR) 
    data.append(bestWR)
    data.append(avgWR)

    path = os.path.join(parentDir, "CompactTrainingStats.csv")
    mode = "w"
    if os.path.exists(path) is True:
        mode = "a"

    with open(path, mode, encoding='UTF8', newline='') as file:
        writer = csv.writer(file)

        if mode == "w":
            writer.writerow(keys)
            writer.writerow(data)
        else:
            writer.writerow(data)


def WriteTestingStatsToFile(stats):   
    target = "Midrange"
    keys = ["Turn Num", "Minions Played", "Spells Played", "Weapons Played", "Min to Hero atk", "Hero to Hero atk", 
            "Min to Min atk", "Hero to Min atk", "Hero Power Used", "Has Board Control", "Enemy Min Deaths", "Self Dmg", "Enemy Hero Dmg",
            "Mana Spent", "Mana Remaining"]
    avgKeys = ["Minions Played", "Spells Played", "Weapons Played", "Min to Hero atk", "Hero to Hero atk", 
            "Min to Min atk", "Hero to Min atk", "Hero Power Used", "Has Board Control", "Enemy Min Deaths", "Self Dmg", "Enemy Hero Dmg",
            "Mana Spent", "Mana Remaining", "target"]

    parentDir = "C:/Users/Elliott/Desktop/msc project/projectdir/Testing/"
    path = os.path.join(parentDir, "MidrangeNEAT/")
    mode = "w"

    if os.path.exists(path+"MidrangeNEATMid.csv") is True:
        mode = "a"

    if os.path.exists(path) is False:
        print(path)
        print("directory not there")
        os.mkdir(path)


    avg = {'PLAYMINIONCARD': [],
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


    data = []
    rawGames = defaultdict(list)
    avg = defaultdict(list)

    gs = stats[0][4]

    wins = stats[0][1]
    loss = stats[0][2]
    for ind, games in gs.items():

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
             'MANASPENTPERGAME': [],
             'MANAREMAININGPERTURN': []}      
        #data['GAMENUM'].append(ind)        
        for turns in games:
            
            data = []
            data.append(turns)
            data.append(games[turns]['PLAYMINIONCARD'])
            data.append(games[turns]['PLAYSPELLCARD'])
            data.append(games[turns]['PLAYWEAPONCARD'])
            data.append(games[turns]['ATKMINTOHERO'])
            data.append(games[turns]['ATKHEROTOHERO'])
            data.append(games[turns]['ATKMINTOMIN'])
            data.append(games[turns]['ATKHEROTOMIN'])
            data.append(games[turns]['HEROPWR'])
            data.append(games[turns]['BOARDADV'])
            data.append(games[turns]['ENEMYMINDEATHS'])
            data.append(games[turns]['SELFHERODMG'])
            data.append(games[turns]['ENEMYHERODMG'])
            data.append(games[turns]['MANASPENTPERTURN'])
            data.append(games[turns]['MANASPENTPERGAME'])
            data.append(games[turns]['MANAREMAININGPERTURN'])
            rawGames[ind].append(data)
            #

            temp['PLAYMINIONCARD'].append(games[turns]['PLAYMINIONCARD'])
            temp['PLAYSPELLCARD'].append(games[turns]['PLAYSPELLCARD'])
            temp['PLAYWEAPONCARD'].append(games[turns]['PLAYWEAPONCARD'])
            temp['ATKMINTOHERO'].append(games[turns]['ATKMINTOHERO'])
            temp['ATKHEROTOHERO'].append(games[turns]['ATKHEROTOHERO'])
            temp['ATKMINTOMIN'].append(games[turns]['ATKMINTOMIN'])
            temp['ATKHEROTOMIN'].append(games[turns]['ATKHEROTOMIN'])
            temp['HEROPWR'].append(games[turns]['HEROPWR'])
            temp['BOARDADV'].append(games[turns]['BOARDADV'])
            temp['ENEMYMINDEATHS'].append(games[turns]['ENEMYMINDEATHS'])
            temp['SELFHERODMG'].append(games[turns]['SELFHERODMG'])
            temp['ENEMYHERODMG'].append(games[turns]['ENEMYHERODMG'])
            temp['MANASPENTPERTURN'].append(games[turns]['MANASPENTPERTURN'])
            temp['MANASPENTPERGAME'].append(games[turns]['MANASPENTPERGAME'])
            temp['MANAREMAININGPERTURN'].append(games[turns]['MANAREMAININGPERTURN'])
        
        mins = (sum(temp['PLAYMINIONCARD']) / len(temp['PLAYMINIONCARD'])) if len(temp['PLAYMINIONCARD']) != 0 else 0
        spl = (sum(temp['PLAYSPELLCARD'])/ len(temp['PLAYSPELLCARD'])) if len(temp['PLAYSPELLCARD']) != 0 else 0
        wep = (sum(temp['PLAYWEAPONCARD'])/ len(temp['PLAYWEAPONCARD'])) if len(temp['PLAYWEAPONCARD']) != 0 else 0
        m2m = (sum(temp['ATKMINTOMIN'])/ len(temp['ATKMINTOMIN'])) if len(temp['ATKMINTOMIN']) != 0 else 0
        h2m = (sum(temp['ATKHEROTOMIN'])/ len(temp['ATKHEROTOMIN'])) if len(temp['ATKHEROTOMIN']) != 0 else 0
        m2h = (sum(temp['ATKMINTOHERO'])/ len(temp['ATKMINTOHERO'])) if len(temp['ATKMINTOHERO']) != 0 else 0
        h2h = (sum(temp['ATKHEROTOHERO'])/ len(temp['ATKHEROTOHERO'])) if len(temp['ATKHEROTOHERO']) != 0 else 0
        pwr = (sum(temp['HEROPWR'])/ len(temp['HEROPWR'])) if len(temp['HEROPWR']) != 0 else 0
        ba = (sum(temp['BOARDADV'])/ len(temp['BOARDADV'])) if len(temp['BOARDADV']) != 0 else 0
        emd = (sum(temp['ENEMYMINDEATHS'])/ len(temp['ENEMYMINDEATHS'])) if len(temp['ENEMYMINDEATHS']) != 0 else 0
        shd = (sum(temp['SELFHERODMG'])/ len(temp['SELFHERODMG'])) if len(temp['SELFHERODMG']) != 0 else 0
        ehd = (sum(temp['ENEMYHERODMG'])/ len(temp['ENEMYHERODMG'])) if len(temp['ENEMYHERODMG']) != 0 else 0
        ms = (sum(temp['MANASPENTPERTURN'])/ len(temp['MANASPENTPERTURN'])) if len(temp['MANASPENTPERTURN']) != 0 else 0
        mr = (sum(temp['MANAREMAININGPERTURN'])/ len(temp['MANAREMAININGPERTURN'])) if len(temp['MANAREMAININGPERTURN']) != 0 else 0

        avg[ind].append(mins)
        avg[ind].append(spl)
        avg[ind].append(wep)
        avg[ind].append(m2h)
        avg[ind].append(h2h)
        avg[ind].append(m2m)
        avg[ind].append(h2m)
        avg[ind].append(pwr)
        avg[ind].append(ba)
        avg[ind].append(emd)
        avg[ind].append(shd)
        avg[ind].append(ehd)
        avg[ind].append(ms)
        avg[ind].append(mr) 
        avg[ind].append(target)

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
             'MANASPENTPERGAME': [],
             'MANAREMAININGPERTURN': []}

        
        data = []


    # per turn
    with open(path+"MidrangeNEATMid.csv", mode, encoding='UTF8', newline='') as file:
        writer = csv.writer(file)

        if mode == "w":
            writer.writerow(keys)
            
            for game, turns in rawGames.items():
                #print(game)
                
                for turn in turns:
                    #print(turn)
                    
                    writer.writerow(turn)
        else:
            writer.writerow(data)    


    # averaged
    with open(path+"MidrangeNEATMidAvg.csv", mode, encoding='UTF8', newline='') as file:
        writer = csv.writer(file)

        if mode == "w":
            writer.writerow(avgKeys)
            for game, stats in avg.items():
                
                writer.writerow(stats)

    with open(path+"MidrangeNEATMidWR.csv", mode, encoding='UTF8', newline='') as file:
        writer = csv.writer(file)
        key = ["Wins","Losses"]
        d = []
        d.append(wins)
        d.append(loss)
        if mode == "w":
            writer.writerow(key)
            writer.writerow(d)           
                    
        else:
            writer.writerow(data)  
    '''for i in range(len(nets)):
        fileName = "Stats-Ind" + str(genNum)
        p = path2 + fileName
        file = open(p,"w")
        file.write(fileName + " All Stats (averaged where noted)")
        file.write("Fitness -- " + str(fitness) + "\n")
        file.write("Wins -- " + str(stats['WINS'])+"\n")
        file.write("Losses -- " +str(stats['LOSSES'])+"\n")

        file.write("Total Minions Played\n")
        for i in range(len(stats['PLAYMINIONCARD'])):
            file.write("Game " + str(i+1) + ": %s\n" % stats['PLAYMINIONCARD'][i])
        file.write("Total Spells Played\n")
        for i in range(len(stats['PLAYSPELLCARD'])):
            file.write("Game " + str(i) + ": %s\n" % stats['PLAYSPELLCARD'][i])
        file.write("Total Weapons Played\n")
        for i in range(len(stats['PLAYWEAPONCARD'])):
            file.write("Game " + str(i) + ": %s\n" % stats['PLAYWEAPONCARD'][i])
        file.write("Total Minion->Minion Attacks\n")
        for i in range(len(stats['ATKMINTOMIN'])):
            file.write("Game " + str(i) + ": %s\n" % stats['ATKMINTOMIN'][i])
        file.write("Total Hero->Minion Attacks\n")
        for i in range(len(stats['ATKHEROTOMIN'])):
            file.write("Game " + str(i) + ": %s\n" % stats['ATKHEROTOMIN'][i])
        file.write("Total Minion->Hero Attacks\n")
        for i in range(len(stats['ATKMINTOHERO'])):
            file.write("Game " + str(i) + ": %s\n" % stats['ATKMINTOHERO'][i])
        file.write("Total Hero->Hero Attacks\n")
        for i in range(len(stats['ATKHEROTOHERO'])):
            file.write("Game " + str(i) + ": %s\n" % stats['ATKHEROTOHERO'][i])

        file.close()'''


def WriteCompactStatsToFile(stats, genNum, indNum, fitness):
    keys = stats.keys()
    parentDir = "C:/Users/Elliott/Desktop/msc project/projectdir/Training/"
    dirName = "Generation " + str(genNum)
    path = os.path.join(parentDir, dirName)

    with open(path +"/"+ "CompactStatsInd"+str(indNum+1)+".csv", "w") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(keys)
        
        for key in keys:
            writer.writerow([stats[key]])

def WriteFitnessFuncsToFile(funcs, genNum):
    parentDir = "C:/Users/Elliott/Desktop/msc project/projectdir/Training/"
    dirName = "Generation " + str(genNum)
    path = os.path.join(parentDir, dirName)

    file = open(path + "/" + "FitnessFuncs.txt","w")
    print(funcs)
    file.write(dirName + " Fitness Funcs By Generation (Importance/Weight)")
    file.write("\nMinion to Hero Atks (avg of total per game)")
    file.write(funcs['ATKMINTOHERO'][0])
    file.write(str(funcs['ATKMINTOHERO'][1]))
    file.write("\n\Hero to Hero Atks (avg of total per game)")
    file.write(funcs['ATKHEROTOHERO'][0])
    file.write(str(funcs['ATKHEROTOHERO'][1]))
    file.write("\nNumber of turns (avg of total per game)")
    file.write(funcs['NUMTURNS'][0])
    file.write(str(funcs['NUMTURNS'][1]))
    file.write("\nBoard Advantage (avg of total times p1 board greater than p2 board)")
    file.write(funcs['BOARDCONTROL'][0])
    file.write(str(funcs['BOARDCONTROL'][1]))
    file.write("\nMinion to Minion Atks (avg of total per game)")
    file.write(funcs['ATKMINTOMIN'][0])
    file.write(str(funcs['ATKMINTOMIN'][1]))
    file.write("\nHero to Minion Atks (avg of total per game)")
    file.write(funcs['ATKHEROTOMIN'][0])
    file.write(str(funcs['ATKHEROTOMIN'][1]))

    file.close()



def CalcZScore(values):
    mean = sum(values) / len(values)
    diff = [(i - mean)**2 for i in values]
    sumdiff = sum(diff)
    stdev = (sumdiff / (len(values)-1)) ** 0.5

    zscores = [(i - mean) / stdev for i in values]
    return zscores

