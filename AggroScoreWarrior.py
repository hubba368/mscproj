import math
import random
from fireplace.utils import *
from fireplace.card import *
from operator import itemgetter
from fireplace.player import Player
from hearthstone.enums import CardClass
from fireplace.card import Minion, Hero

class AggroScoreWarrior(Player):

    # greedy aggro class to train against
    def __init__(self, name, deck_id):
        deck = []# same as nnet agent
        self.heroID = 10
        # class - 15
        # upgrade - 0
        deck.append('EX1_409')
        deck.append('EX1_409')
        # heroic strike - 2
        deck.append('CS2_105')
        deck.append('CS2_105')
        # kings defender - 3
        deck.append('AT_065')
        deck.append('AT_065')
        # frothing beserker - 3
        deck.append('EX1_604')
        deck.append('EX1_604')
        # arathi weaponsmith - 4
        deck.append('EX1_398')
        # mortal strike - 4
        deck.append('EX1_408')
        deck.append('EX1_408')
        # axe flinger - 4
        deck.append('BRM_016')
        deck.append('BRM_016')
        # tentacles for arms - 5
        deck.append('OG_033')
        deck.append('OG_033')

        # neutral - 15
        # southsea deckhand - 1
        deck.append('CS2_146')
        deck.append('CS2_146')
        # leper gnome - 1
        deck.append('EX1_029')
        deck.append('EX1_029')
        # elven archer - 1
        deck.append('CS2_189')
        deck.append('CS2_189')
        # bloodsail raider - 2
        deck.append('NEW1_018')
        deck.append('NEW1_018')
        # direwolf alpha - 2 	
        deck.append('EX1_162')
        deck.append('EX1_162')
        # harvest golem - 3
        deck.append('EX1_556')
        deck.append('EX1_556')
        # dread corsair - 4
        deck.append('NEW1_022')
        deck.append('NEW1_022')
        # leeroy jenkins
        deck.append('EX1_116')

        random.shuffle(deck)

        super().__init__(name,deck, CardClass(self.heroID).default_hero)

    def GetNextTurn(self, instance):
        p1 = instance.current_player
        p2 = p1.opponent

        return self.GetBestAction(instance, p1)

    def GetBestAction(self, instance, p1):
        return self.GetBestCard(instance, p1)
        
    def GetMulligan(self, mulligan):
        chosenCards = []

        for card in mulligan:
            if card.cost > 3:
                chosenCards.append(card)

        if len(chosenCards) == 0:
            return chosenCards
        else:
            return chosenCards


    def GetBestCard(self, instance, p1):
        # choose cheapest + strongest min
        # spells = attack random valid (e.g. enemy side only) targets
        manaLeft = p1.mana
        chosenCards = []
        useCoin = False
        coin = None

        for card in p1.hand:         
            if card.id == "GAME_005":
                manaLeft += 1
                useCoin = True
                coin = card

        for card in p1.hand:
            if card.cost <= manaLeft and card.is_playable():
                if card.type == CardType.MINION:              
                    chosenCards.append([card, card.cost])
                if card.type == CardType.SPELL:                
                    chosenCards.append([card, card.cost])
                if card.type == CardType.WEAPON:
                    if p1.weapon is None:
                        chosenCards.append([card, card.cost])

        if useCoin is True and len(chosenCards) != 0:
            return [2, coin, None]

        if len(chosenCards) == 0:
            if manaLeft >= 2 and p1.hero.power.is_usable():
                return [3, None, None] # hero power               
            elif p1.hero.can_attack():
                print(p1.hero.targets)
                return [5, None, self.GetValidTarget(p1, p1.hero.targets)] # a valid targ
            elif len(p1.field) != 0:
                return self.GetBestMinionAttack(instance, p1)
            else:
                    return [4, None, None] # end turn
        else:
            # score based on cheap cost and strong stat
            # if dupes pick at random
            pick = min(x[1] for x in chosenCards)
            pruned = []
            spells = []
            weapons = []
            chosenCard = None
            print(pick)

            for i in range(len(chosenCards)):
                if chosenCards[i][1] == pick:
                    if chosenCards[i][0].type == CardType.MINION:
                        pruned.append([chosenCards[i][0], chosenCards[i][0].atk])
                    if chosenCards[i][0].type == CardType.SPELL: # just play spell if first pick
                        spells.append(chosenCards[i][0])
                    if chosenCards[i][0].type == CardType.WEAPON:
                        weapons.append(chosenCards[i][0])

            if len(pruned) > 1:
                pick = max(x[1] for x in pruned)
                for i in range(len(pruned)):
                    if pruned[i][1] == pick: # just pick first with highest atk even if dupe
                        chosenCard = pruned[i][0]
            elif len(pruned) == 1:
                chosenCard = pruned[0][0]

            if len(pruned) == 0:
                if len(spells) > 0:
                    # play spells
                    chosenCard = spells[0]
                elif len(weapons) > 0:
                    # play weapon
                    chosenCard = weapons[0]
            

            targs = None
            if chosenCard.requires_target():
                targs = self.GetValidTarget(p1, chosenCard.targets)

            return [2, chosenCard, targs]

    def GetValidTarget(self, p1, targets):
        if len(targets) > 0:
            valids = []
            for i in range(len(targets)):
                if targets[i].controller == p1.opponent:
                     valids.append(targets[i])

            if len(valids) > 0:
                return random.choice(valids)
            

    def GetBestMinionAttack(self, instance, p1):
        # efficient trade (e.g. 1/2 killing a 5/1)
        # then focus hero
        if len(p1.field) == 0:
            return None

        minionAtkTargs = []
        scores = []
        temp = []
        print(p1.field)
        for minion in p1.field:
            
            if minion.can_attack():
                temp.append(minion)
        
        for minion in temp:
            print(minion)
            targs = minion.attack_targets
            minDmg = minion.atk
            minHealth = minion.health

            for t in targs:
                curScore = -5
                tHealth = t.health
                tDmg = t.atk

                if isinstance(t, Hero):
                    curScore += 1000
                    # if board adv do that first
                    if len(p1.field) < len(p1.opponent.field):
                        curScore -= 1000                 

                if minDmg == tHealth:
                    curScore += 5
                if tDmg >= minHealth:
                    curScore += -2

                if isinstance(t, Minion):
                    if t.taunt:
                        curScore += 9999
                    elif t.has_deathrattle:
                        curScore += -2
                    elif t.has_inspire:
                        curScore += 1
                  
            scores.append([curScore, t, minion])

        if len(scores) == 0:
            return [4,None,None]

        atk = max(scores, key=itemgetter(0))[1]
        source = max(scores, key=itemgetter(0))[2]
        return [1, minion, atk]