import math
import random
from fireplace.utils import *
from fireplace.card import *
from operator import itemgetter
from fireplace.player import Player
from hearthstone.enums import CardClass, Race
from fireplace.card import Minion, Hero, Spell

class MidrangeScoreHunter(Player):

    # midrange
    
    #deck
    '''hunters mark        CS2_084 # 1
                        CS2_084
###########################################
    Alleycat          CFM_315 # 1
                        CFM_315

    Fiery Bat           OG_179 # 1
                        OG_179

    On the Hunt         OG_061 # 1
                        OG_061

    dire wolf alpha     EX1_162 # 2
                        EX1_162

    haunted creeper     FP1_002 # 2
                        FP1_002

    scavenging hyena    EX1_531
                        EX1_531 # 2

    Infested Wolf       OG_216 #3
                        OG_216

    unleash the hounds  EX1_538 #3
                        EX1_538

    kill command        EX1_539 # 3
                        EX1_539

    eaglehorn bow       EX1_536 #3
                        EX1_536
    
    animal companion    NEW1_031 # 3
                        NEW1_031

    King of Beasts         GVG_046 # 5
                        GVG_046

    Multi shot          DS1_183 # 4
                        DS1_183

    tundra rhino        DS1_178 #5
                        DS1_178

    savannah highmane   EX1_534 # 6
                        EX1_534'''
    
    

    def __init__(self, name, deck_id):
        self.heroID = 3
        self.AggroTallyMinimum = 6
        self.currentTurnCount = 0
        self.IsAggroing = False
        self.HasBoardAdv = False
        deck = []# same as nnet agent
        deck.append("EX1_534")
        deck.append("EX1_534")
        deck.append("CFM_315")
        deck.append("CFM_315")
        deck.append("OG_179")
        deck.append("OG_179")
        deck.append("OG_061")
        deck.append("OG_061")
        deck.append("EX1_162")
        deck.append("EX1_162")
        deck.append("FP1_002")
        deck.append("FP1_002")
        deck.append("EX1_531")
        deck.append("EX1_531")
        deck.append("OG_216")
        deck.append("OG_216")
        deck.append("EX1_539")
        deck.append("EX1_539")
        deck.append("EX1_538")
        deck.append("EX1_538")
        deck.append("EX1_536")
        deck.append("EX1_536")
        deck.append("NEW1_031")
        deck.append("NEW1_031")
        deck.append("GVG_046")
        deck.append("GVG_046")
        deck.append("DS1_183")
        deck.append("DS1_183")
        deck.append("DS1_178")
        deck.append("DS1_178")

        random.shuffle(deck)

        super().__init__(name,deck, CardClass(self.heroID).default_hero)

    def GetMulligan(self, mulligan):
        chosenCards = []

        for card in mulligan:
            if card.cost > 4:
                chosenCards.append(card)

        if len(chosenCards) == 0:
            return chosenCards
        else:
            return chosenCards

    def GetNextTurn(self, instance):
        p1 = instance.current_player
        p2 = p1.opponent
        self.UpdatePlaystyleSwitch(instance)

        return self.GetBestAction(instance, p1, p2)

    def UpdatePlaystyleSwitch(self, instance):
        # updates "playstyle (i.e. aggro/defensive") based on current board stats
        self.currentTurnCount += 1    
        p1 = instance.current_player
        p2 = p1.opponent   
        self.IsAggroing = False
        # board adv
        if len(p1.field) > len(p2.field):
            self.HasBoardAdv = True
        else:
            self.HasBoardAdv = False

        if self.currentTurnCount < self.AggroTallyMinimum:
            return

        totalDmg = 0
        manaLeft = p1.mana
        hasBeast = False

        for t in p1.field:
            totalDmg += t.atk
            if t.race == Race.BEAST:
                hasBeast = True
        for c in p1.hand:
            if c.cost <= manaLeft and c.is_playable() and c.type == CardType.SPELL and c.__str__() != "Multi-Shot":
                if c.__str__() == "On the Hunt":
                    totalDmg += 1
                elif c.__str__() == "Kill Command":
                    if hasBeast:
                        totalDmg += 5
                    else:
                        totalDmg += 3
        if p1.weapon is not None and p1.hero.can_attack():
            totalDmg += p1.weapon.damage
        if p1.hero.power.is_usable() and manaLeft >= 2:
            totalDmg += 2

        if p2.hero.health - totalDmg <= 0:
            self.IsAggroing = True

    def GetBestAction(self, instance, p1, p2):
        # score based on cards in hand and minions(both sides)
        return self.GetBestCard(instance, p1, p2)
        

    def GetBestCard(self, instance, p1, p2):
        # focus on board control, buffing hyena then becoming aggressive
        # spells = be efficient e.g. hunters mark on strong atk min or taunts
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
                    if len(p1.field) != 7:            
                        chosenCards.append(card)
                if card.type == CardType.SPELL:                
                    chosenCards.append(card)
                if card.type == CardType.WEAPON:
                    if p1.weapon is None:
                        chosenCards.append(card)

        if useCoin is True and len(chosenCards) != 0:
            return [2, coin, None]

        if len(chosenCards) == 0:
            if manaLeft >= 2 and p1.hero.power.is_usable():
                return [3, None, None] # hero power               
            elif p1.hero.can_attack():
                return self.GetValidTarget(p1, p1.hero.targets) # a valid targ
            elif len(p1.field) != 0:
                return self.GetBestAttack(instance, p1)
            else:
                return [4, None, None] # end turn
        else:
            # score based on cheap cost and strong stat
            # if dupes pick at random
            pruned = []
            chosenCard = None

            for i in range(len(chosenCards)):
                score = self.ScoreNextCardToPlay(p1, chosenCards[i])
                if chosenCards[i].type == CardType.MINION:
                    pruned.append([chosenCards[i], score])
                if chosenCards[i].type == CardType.SPELL: # just play spell if first pick
                    pruned.append([chosenCards[i], score])
                if chosenCards[i].type == CardType.WEAPON:
                    pruned.append([chosenCards[i], score])

            highestScore = 0
            pick = None

            if len(pruned) > 0:
                highestScore = max(pruned, key=itemgetter(1))[1]
                pick = max(pruned, key=itemgetter(1))[0]

            if highestScore > -100:
                print(highestScore)
                print(pick)
                chosenCard = pick
            elif highestScore <= -100:
                return [4, None, None]

            targs = None
            if chosenCard.requires_target():
                targs = self.GetValidTarget(p1, chosenCard.targets, chosenCard)

            return [2, chosenCard, targs]

    def GetValidTarget(self, p1, targets, source=None):
        if len(targets) > 0:
            valids = []
            for i in range(len(targets)):
                if targets[i].controller == p1.opponent:
                     valids.append(targets[i])

            if len(valids) > 0 and source is not None:
                return self.GetBestValidTarget(p1, valids, source)
            elif len(valids) > 0 and source is None:
                return self.GetBestValidTarget(p1, valids)

    def GetBestValidTarget(self, p1, targs, source=None):
        scores = []

        if isinstance(source, Hero):
            t = p1.hero.targets
            for targ in targs:
                if isinstance(targ, Hero):
                    if self.IsAggroing:
                        scores.append([1000, targ])
                    else:
                        scores.append([0, targ])
                if p1.hero.health - targ.atk <= 0:
                    continue
                else:
                    if targ.taunt:
                        scores.append([9999, targ])
                    else:
                        scores.append([p1.hero.health - targ.atk, targ])

        elif isinstance(source, Spell):
            dmg = 0

            if source.__str__() == "On the Hunt":
                dmg = 1
            elif source.__str__() == "Kill Command":
                if len(p1.field) == 0:
                    dmg = 3
                else:
                    dmg = 5

            for targ in targs:
                if isinstance(targ, Hero):         
                    if targ.health - dmg <= 0:
                        scores.append([1000, targ])
                    else:
                        scores.append([1, targ])
                else:
                    if targ.health - dmg <= 1:
                        scores.append([7, targ])
                    else:
                        if source.__str__() == "Multi-Shot":
                            if len(p1.opponent.field) <= 1:
                                scores.append([1, targ])
                            else:
                                scores.append([6, targ])        
                        scores.append([6, targ])

                if source.__str__() == "Hunter's Mark":
                    huntersMarkScore = -1
                    if isinstance(targ, Minion):
                        if targ.health == 1:
                            huntersMarkScore -= 1000
                        else:
                            if targ.atk >= 4: 
                                huntersMarkScore += 3 + targ.atk - targ.health
                            elif targ.taunt:
                                huntersMarkScore += 100
                            else:
                                huntersMarkScore += 2
                    scores.append[huntersMarkScore, targ]

        if len(scores) == 0:
            return [4, None, None]

        choice = max(scores, key=itemgetter(0))[0]
        if choice < 0:
            return [4, None, None]
        targ = max(scores, key=itemgetter(0))[1]
        return targ


    def GetBestAttack(self, instance, p1):
        # "defensive" until hyena is out then become minion aggressive to buff
        # then become hero aggressive
        if len(p1.field) == 0:
            return None

        minionAtkTargs = []
        scores = []
        temp = []
        totalBoardDmg = 0
        oppHealth = p1.opponent.hero.health
        hyenaActive = False


        for minion in p1.field:           
            if minion.can_attack():
                temp.append(minion)
                totalBoardDmg += minion.atk
            if minion.__str__() == "Scavenging Hyena":
                hyenaActive = True
        
        for minion in temp:
            targs = minion.attack_targets
            minDmg = minion.atk
            minHealth = minion.health

            for t in targs:
                curScore = -5
                tHealth = t.health
                tDmg = t.atk

                if isinstance(t, Hero):
                    if self.IsAggroing:
                        curScore += 1000
                    # if board adv do that first
                    else:
                        curScore = 0                

                if minDmg == tHealth:
                    if self.IsAggroing:
                        curScore += 1                   
                    else:
                        curScore += 3
                if tDmg >= minHealth:
                    if self.IsAggroing is False:
                        curScore += 2
                    else:
                        curScore += -2

                if minion.__str__() != "Scavenging Hyena" and hyenaActive and minion.race == Race.BEAST and totalBoardDmg >= tHealth:
                    curScore += 5

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
        #if atk < 0:
            #return [4, None, None]

        source = max(scores, key=itemgetter(0))[2]
        print(source)
        return [1, source, atk]
                    
    def ScoreNextCardToPlay(self, p1, card):
        # score cards based on "utility" e.g tundra rhino if non attacked mins on board
        cardScore = 0
        field = p1.field
        oppField = p1.opponent.field

        exhaustedBeasts = False
        hasBeasts = False
        hasHyena = False
        beastNum = 0

        for minion in field:
            if minion.__str__() == "Scavenging Hyena":
                hasHyena = True
            if minion.race == Race.BEAST:
                beastNum += 1
                hasBeasts = True
                if minion.num_attacks == 0:
                    exhaustedBeasts = True
        # minimum value for selection
        if self.HasBoardAdv:
            cardScore += 1
        else:
            cardScore += 5

        if card.type == CardType.MINION:
            if len(field) >= 7:
                return -100
                
            cardScore = (cardScore + card.atk) * 1.2
            if hasHyena:
                cardScore += 2

            if card.has_deathrattle:
                cardScore += 1

            # card specific
            if card.__str__() == "Dire Wolf Alpha":
                if len(field) == 0 or hasBeasts is False:
                    cardScore -= 10
            elif card.__str__() == "Tundra Rhino":
                if len(field) == 0 or exhaustedBeasts is False:
                    cardScore -= 10
            elif card.__str__() == "King of Beasts":
                if len(field) == 0 or hasBeasts is False:
                    cardScore -= 10
                else:
                    if 1 < beastNum >= 3:
                        cardScore += 5
                    else:
                        cardScore += 10 
            elif card.__str__() == "Scavenging Hyena":
                if self.HasBoardAdv is not True:
                    if hasHyena:
                        cardScore -= 3
                    else:
                        cardScore -= 1

        if card.type == CardType.SPELL:
            if card.__str__() == "Hunter's Mark":
                if len(oppField) == 0:
                    return -100
                else:
                    cardScore += len(oppField)
            
            elif card.__str__() == "On the Hunt":
                if len(oppField) == 0 or len(field) >= 7:
                    cardScore -= 10
                else:
                    cardScore += 6
            
            elif card.__str__() == "Unleash the Hounds":
                if len(oppField) == 0 or len(field) >= 7:
                    return -100
                else:
                    cardScore += len(oppField) - len(field)
            
            elif card.__str__() == "Multi-Shot":
                if len(oppField) == 0:
                    return -100
                else:
                    cardScore += len(oppField) - 5

            elif card.__str__() == "Kill Command":
                if hasBeasts:
                    cardScore += 4
                    if len(oppField) == 0:
                        cardScore -= 6
                    elif p1.opponent.hero.health <= 5:
                        cardScore += 100
            
            elif card.__str__() == "Animal Companion":
                if len(field) >= 7:
                    return -100
                
                if self.HasBoardAdv is not True:
                    cardScore += 5

        if card.type == CardType.WEAPON:
            if p1.weapon is not None:
                return -100
            else:
                cardScore += 3

        return cardScore
        



        
        


