import random
#import numpy as np
#import pickle
import copy


from fireplace import cards
from fireplace.exceptions import GameOver, InvalidAction
from fireplace.game import Game
from fireplace.player import Player
from fireplace.utils import random_draft
from fireplace.deck import Deck
from fireplace.utils import play_turn

from hearthstone.enums import CardClass, CardSet

class NeatArena:

    def __init__(self, testGame=True):
        self.game = None
        self.players = ['Player1', 'Player2']
        self.testGame = testGame # for debugging stuff
        cards.db.initialize()
       # self.testgame(self.game)

        
    #TODOs below
    def InitGame(self):
        # should return representation of game state (initial) that can be inserted into neat NN

        

        if self.testGame:
            extra_set = cards.filter(
                card_set = [CardSet.EXPERT1, CardSet.HOF, CardSet.NAXX, CardSet.GVG, CardSet.BRM, CardSet.TGT, CardSet.LOE, CardSet.OG, CardSet.KARA, CardSet.GANGS,
                            CardSet.UNGORO, CardSet.ICECROWN, CardSet.LOOTAPALOOZA, CardSet.GILNEAS, CardSet.BOOMSDAY, CardSet.TROLL]
            )

            p1 = 10
            p2 = 7 # mage is 4
            # todo make decks in sep func or pull from file
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

            random.shuffle(d1)

            deck = []

            # Assassinate
            deck.append('CS2_076')
            deck.append('CS2_076')
            # Backstab
            deck.append('CS2_072')
            deck.append('CS2_072')
            # Bloodfen Raptor
            deck.append('CS2_172')
            deck.append('CS2_172')
            # Deadly Poison
            deck.append('CS2_074')
            deck.append('CS2_074')
            # Dragonling Mechanic
            deck.append('EX1_025')
            deck.append('EX1_025')
            # Elven Archer
            deck.append('CS2_189')
            deck.append('CS2_189')
            # Gnomish Inventor
            deck.append('CS2_147')
            deck.append('CS2_147')
            # Goldshire Footman
            deck.append('CS1_042')
            deck.append('CS1_042')
            # Ironforge Rifleman 	
            deck.append('CS2_141')
            deck.append('CS2_141')
            # Nightblade
            deck.append('EX1_593')
            deck.append('EX1_593')
            # Novice Engineer
            deck.append('EX1_015')
            deck.append('EX1_015')
            # Sap
            deck.append('EX1_581')
            deck.append('EX1_581')
            # Sinister Strike
            deck.append('CS2_075')
            deck.append('CS2_075')
            # Stormpike Commando
            deck.append('CS2_150')
            deck.append('CS2_150')
            # Stormwind Knight
            deck.append('CS2_131')
            deck.append('CS2_131')

            random.shuffle(deck)

            self.players[0] = Player("Player1", d1, CardClass(p1).default_hero)
            self.players[1] = Player("Player2", deck, CardClass(p2).default_hero)

            game = Game(players=self.players)
            game.start()

            # todo NN mulligan?
            for p in game.players:
                mull = random.sample(p.choice.cards, 0)
                p.choice.choose(*mull) # *arg means recives tuple of "any" length (default empty)

            self.players[0].playedcards = []
            self.players[1].playedcards = []

            self.game = game
            #return game

    def testgame(self, instance):

        player = 1 if instance.current_player.name == "Player1" else -1
        it = 0
        if instance.ended:
            print("instance ended prematurely")
            return None
        try:
            if player == -1:
                print("enemy turn")
                if instance.ended:
                    return None
                else:
                    play_turn(instance)
                return None
            else:

               
                return self.GetCurrentStateRepresentation(instance)
        except GameOver:
            return None
            

            


            

    def GetCurrentStateRepresentation(self, instance):
        # should return a feature representation e.g. array of extracted game features

        #state = np.zeros(281, dtype=np.float32)
        state = []

        p1 = instance.current_player
        p2 = p1.opponent

        state.append(p1.hero.card_class-1) #player class (zero based)
        state.append(p2.hero.card_class-1)

        i = 20 #current bit flag

        state.append(p1.hero.health / 30) 
        state.append(p2.hero.health / 30)

        state.append(p1.hero.power.is_usable() * 1) # hero power usable
        state.append(p1.max_mana / 10) # max mana
        state.append(p2.max_mana / 10)

        state.append(p1.mana / 10) # current mana

        state.append(0 if p1.weapon is None else 1)
        state.append(0 if p1.weapon is None else p1.weapon.damage)
        state.append(0 if p1.weapon is None else p1.weapon.durability)

        state.append(0 if p2.weapon is None else 1)
        state.append(0 if p2.weapon is None else p2.weapon.damage)
        state.append(0 if p2.weapon is None else p2.weapon.durability)

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

        if len(state) < 282:
            remainder = 282 - len(state)
            b = [0] * remainder
            state.extend(b)

        return state


    def GetValidMoves(self, instance, netOutput):
        # create binary mask for invalid moves

        rows, cols = (21,18)

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
                        for t, c in enumerate(card.targets):
                            actions[i][t] = 1.0 # enumerate counter e.g board slot

                    elif card.must_choose_one:
                        for choice, c in enumerate(card.choose_cards):
                            actions[i][choice] = 1.0
                    else:
                        actions[i][0] = 1.0

            # add targets for each minion to attack
            for pos, minion in enumerate(player.field):
                if minion.can_attack():
                    for t, c in enumerate(minion.attack_targets):                   
                        actions[pos+10][t] = 1.0
                        print("minion pos: {}".format(pos+10))
                        print("minion targ: {}".format(t))

            # hero power if available
            if player.hero.power.is_usable():
                if player.hero.power.requires_target():
                    for t, c in enumerate(player.hero.power.targets):
                        actions[17][t] = 1.0
                else:
                    actions[17][0] = 1.0

            # hero weapon attack if available
            if player.hero.can_attack():
                for t, c in enumerate(player.hero.attack_targets):
                    print(c)
                    actions[18][t] = 1.0
            
            # end turn TODO add concede?
            actions[19][0] = 1.0
        
        return actions


    def ForceEndTurn(self, instance):
        try:
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

            print("Player Current Hand (L to R):")
            for i in range(len(player.hand)):
                print(player.hand[i])

            print("\n player boards:")
            for i in range(len(instance.players)):
                cur = instance.players[i]
                print(cur)
                if len(cur.field) > 0:
                    for i in range(len(cur.field)):
                        print(cur.field[i])
            print("\nPlayer Current Board (L to R):")
            if len(player.field) > 0:
                for i in range(len(player.field)):
                    print(player.field[i])
            else:
                print("Player Board Empty.")
        


            playables = []
            cards = a[0:10]   
            print("MEGA TEST")
            print(valids)          
            # assemble valids
            for i in range(10):
                #print(cards[i])
                cards[i] = cards[i] * valids[i][0]
                #print(cards[i])


            mins = a[10:17]
            for i in range(7):
                mins[i] = mins[i] * valids[i+10][0]

            c = cards.index(max(cards))
            m = mins.index(max(mins))

            hp = a[17] * valids[17][0]
            wep = a[18] * valids[18][0]
            endTurn = a[19] * valids[19][0]
            cards.extend(mins)
            cards.append(hp)
            cards.append(wep)
            cards.append(endTurn)

            playables = cards

            action = max(range(len(playables)), key=playables.__getitem__)

            # targets
            targets = []
            
            p1 = a[20]
            p2 = a[21]
            targ1 = a[22:29]
            targ2 = a[29:36]
            print("P1 Mins: {}".format(targ1))
            print("P2 Mins: {}".format(targ2))
            #t1 = targ1.index(max(targ1))
            #t2 = targ2.index(max(targ2))

            #t1 = max(targ1)
            #t2 = max(targ2)
            
            none = a[36]
            #chooseOne = a[38:40]
            #c1 = chooseOne.index(max(chooseOne))
            targets.append(p1)
            targets.append(p2)
            targets.append(none)
            targets.extend(targ1) # - 2
            targets.extend(targ2) # - 9  9-15

            #targets.extend(chooseOne)            

            
            target = max(range(len(targets)), key=targets.__getitem__)
            
            #temp = max(t1,t2,targets[target])

            chosenTarg = target

            print("\nActions")
            print(playables)
            print("\nTargets")
            print(targets)
            #print("\nTargets - Minions")
            #print("P1: {},  P2: {}".format(t1,t2))
            print("\nAction: {}".format(action))
            print("Action Value:")
            print(cards[action])
            print("End Turn value: {}".format(cards[19]))
            print("Chosen Target: {}".format(chosenTarg))
            print("Target: {}".format(target))
            

            #if action == 0.0:
                #print("no viable actions")
                #return 1

            #if et > 0.5:
                #player.game.end_turn()

            try:
                # sort targ indices
                t = int(chosenTarg)
                
                if 1 < t <= 8:
                    t = t-2
                elif 9 <= t <= 16:
                    t = t-9
                    if t < 0:
                        t = 0
                print("Sorted Target: {}".format(t))

                if 0 <= int(action) <= 9:
                    c = int(action)
                    print("card Picked")
                    try:
                        print(player.hand[c])                
                        card = player.hand[c]
                    except:
                        print("went to play a card but hand is empty")
                        return 1


                    if card.requires_target():
                        print(card.targets)
                        if 0 <= t < len(card.targets):
                            print("targetting index: {}".format(t))
                            print("Card target:")
                            print(card.targets[t])
                            try:
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
                    c = int(action-10)                   
                    try:
                        print(player.field[c].attack_targets)
                        player.field[c].attack(player.field[c].attack_targets[t])
                    except GameOver:
                        print("weird gameover state")
                        return 0
                elif int(action) == 17:
                    if player.hero.power.requires_target():
                        player.hero.power.use(player.hero.power.play_targets[t])
                    else:
                        player.hero.power.use()
                elif int(action) == 18:
                    print(player.hero.attack_targets)
                    try:
                        player.hero.attack(player.hero.attack_targets[t])
                    except GameOver:
                        return 0
                elif int(action) == 19:
                    try:
                        player.game.end_turn()
                    except GameOver:
                        return 0
                elif int(action) == 20 and not player.choice:
                    player.game.end_turn()
            except IndexError:
                print("most likely error with sim not updating targets in time.")
                return 1
            except InvalidAction:
                print("error action - should've ended turn.")
                return 1


    def GameEnded(self):
        p1 = self.game.players[0]
        p2 = self.game.players[1]

        if p1.playstate == 4:
            return 1
        if p2.playstate == 4:
            return -1
        if p1.playstate == 6 and p2.playstate == 6:
            return 0
        if self.game.turn > 180:
            self.game.ended = True
            return 0
        #return None

