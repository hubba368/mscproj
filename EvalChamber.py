import random
import Utils
import copy


from fireplace import cards
from fireplace.exceptions import GameOver, InvalidAction
from fireplace.game import Game
from fireplace.player import Player
from fireplace.utils import random_draft
from fireplace.deck import Deck
from fireplace.utils import play_turn

from hearthstone.enums import CardClass, CardSet, CardType, State

# same as neatArena just with no evo

class EvalChamber():

    def __init__(self):
        self.game = None
        self.players = ['', '']
        self.aggroDeck = []
        self.midrangeDeck = []
        self.AIBot = None

        self.currentGameStats = None
        self.currentTurnStats = None
        self.prevSelfHeroDmg = 0
        self.currentSelfHeroDmg = 0
        self.prevEnemyHeroDmg = 0
        self.currentEnemyHeroDmg = 0
        self.numTurns = 1
        self.currentTurn = 1
        cards.db.initialize()
        
        ### Decks
        d1 = []
        # class - 15
        # upgrade - 0
        d1.append('EX1_409')
        d1.append('EX1_409')
        # heroic strike - 2
        d1.append('CS2_105')
        d1.append('CS2_105')
        # kings defender - 3
        d1.append('AT_065')
        d1.append('AT_065')
        # frothing beserker - 3
        d1.append('EX1_604')
        d1.append('EX1_604')
        # arathi weaponsmith - 4
        d1.append('EX1_398')
        # mortal strike - 4
        d1.append('EX1_408')
        d1.append('EX1_408')
        # axe flinger - 4
        d1.append('BRM_016')
        d1.append('BRM_016')
        # tentacles for arms - 5
        d1.append('OG_033')
        d1.append('OG_033')
        # neutral - 15
        # southsea deckhand - 1
        d1.append('CS2_146')
        d1.append('CS2_146')
        # leper gnome - 1
        d1.append('EX1_029')
        d1.append('EX1_029')
        # elven archer - 1
        d1.append('CS2_189')
        d1.append('CS2_189')
        # bloodsail raider - 2
        d1.append('NEW1_018')
        d1.append('NEW1_018')
        # direwolf alpha - 2 	
        d1.append('EX1_162')
        d1.append('EX1_162')
        # harvest golem - 3
        d1.append('EX1_556')
        d1.append('EX1_556')
        # dread corsair - 4
        d1.append('NEW1_022')
        d1.append('NEW1_022')
        # leeroy jenkins
        d1.append('EX1_116')

        self.aggroDeck = d1

        deck = []# midrange
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

        self.midrangeDeck = deck

    def InitGame(self, player1=None, player2=None):

        if self.game is not None and self.game.ended is not State.COMPLETE:
            self.game.state = State.COMPLETE
            self.game.check_for_end_game()

        self.currentTurnStats = {'PLAYMINIONCARD': 0,
                                     'PLAYSPELLCARD': 0,
                                     'PLAYWEAPONCARD':0,
                                     'ATKMINTOMIN':0,
                                     'ATKHEROTOMIN':0,
                                     'ATKMINTOHERO':0,
                                     'ATKHEROTOHERO':0,
                                     'HEROPWR':0,
                                     'BOARDADV':0,
                                     'ENEMYMINDEATHS':0,
                                     'SELFHERODMG':0,
                                     'ENEMYHERODMG':0,
                                     'MANASPENTPERTURN':0,
                                     'MANASPENTPERGAME':0,
                                     'MANAREMAININGPERTURN':0}

        self.currentGameStats = {}
        self.prevSelfHeroDmg = 30
        self.prevEnemyHeroDmg = 30
        self.currentTurn = 1
        print(player1)
        print(player2)
        p1 = player1
        p2 = Utils.GetOpponent(player2)         

        deck = []
            # Assassinate - 4
        deck.append('CS2_076')
        deck.append('CS2_076')
            # Backstab - 0 
        deck.append('CS2_072')
        deck.append('CS2_072')
            # Bloodfen Raptor - 2
        deck.append('CS2_172')
        deck.append('CS2_172')
            # Deadly Poison - 1
        deck.append('CS2_074')
        deck.append('CS2_074')
            # Dragonling Mechanic - 4
        deck.append('EX1_025')
        deck.append('EX1_025')
            # Elven Archer - 1
        deck.append('CS2_189')
        deck.append('CS2_189')
            # Gnomish Inventor - 4
        deck.append('CS2_147')
        deck.append('CS2_147')
            # Goldshire Footman - 1
        deck.append('CS1_042')
        deck.append('CS1_042')
            # Ironforge Rifleman - 3	
        deck.append('CS2_141')
        deck.append('CS2_141')
            # Nightblade - 5
        deck.append('EX1_593')
        deck.append('EX1_593')
            # Novice Engineer - 2
        deck.append('EX1_015')
        deck.append('EX1_015')
            # Sap - 2
        deck.append('EX1_581')
        deck.append('EX1_581')
            # Sinister Strike - 1
        deck.append('CS2_075')
        deck.append('CS2_075')
            # Stormpike Commando - 5
        deck.append('CS2_150')
        deck.append('CS2_150')
            # Stormwind Knight - 7
        deck.append('CS2_131')
        deck.append('CS2_131')

        if player1 == 10:
            random.shuffle(self.aggroDeck)
            self.players[0] = Player("NEATBot", self.aggroDeck, CardClass(p1).default_hero)
        elif player1 == 3:
            random.shuffle(self.midrangeDeck)
            self.players[0] = Player("NEATBot", self.midrangeDeck, CardClass(p1).default_hero)

        if p2 == None:
            random.shuffle(deck)
            self.players[1] = Player("RogueBot", deck, CardClass(7).default_hero)
        else:
            self.players[1] = p2

        game = Game(players=self.players)
        game.start()

        # todo NN mulligan?
        #for p in game.players:
        mull = random.sample(game.players[0].choice.cards, 0)
        game.players[0].choice.choose(*mull) # *arg means recives tuple of "any" length (default empty)

        if self.AIBot is not None:
            mull = self.AIBot.GetMulligan(game.players[1].choice.cards)
            game.players[1].choice.choose(*mull)
        else:
            mull = random.sample(game.players[1].choice.cards, 0)
            game.players[1].choice.choose(*mull)

        self.players[0].playedcards = []
        self.players[1].playedcards = []

        self.game = game


    # returns None to denote whether a game is over
    def testgame(self, instance):
        player = 1 if instance.current_player.name == "NEATBot" else -1

        if instance.ended:
            print("instance ended, starting new if necessary.")
            return None
        try:
            if player == -1:
                print("enemy turn")            

                if instance.ended:
                    return None
                else:
                    self.HandleAITurn(instance)
                    return None               
            else:          
                return self.GetCurrentStateRepresentation(instance)
        except GameOver:
            return None
            
    def HandleAITurn(self, instance):
        if self.AIBot == None:
            play_turn(instance)
            return
        else:
            result = self.AIBot.GetNextTurn(instance)
            choice = result[0]
            source = result[1]
            targ = result[2]
            print(choice)

            if choice == 1:
                # minion atk
                source.attack(target=targ)
                return
            elif choice == 2:
                # play card
                if source is None:
                    return

                source.play(target=targ)
                return
            elif choice == 3:
                # hero pwr
                if self.AIBot.hero.power.requires_target():
                    self.AIBot.hero.power.use(target=targ)
                else:
                    self.AIBot.hero.power.use()
                return
            elif choice == 4:
                #end turn
                instance.end_turn()
                return
            elif choice == 5:
                # hero atk
                self.AIBot.hero.attack(target=targ)
                return

    def AddStats(self, rewardType):    
        # add to relevant stat per action
        self.currentTurnStats[rewardType] += 1
        print(rewardType)
         
    def FinaliseStatsEndOfTurn(self):
        currentTurn = self.currentTurn
        print("current Turn: {}".format(currentTurn))
        self.currentTurnStats['ENEMYMINDEATHS'] = self.game.players[0].minions_killed_this_turn
        self.currentTurnStats['BOARDADV'] = 1 if len(self.game.players[0].field) > len(self.game.players[1].field) else 0
        self.currentTurnStats['SELFHERODMG'] = (abs(self.prevSelfHeroDmg) - abs(self.game.players[0].hero.health))
        self.currentTurnStats['ENEMYHERODMG'] = (abs(self.prevEnemyHeroDmg) - abs(self.game.players[1].hero.health))
        self.currentTurnStats['MANASPENTPERTURN'] = abs((abs(self.game.players[0].mana) - abs(self.game.players[0].max_mana)))
        self.currentTurnStats['MANAREMAININGPERTURN'] = self.game.players[0].mana

        self.prevSelfHeroDmg = self.game.players[0].hero.health
        self.prevEnemyHeroDmg = self.game.players[1].hero.health

        if currentTurn == 1:
            self.currentGameStats[1] = self.currentTurnStats
        elif currentTurn not in self.currentGameStats:
            self.currentGameStats[currentTurn] = self.currentTurnStats
        else:
            print("key already in there what !!!")
            print(currentTurn)
            print(self.currentGameStats)
        self.currentTurn += 1
        self.numturns = self.currentTurn
        #print(self.currentGameStats)

        self.currentTurnStats = {'PLAYMINIONCARD': 0,
                                    'PLAYSPELLCARD': 0,
                                    'PLAYWEAPONCARD':0,
                                    'ATKMINTOMIN':0,
                                    'ATKHEROTOMIN':0,
                                    'ATKMINTOHERO':0,
                                     'ATKHEROTOHERO':0,
                                     'HEROPWR':0,
                                     'BOARDADV':0,
                                     'ENEMYMINDEATHS':0,
                                     'SELFHERODMG':0,
                                     'ENEMYHERODMG':0,
                                     'MANASPENTPERTURN':0,
                                     'MANASPENTPERGAME':0,
                                     'MANAREMAININGPERTURN':0}
            
    def GetCurrentStateRepresentation(self, instance):
        # should return a feature representation e.g. array of extracted game features

        state = []

        p1 = instance.current_player
        p2 = p1.opponent

        state.append(p1.hero.card_class-1) #player class (zero based)
        state.append(p2.hero.card_class-1)

        state.append(p1.hero.health / 30) 
        state.append(p2.hero.health / 30)

        state.append(p1.hero.power.is_usable() * 1) # hero power usable
        state.append(p1.max_mana / 10) # max mana
        state.append(p2.max_mana / 10)

        state.append(p1.mana / 10) # current mana

        # active hero weapons
        state.append(0 if p1.weapon is None else 1)
        state.append(0 if p1.weapon is None else p1.weapon.damage)
        state.append(0 if p1.weapon is None else p1.weapon.durability)

        state.append(0 if p2.weapon is None else 1)
        state.append(0 if p2.weapon is None else p2.weapon.damage)
        state.append(0 if p2.weapon is None else p2.weapon.durability)

        #state.append(0 if p1.atk is None else p1.atk/20)

        state.append(len(p2.hand) / 10)

        #minions in play

        i = 0

        buffer = [0] * 10
        p1Min = len(p1.field)

        p1mins = []
        p2mins = []

        for j in range(0, 7):
            if j < p1Min:
                p1mins.extend(buffer)
                p1mins[i] = 1 # is field slot filled

                p1mins[i+1] = p1.field[j].atk / 20
                p1mins[i+2] = p1.field[j].max_health / 20
                p1mins[i+3] = p1.field[j].health / 20
                p1mins[i+4] = p1.field[j].can_attack() * 1

                # minion keywords 1/0
                p1mins[i+5] = p1.field[j].has_deathrattle * 1
                p1mins[i+6] = p1.field[j].divine_shield * 1
                p1mins[i+7] = p1.field[j].taunt * 1
                p1mins[i+8] = p1.field[j].stealthed * 1
                p1mins[i+9] = p1.field[j].silenced * 1

            i += 10
        state.extend(p1mins)

        # enemy minions
        p2Min = len(p2.field)
        i = 0

        for j in range(0, 7):
            if j < p2Min:
                p2mins.extend(buffer)
                p2mins[i] = 1 # is field slot filled

                p2mins[i+1] = p2.field[j].atk / 20
                p2mins[i+2] = p2.field[j].max_health / 20
                p2mins[i+3] = p2.field[j].health / 20
                p2mins[i+4] = p2.field[j].can_attack() * 1

                # minion keywords 1/0
                p2mins[i+5] = p2.field[j].has_deathrattle * 1
                p2mins[i+6] = p2.field[j].divine_shield * 1
                p2mins[i+7] = p2.field[j].taunt * 1
                p2mins[i+8] = p2.field[j].stealthed * 1
                p2mins[i+9] = p2.field[j].silenced * 1

            i += 10
        state.extend(p2mins)

        # cards in hand
        p1Hand = len(p1.hand)

        i = 0
        p1h = []

        # TODO: probs affect heuristics here
        for j in range(0,10):
            if j < p1Hand:
                p1h.extend(buffer)
                p1h[i] = 1 # if card exists in "slot"

                # card deets
                p1h[i+1] = 1 if p1.hand[j].type == 4 else 0 # if minion
                p1h[i+2] = p1.hand[j].atk / 20 if p1h[i+1] == 1 else 0
                p1h[i+3] = p1.hand[j].health / 20 if p1h[i+1] == 1 else 0
                p1h[i+4] = p1.hand[j].divine_shield * 1 if p1h[i+1] == 1 else 0
                p1h[i+5] = p1.hand[j].has_deathrattle * 1 if p1h[i+1] == 1 else 0
                p1h[i+6] = p1.hand[j].taunt * 1 if p1h[i+1] == 1 else 0

                #weapons todo add stats
                p1h[i+7] = 1 if p1.hand[j].type == 7 else 0
                #spells todo add stats
                p1h[i+8] = 1 if p1.hand[j].type == 5 else 0

                p1h[i+9] = p1.hand[j].cost / 25
            i += 10
            
        state.extend(p1h)
        state.append(p2.mana / 10)
        state.append(len(p1.field) / 7)
        state.append(len(p2.field) / 7)
        state.append(len(p1.hand) / 10)
        state.append(len(p1.deck) / 30)
        state.append(len(p2.deck) / 30)
        state.append(1 if len(p1.hand) > len(p2.hand) else 0) # hand advantage
        state.append(1 if len(p1.field) > len(p2.field) else 0) # board advantage
            
        state.append(instance.turn /180) # current turn num (normalize by max turn num)

        # buffer if vector is not at 282
        if len(state) < 282:
            remainder = 282 - len(state)
            b = [0] * remainder
            state.extend(b)

        # normalize
        s = sum(state)
        norm = [float(x)/s for x in state]
        print(norm)
        return norm


    def GetValidMoves(self, instance, netOutput):
        # create binary mask for invalid moves
        # first bit == whether the action is valid

        rows, cols = (21,2)
        actions = [[0.0 for i in range(cols)] for j in range(rows)]
        player = instance.current_player

        if player.choice:
            # get valid choices e.g. discover, choose one
            for i, c in enumerate(player.choice.cards):
                actions[20][i] = 1.0
        else:
            # add cards in hand
            for i, card in enumerate(player.hand):
                if card.is_playable():
                    if card.requires_target():
                        actions[i][0] = 1.0
                        for t, c in enumerate(card.targets):
                            actions[i][1] += 1.0 # enumerate counter e.g board slot

                    elif card.must_choose_one:
                        for choice, c in enumerate(card.choose_cards):
                            actions[i][choice] = 1.0
                    else:
                        actions[i][0] = 1.0

            # add targets for each minion to attack
            # should always have atleast one target (hero or taunt minion)
            for pos, minion in enumerate(player.field):
                if minion.can_attack():
                    print(minion)
                    print("minion pos (on board): {}".format(pos))
                    actions[pos+10][0] = 1.0                    
                    for t, c in enumerate(minion.attack_targets):  
                        # set target masks                                                                
                        if(c.taunt):
                            actions[pos+10][1] += 1.0  
                            print("taunt minion (on board): {}".format(t)) 
                            print(c)
                        else:
                            actions[pos+10][1] += 1.0
                            print("minion targs: {}".format(t))
                            print(c)

            # hero power if available
            # mage and priest only ones that can attack self
            if player.hero.power.is_usable():
                if player.hero.power.requires_target():
                    for t, c in enumerate(player.hero.power.targets):
                        actions[17][1] += 1.0
                else:
                    actions[17][0] = 1.0

            # hero weapon attack if available
            if player.hero.can_attack():
                actions[18][0] = 1.0
                for t, c in enumerate(player.hero.attack_targets):
                    if(c.taunt):
                        actions[18][1] += 1.0  
                        print("taunt minion (on board): {}".format(t)) 
                    else:
                        actions[18][1] += 1.0
                        print("minion targs: {}".format(t))
                    
            
            # end turn
            actions[19][0] = 1.0
        
        return actions


    def ForceEndTurn(self, instance):
        try:
            self.FinaliseStatsEndOfTurn()
            p = instance.current_player
            p.game.end_turn()
        except GameOver:
            print("game has ended")
            return

    def PerformAction(self, a, instance):
        player = instance.current_player

        if not instance.ended:
            # get valid moves - mask invalid moves
            valids = self.GetValidMoves(instance, a) 
            # split output into "playables" and "targets"
            # playables
            # assemble valid actions through masking
            playables = []

            #cards
            cards = a[0:10]   
            for i in range(10):
                cards[i] = cards[i] * valids[i][0]
            #minions
            mins = a[10:17]
            for i in range(7):
                mins[i] = mins[i] * valids[i+10][0]

            hp = a[17] * valids[17][0]
            wep = a[18] * valids[18][0]
            endTurn = a[19] * valids[19][0]
            print("End turn VAL: {}".format(valids[19][0]))
            cards.extend(mins)
            cards.append(hp)
            cards.append(wep)
            cards.append(endTurn)

            playables = cards

            action = max(range(len(playables)), key=playables.__getitem__)

            # targets
            targets = []          
            heroes = a[20:22]           
            targs = a[22:29]
            # side of board
            side1 = a[29]
            side2 = a[30]

            print("Hero: {}".format(heroes))
            print("Mins: {}".format(targs))
                
            #chooseOne = a[38:40]
            #c1 = chooseOne.index(max(chooseOne)) 
            targets.extend(heroes)      
            targets.extend(targs) # - 1 
            
            target = max(range(len(targets)), key=targets.__getitem__)           
            chosenTarg = target

            print("\nValids")
            print(valids)
            print("\nPlayables")
            print(playables)
            print("\nTargets")
            print(targets)
            print("\nAction: {}".format(action))
            print("Action Value:")
            print(cards[action])
            print("End Turn value: {}".format(cards[19]))
            print("Chosen Target: {}".format(chosenTarg))

            # if actions are all 0 (max chosen action is 0),
            # activate retries
            if cards[action] == 0.0:
                return 1

            try:
                # sort targ indices
                # should be max 8 (per side)
                # e.g. 7 mins + self,
                # 7 enemy mins + enemy hero
                # if taunts - all targs that arent taunt are removed
                t = int(chosenTarg)
                
                if 1 < t <= 8:
                    t = t-1
                    
                if t < 0:
                    t = 0

                print("Sorted Target: {}".format(t))

                if 0 <= int(action) <= 9:
                    c = int(action)
                    print("card Picked")
                    print(player.hand[c])                   

                    try:                                     
                        card = player.hand[c]
                    except:
                        print("went to play a card but hand is empty")
                        return 1

                    if card.requires_target():
                        t = self.GetValidTarget(c, valids, 
                        targets, card.targets) 

                        if 0 <= t < len(card.targets):                           
                            try:
                                print("targetting index: {}".format(t))
                                print("Card target:")
                                print(card.targets[t])
                                
                                # get reward
                                if card.type == 4:
                                    self.AddStats('PLAYMINIONCARD')
                                elif card.type == 5:
                                    self.AddStats('PLAYSPELLCARD')
                                elif card.type == 7:
                                    self.AddStats('PLAYWEAPONCARD')
                                card.play(card.targets[t])
                            except GameOver:
                                print("most likely killed self")
                                return 0
                        else:
                            print("tried to play card with no valid targets.")
                            return 1
                    elif card.must_choose_one:
                        card.play(choose=card.choose_targets[t])
                    else:
                        try:
                            if card.type == 4:
                                self.AddStats('PLAYMINIONCARD')
                            elif card.type == 5:
                                self.AddStats('PLAYSPELLCARD')
                            elif card.type == 7:
                                self.AddStats('PLAYWEAPONCARD')
                            card.play()
                        except InvalidAction:
                            print("Cannot play that card or hand is empty")
                            print(card)
                            print("\n")
                            return 1
                            #player.game.end_turn()
                    try:
                        player.playedcards.append(card.id)
                    except InvalidAction:
                        print("tried to add card to played cards, empty hand")
                        return 1
                elif 10 <= int(action) <= 16:
                    print("Attacking with minion:")
                    c = int(action-10)      
                    t = self.GetValidTarget(c+10, valids, 
                    targets, player.field[c].attack_targets)       
                    if t == -1:
                        return 1

                    try:                        
                        print(player.field[c])
                        print(player.field[c].attack_targets[t])

                        if player.field[c].attack_targets[t].type == CardType.HERO:
                            self.AddStats('ATKMINTOHERO')
                        elif player.field[c].attack_targets[t].type == CardType.MINION:
                            self.AddStats('ATKMINTOMIN')

                        player.field[c].attack(player.field[c].attack_targets[t])
                    except IndexError:
                        print("tried to attack at null index, probs NN output")
                        return 1
                    except GameOver:
                        print("weird gameover state")
                        return 0
                elif int(action) == 17:
                    if player.hero.power.requires_target():
                        
                        '''if player.hero.power.play_targets[t].type == CardType.HERO:
                            self.AddStats(rewardFuncs, 'ATKHEROTOHERO')
                        elif player.hero.power.play_targets[t].type == CardType.MINION:
                            self.AddStats(rewardFuncs, 'ATKHEROTOMIN')'''
                        player.hero.power.use(player.hero.power.play_targets[t])
                    else:
                        
                        self.AddStats('HEROPWR')
                        player.hero.power.use()
                elif int(action) == 18:
                    print("attacking with Hero: \n")
                    t = self.GetValidTarget(18, valids, 
                    targets, player.hero.attack_targets)
                    if t == -1:
                        return 1

                    try:                       
                        print(player.hero.attack_targets)
                        if player.hero.attack_targets[t].type == CardType.HERO:
                            self.AddStats('ATKHEROTOHERO')
                        elif player.hero.attack_targets[t].type == CardType.MINION:
                            self.AddStats('ATKHEROTOMIN')

                        player.hero.attack(player.hero.attack_targets[t])
                    except GameOver:
                        return 0
                elif int(action) == 19:
                    try:                   
                        self.FinaliseStatsEndOfTurn()
                        player.game.end_turn()
                    except GameOver:
                        return 0
                elif int(action) == 20 and not player.choice:             
                    self.FinaliseStatsEndOfTurn()
                    player.game.end_turn()
            except IndexError:
                print("most likely error with sim not updating targets in time.")
                return 1
            except InvalidAction:
                print("error action - should've ended turn.")
                return 1


    def GetValidTarget(self, index, valids, targets, entityTargs):
        # get the correct "valid action" slot
        c = None

        for j in range(len(valids)):
            if j == index:
                print("index: {}".format(j))
                c = valids[j]
        print("=====")
        print(c)
        print(entityTargs)

        # get "both sides" of the board if applicable
        p1BoardValids = [0.0] * 8
        p2BoardValids = [0.0] * 8
        p1Board = []
        p2Board = []

        for i in range(len(entityTargs)):
            if entityTargs[i].controller == self.game.players[0]:
                p1Board.append(entityTargs[i])

            elif entityTargs[i].controller == self.game.players[1]:
                p2Board.append(entityTargs[i])

        
        # get the valid targets
        for i in range(len(p1Board)):
            p1BoardValids[i] = 1.0
        for i in range(len(p2Board)):
            p2BoardValids[i] = 1.0

        min = entityTargs[0]
        print("\nValids")
        print(p1BoardValids)
        print(p2BoardValids)
        t1 = [0.0] * 8
        t2 = [0.0] * 8

        p1TargVals = []
        p1TargVals.append(targets[0])
        p1TargVals.extend(targets[2:9])
        p2TargVals = targets[1:9]
        print("\nTargets P1 / P2")
        print(p1TargVals)
        print(p2TargVals)

        for i in range(len(p1TargVals)):
            t1[i] = p1TargVals[i] * p1BoardValids[i]
        for i in range(len(p2TargVals)):
            t2[i] = p2TargVals[i] * p2BoardValids[i]

        if max(t1) == 0 and max(t2) == 0:
            # probs got no valid targets 
            print("Net outputted no valid targets")
            return -1

        target = 0
        try: # simply choose the best ranked utility as target
            p1m = max(t1)
            p2m = max(t2)
            p1t = max(range(len(t1)), key=t1.__getitem__)     
            p2t = max(range(len(t2)), key=t2.__getitem__) 
                    
            if p1m > p2m:
                target = p1t
            else:
                target = p2t
    
        except ValueError:
            print("net outputted 0.0 target.")
            return -1
        print(t1)
        print(t2)
        if min.taunt:#if 1 < target <= 8:
            target = target-1
                     
        if target < 0:
            target = 0

        print("Card/Spell/Attack Target: {0}".format(target))
        
        return target

    def GameEnded(self):
        p1 = self.game.players[0]
        p2 = self.game.players[1]
        print("player 1: {}".format(p1))
        print("player 2: {}".format(p2))

        if p1.playstate == 4:
            print("won game")
            return 1
        if p2.playstate == 4:
            print("enemy won game")
            return -1
        if p1.playstate == 6 and p2.playstate == 6:
            print("DRAW")
            return 0.5
        if self.game.turn > 180:
            
            print("RAN OUT OF TURNS - LOSS")
            return -1
        
        return None