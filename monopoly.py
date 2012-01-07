from __future__ import print_function
import pdb
from random import randrange
import csv


class Player:
    name = ''
    position = 0
    money = 1500
    def __init__(self, name):
        self.name = name 

    def print_state(self):
        print('%s: Position %2d, Money $%4d' % (self.name, self.position, self.money))

    def take_turn(self):
        for roll_num in range(3):
            d1,d2 = (randrange(6)+1 for die in range (2))
            print ('%s rolled %d' %(self.name, d1+d2))
            if roll_num == 3 and d1 == d2:
                self.go_to_jail()
            self.position += d1 + d2
            self.position %= 40
            self.eval_new_position()
            self.property_development()
            print_game_state()
            if d1 != d2:
                break

    def eval_new_position(self):
        p = property_state[self.position]
        if not p.property_bool:
            return
        if p.owner == bank:
            if self.buy_decision():
                p.change_owner(self)
        elif p.owner != self:
            pay_rent(p.owner, self, p.rate)
            print('%s paid %d in rent to %s for landing on %s' %(self.name, p.rate, p.owner.name, p.name))
            if self.money < 0:
                print ('Game over man, %s loses!' %self.name)
                exit(0)

    def property_development(self):
        # build one house on lowest valued property we have a monopoly on
        for p in self.gen_my_properties():
            if p.building_state > 0:
                if p.add_house():
                    return

    def buy_decision(self):
        # for now always buy
        # TODO make this logic more sophisticated
        return True

    def trade_decision(self):
        return True

    def gen_my_properties(self):
        for p in property_state:
            if p.owner == self:
                yield p

class Property:
    def __init__(self, **kwargs):
        # game definition
        self.position = kwargs['Board Position']
        self.name = kwargs['Name']
        self.group = int(kwargs['Property Group #'])
        self.cost_to_buy = int(kwargs['Cost to buy'])
        self.mortgage_value = int(kwargs['Mortgage value'])
        self.all_rates = (int(kwargs['Rent_0']), int(kwargs['Rent_m']),
                          int(kwargs['Rent_1']), int(kwargs['Rent_2']),
                          int(kwargs['Rent_3']), int(kwargs['Rent_4']),
                          int(kwargs['Rent_h']))
        self.property_bool = int(kwargs['Property?'])
        self.chance_bool = int(kwargs['Chance?'])
        self.community_chest_bool = int(kwargs['Community Chest?'])
        self.railroad_bool = int(kwargs['Railroad?'])
        self.utility_bool = int(kwargs['Utility?'])
        self.fine = int(kwargs['Fine $'])

        # game state
        self.owner = bank
        self.houses = 0
        self.monopoly = 0
        self.building_state = 0
        self.rate = self.all_rates[0]

    def print_state(self):
        if self.owner != bank and self.property_bool:
            print('%s:%s %d+%d=%d' %(self.name, self.owner.name, self.monopoly, self.houses, self.building_state))

    def update_state(self):
        begin_mon = self.monopoly
        self.monopoly = True
        for p_g in gen_group(self.group):
            if p_g.owner != self.owner:
                self.monopoly = False
        self.building_state = self.monopoly + self.houses
        self.rate = self.all_rates[self.building_state]
        if self.monopoly:
            print('we got a monopoly %s' %self.name)

        # this seems inefficent, TODO make this cleaner
        if begin_mon != self.monopoly:
            for p_g in gen_group(self.group):
                p_g.update_state()
            
    def add_house(self):
        if self.houses < 5 and not self.railroad_bool and not self.utility_bool:
            self.houses += 1
            self.update_state()
            return True
        return False

    def change_owner(self, owner):
        self.owner = owner
        print('%s bought %s' %(owner.name, self.name))
        self.update_state()
        
def gen_group(num):
    for p in property_state:
        if p.group == num:
            yield p

def pay_rent(dest, src, amount):
    dest.money += amount
    src.money -= amount

total_positions = 40
property_state = []
player_names = ['dog', 'car']
players = [Player(name) for name in player_names]
bank = Player('Bank')
num_turns = 500

def print_game_state():
    for player in players:
        player.print_state()
    for prop in property_state:
        prop.print_state()

csv_file = 'board_positions.csv'
with open(csv_file, 'rb') as f:
    reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        property_state.append(Property(**row))

for turn in range(num_turns):
    for player in players:
        player.take_turn()
    print('\n')

# print whole game state (serialize it too)
# game mechanics
# trades
# decide to build houses
