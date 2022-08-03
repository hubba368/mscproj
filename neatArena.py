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
        
       # self.testgame(self.game)

        
    #TODOs below
    def InitGame(self):
        # should return representation of game state (initial) that can be inserted into neat NN

        cards.db.initialize()

        if self.testGame:
            extra_set = cards.filter(
                card_set = [CardSet.EXPERT1, CardSet.HOF, CardSet.NAXX, CardSet.GVG, CardSet.BRM, CardSet.TGT, CardSet.LOE, CardSet.OG, CardSet.KARA, CardSet.GANGS,
                            CardSet.UNGORO, CardSet.ICECROWN, CardSet.LOOTAPALOOZA, CardSet.GILNEAS, CardSet.BOOMSDAY, CardSet.TROLL]
            )

            p1 = 7
            p2 = 7
            # todo make decks in sep func or pull from file
            d1 = []
            # Assassinate
            d1.append('CS2_076')
            d1.append('CS2_076')
            # Backstab
            d1.append('CS2_072')
            d1.append('CS2_072')
            # Bloodfen Raptor
            d1.append('CS2_172')
            d1.append('CS2_172')
            # Deadly Poison
            d1.append('CS2_074')
            d1.append('CS2_074')
            # Dragonling Mechanic
            d1.append('EX1_025')
            d1.append('EX1_025')
            # Elven Archer
            d1.append('CS2_189')
            d1.append('CS2_189')
            # Gnomish Inventor
            d1.append('CS2_147')
            d1.append('CS2_147')
            # Goldshire Footman
            d1.append('CS1_042')
            d1.append('CS1_042')
            # Ironforge Rifleman 	
            d1.append('CS2_141')
            d1.append('CS2_141')
            # Nightblade
            d1.append('EX1_593')
            d1.append('EX1_593')
            # Novice Engineer
            d1.append('EX1_015')
            d1.append('EX1_015')
            # Sap
            d1.append('EX1_581')
            d1.append('EX1_581')
            # Sinister Strike
            d1.append('CS2_075')
            d1.append('CS2_075')
            # Stormpike Commando
            d1.append('CS2_150')
            d1.append('CS2_150')
            # Stormwind Knight
            d1.append('CS2_131')
            d1.append('CS2_131')

            random.shuffle(d1)

            d2 = d1.copy()
            random.shuffle(d2)

            self.players[0] = Player("Player1", d1, CardClass(p1).default_hero)
            self.players[1] = Player("Player2", d1, CardClass(p2).default_hero)

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

        if player == -1:
            print("enemy turn")
            play_turn(instance)
            return None
        else:

            #actions = self.GetValidMoves(instance)
            return self.GetCurrentStateRepresentation(instance)
        '''while not self.game.ended:
            it+=1
            print("test ruin")'''

            


            

    def GetCurrentStateRepresentation(self, instance):
        # should return a feature representation e.g. array of extracted game features

        #state = np.zeros(281, dtype=np.float32)
        state = [0] * 282

        p1 = instance.current_player
        p2 = p1.opponent

        state[p1.hero.card_class-1] = 1 #player class (zero based)
        state[10+p2.hero.card_class-1] = 1

        i = 20 #current bit flag

        state[i] = p1.hero.health / 30 
        state[i+1] = p2.hero.health / 30

        state[i + 2] = p1.hero.power.is_usable() * 1 # hero power usable
        state[i+3] = p1.max_mana / 10 # mana
        state[i+4] = p2.max_mana / 10

        state[i+5] = p1.mana / 10

        state[i+6] = 0 if p1.weapon is None else 1
        state[i+7] = 0 if p1.weapon is None else p1.weapon.damage
        state[i+8] = 0 if p1.weapon is None else p1.weapon.durability

        state[i+9] = 0 if p2.weapon is None else 1
        state[i+10] = 0 if p2.weapon is None else p2.weapon.damage
        state[i+11] = 0 if p2.weapon is None else p2.weapon.durability

        state[i+12] = len(p2.hand) / 10

        #minions in play

        i = 33

        p1Min = len(p1.field)

        for j in range(0, 7):
            if j < p1Min:
                state[i] = 1 # is field slot filled

                state[i+1] = p1.field[j].atk / 20
                state[i+2] = p1.field[j].max_health / 20
                state[i+3] = p1.field[j].health / 20
                state[i+4] = p1.field[j].can_attack() * 1

                # minion keywords 1/0
                state[i+5] = p1.field[j].has_deathrattle * 1
                state[i+6] = p1.field[j].divine_shield * 1
                state[i+7] = p1.field[j].taunt * 1
                state[i+8] = p1.field[j].stealthed * 1
                state[i+9] = p1.field[j].silenced * 1

            i += 10

        # enemy minions
        p2Min = len(p2.field)

        for j in range(0, 7):
            if j < p2Min:
                state[i] = 1 # is field slot filled

                state[i+1] = p2.field[j].atk / 20
                state[i+2] = p2.field[j].max_health / 20
                state[i+3] = p2.field[j].health / 20
                state[i+4] = p2.field[j].can_attack() * 1

                # minion keywords 1/0
                state[i+5] = p2.field[j].has_deathrattle * 1
                state[i+6] = p2.field[j].divine_shield * 1
                state[i+7] = p2.field[j].taunt * 1
                state[i+8] = p2.field[j].stealthed * 1
                state[i+9] = p2.field[j].silenced * 1

            i += 10

        # cards in hand
        p1Hand = len(p1.hand)

        for j in range(0,10):
            if j < p1Hand:
                state[i] = 1

                # card deets
                state[i+1] = 1 if p1.hand[j].type == 4 else 0 # if minion
                state[i+2] = p1.hand[j].atk / 20 if state[i+1] == 1 else 0
                state[i+3] = p1.hand[j].health / 20 if state[i+1] == 1 else 0
                state[i+4] = p1.hand[j].divine_shield * 1 if state[i+1] == 1 else 0
                state[i+5] = p1.hand[j].has_deathrattle * 1 if state[i+1] == 1 else 0
                state[i+6] = p1.hand[j].taunt * 1 if state[i+1] == 1 else 0

                #weapons todo add stats
                state[i+7] = 1 if p1.hand[j].type == 7 else 0
                #spells todo add stats
                state[i+8] = 1 if p1.hand[j].type == 5 else 0

                state[i+0] = p1.hand[j].cost / 25
            i += 10
            
        state[273] = p2.mana / 10
        state[274] = len(p1.field) / 7
        state[275] = len(p2.field) / 7
        state[276] = len(p1.hand) / 10
        state[277] = len(p1.deck) / 30
        state[278] = len(p2.deck) / 30
        state[279] = 1 if len(p1.hand) > len(p2.hand) else 0 # hand advantage
        state[280] = 1 if len(p1.field) > len(p2.field) else 0 # board advantage
            
        state[281] = instance.turn /180 # current turn num (normalize by max turn num)

        i = 282
        return state

    def GetNextState(self, player, chosenAction, instance):
        # should take 
        i = 0

    def GetValidMoves(self, instance):
        # should return some ds of nn applicable moves to features
        # e.g. binary val matrix

        rows, cols = (21,18)

        actions = [[0 for i in range(cols)] for j in range(rows)]
        player = instance.current_player

        if player.choice:
            # get valid choices
            for i, c in enumerate(player.choice.cards):
                print(c)
                actions[20][i] = 1 # only valid card choices e.g. discover?
        else:
            # add cards in hand
            for i, card in enumerate(player.hand):
                if card.is_playable():
                    if card.requires_target():
                        for t, c in enumerate(card.targets):
                            actions[i][t] = 1
                            '''print("\n can play cards:\n")
                            print(c)
                            print(t)'''
                    elif card.must_choose_one:
                        for choice, c in enumerate(card.choose_cards):
                            actions[i][choice] = 1
                    else:
                        actions[i] = 1

            # add targets for each minion to attack
            for pos, minion in enumerate(player.field):
                if minion.can_attack():
                    for t in enumerate(minion.attack_targets):
                        # pos+=10
                        print(t)
                        print(t[0])
                        actions[pos][t[0]] = 1

            # hero power if available
            if player.hero.power.is_usable():
                if player.hero.power.requires_target():
                    for t in enumerate(player.hero.power.targets):
                        actions[17][t[0]] = 1
                else:
                    actions[17] = 1

            # hero weapon attack if available
            if player.hero.can_attack():
                for t in enumerate(player.hero.attack_targets):
                    actions[18][t] = 1
            
            # end turn TODO add concede?
            actions[19][1] = 1
        
        return actions


    def PerformAction(self, a, instance):
        player = instance.current_player

        if not instance.ended:
            try:
                if 0 <= int(a[0]) <= 9:
                    if player.hand[int(a[0])].requires_target():
                        player.hand[int(a[0])].play(player.hand[int(a[0])].targets[int(a[1])])
                    elif player.hand[int(a[0])].must_choose_one:
                        player.hand[int(a[0])].play(choose=player.hand[int(a[0])].choose_targets[int(a[1])])
                    else:
                        try:
                            player.hand[int(a[0])].play()
                        except InvalidAction:
                            print("Cannot play that card")
                            print(player.hand[int(a[0])])
                            print("\n")
                            player.game.end_turn()

                    player.playedcards.append(player.hand[int(a[0])].id)

                elif 10 <= int(a[0]) <= 16:
                    player.field[int(a[0])-10].attack(player.field[int(a[0])-10].attack_targets[int(a[1])])
                elif int(a[0]) == 19:
                    player.game.end_turn()
                elif int(a[0]) == 20 and not player.choice:
                    player.game.end_turn()
            except InvalidAction:
                print("error action - should've ended turn.")
                player.game.end_turn()


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

