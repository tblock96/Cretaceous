''' Animal Class '''

import network as n
import random, math

ENERGY_RATE = 4 # lower is harder
FOOD_RATE = 2  # lower is harder
ATTACK_FACTOR = 10
FOOD_DROP = 400

def get_dist(r2, r1):
    x1, y1 = r1
    x2, y2 = r2
    return ((x2-x1)**2+(y2-y1)**2)**0.5

def get_direction(r2, r1):
    x2,y2 = r2
    x1,y1 = r1
    return math.atan2(y2-y1, x2-x1)
    
class Species():

    def __init__(self, key, net_depth, net_width,location, size, scale, num_spec):
        self.color = (random.randint(0,256),random.randint(0,256),
            random.randint(0,256))
        self.s = n.SexualSpecies(num_spec + 5, 5,net_depth,net_width)
        self.member_nets = self.s.members
        self.key = key
        self.members = {}
        self.dead = []
        self.next_key = 0
        self.location = [location[0], location[1]]
        self.size = size
        self.scale = scale
        self.num_spec = num_spec
    
    def inc_ENERGY_RATE(self):
        global ENERGY_RATE
        ENERGY_RATE += 0.01
        print("Energy Rate is now %f." %ENERGY_RATE)
    
    def dec_ENERGY_RATE(self):
        global ENERGY_RATE
        ENERGY_RATE -= 0.05
        print("Energy Rate is now %f." %ENERGY_RATE)
        
    def add_member(self):
        self.s.add_member(self.next_key)
        self.members[self.next_key] = Animal(self, self.next_key)
        self.members[self.next_key].set_location([self.location[0]+(random.random()-0.5)*self.size*self.scale/2,
            self.location[1]+(random.random()-0.5)*self.size*self.scale/2])
        self.next_key += 1
    
    def remove_member(self, key):
        del self.members[key]
        self.s.remove_member(key)
        self.dead.append(key)
    
    def breed(self, p1, p2):
        self.s.breed(p1,p2,self.next_key)
        energy_sum = health_sum = 0
        for p in [p1, p2]:
            self.members[p].energy /= 2
            energy_sum += self.members[p].energy
            self.members[p].health /= 2
            health_sum += self.members[p].health
        self.members[self.next_key] = Animal(self, self.next_key, p1, p2)
        self.members[self.next_key].energy = energy_sum / 4.
        self.members[self.next_key].health = health_sum / 4.
        x = self.members[p1].location[0]
        y = self.members[p2].location[1]
        self.members[self.next_key].location = [x,y]
        self.next_key += 1
    
    def get_details(self):
        keys = []
        locs = []
        health = []
        colors = []
        for k, m in self.members.items():
            keys.append(k)
            locs.append(m.location)
            health.append(m.health)
            colors.append(self.color)
        return keys,locs,health,colors
        
    def take_turn(self, all):
        actions = {}
        for k, m in self.members.items():
            actions[k] = m.take_turn(all, self.key)
        return actions
    
    def change_speed(self, key, val):
        if key not in self.dead:
            self.members[key].set_speed(val)
    
    def add_direction(self, key, val):
        if key not in self.dead:
            self.members[key].turn(val)
    
    def member_looked(self, key):
        if key not in self.dead:
            self.members[key].looked()
        
    def member_ate(self, key, effort, food):
        if key not in self.dead:
            return self.members[key].eat(effort, food)
        return 0
    
    def member_was_attacked(self, key, attack):
        if key not in self.dead:
            amt = self.members[key].was_attacked(attack)
            if amt != 0:
                self.remove_member(key)
            return amt
        return 0
    
    def member_attacked(self, key, attack):
        if key not in self.dead:
            self.members[key].attacked(attack)

class Animal():

    def __init__(self, species, key, p1 = -1, p2 = -1):
        self.species = species
        self.key = key
        self.net = species.member_nets[key]
        self.location = [0,0]
        self.speed = 0
        self.direction = 0
        self.energy = 50
        self.health = 50
        self.food = 50
        self.sex = random.randint(0,1)
        self.parents = [p1, p2]
        self.get_genes(p1, p2)
        self.look = 0
        self.age = 0
    
    def set_location(self, loc):
        self.location[0] = max(min(self.species.size*self.species.scale-1, loc[0]),0)
        self.location[1] = max(min(self.species.size*self.species.scale-1, loc[1]),0)
        
    def get_input(self, all, i, real = True):
        sighted = -1
        min_dist = 1
        direction = 0
        num_spec = self.species.num_spec
        if self.look:   # Will see the closest animal [yes/no for each species, distance,direction]
                        # within sight range (10*scale)
            if real: self.look = False
            for s in range(len(all)):
                for k,v in all[s].items():
                    if s == i and k == self.key: continue
                    d = get_dist(v[0],self.location)/(10*self.species.scale)
                    if d < min_dist:
                        sighted = s
                        min_dist = d
                        direction = ((get_direction(v[0],self.location)-self.direction+math.pi)\
                            % (2*math.pi)-math.pi)/math.pi
        output = []
        for j in range(num_spec):
            output.append(sighted==j)
        output.extend([min_dist*(min_dist!=1),direction,all[i][self.key][3]/100.,
            min(1,self.health/100.),min(1,self.energy/100.)])
        return output
    
    def get_output(self, input):
        output = self.net.run(input)
        output[0] = 2/(1+math.exp(-output[0]))-1
        output[1] = output[1]/10*3.14/8
        output[2] = 2/(1+math.exp(-output[2]))-1
        output[3] = 2/(1+math.exp(-output[3]))-1
        if self.health*self.energy < 8000: output[4] = 0
        return output
        
    def take_turn(self, all, i):
        input = self.get_input(all, i)
        output = self.get_output(input)
        self.energy -= 0.005*self.age
        if self.energy < self.food and self.food > 0:
            self.energy += 1
            self.food -= 1
        if self.health < min(self.food,99) and self.food > 0:
            self.health += 1
            self.food -= 1
        self.health = min(self.health, 100)
        if self.energy < 0:
            died = self.species.member_was_attacked(self.key,-0.5*self.energy)
            if died: return [0,0,0,0,0,0]
        self.location[0] += self.speed * math.cos(self.direction)
        self.location[1] += self.speed * math.sin(self.direction)
        if self.location[0] < 0: self.location[0] = 0
        while self.location[0] >= self.species.size*self.species.scale:
            self.location[0] -= 1
        if self.location[1] < 0: self.location[1] = 0
        while self.location[1] >= self.species.size*self.species.scale:
            self.location[1] -= 1
        self.age += 1/400.
        return output
    
    def set_speed(self, val):
        self.speed = val*self.species.scale/15
        self.energy -= abs(val)*(1+self.speed_energy)/ENERGY_RATE
    
    def turn(self, val):
        self.direction += val
    
    def looked(self):
        self.look = True
        # self.energy -= (1+self.look_energy)/ENERGY_RATE
    
    def eat(self, effort, food):
        amt = food*effort/(1+self.eat_rate)*FOOD_RATE
        self.food += amt
        self.energy -= effort*(1+self.eat_energy)/ENERGY_RATE
        return amt
    
    def was_attacked(self, attack):
        self.health -= attack*(1+self.defense)*ATTACK_FACTOR
        if self.health <= 0:
            return min(max(1,self.food*2),FOOD_DROP)
        else: return 0
    
    def attacked(self, attack):
        self.energy -= attack*(1+self.attack_energy)/ENERGY_RATE
    
    def get_genes(self, p1, p2):
        self.speed_energy = self.look_energy = self.eat_rate = 0
        self.eat_energy = self.defense = self.attack_energy = 0
        def sum_genes():
            s = self.speed_energy + self.look_energy + self.eat_rate
            s += self.eat_energy + self.defense + self.attack_energy
            return s
        if p1 == -1:
            while sum_genes() < 25:
                self.speed_energy = 10*math.sin(math.pi*random.random())
                self.look_energy = 10*math.sin(math.pi*random.random())
                self.eat_rate = 10*math.sin(math.pi*random.random())
                self.eat_energy = 10*math.sin(math.pi*random.random())
                self.defense = 10*math.sin(math.pi*random.random())
                self.attack_energy = 10*math.sin(math.pi*random.random())
        else:
            p1a = self.species.members[p1]
            p2a = self.species.members[p2]
            self.speed_energy = p1a.speed_energy+random.random()* \
                (p2a.speed_energy-p1a.speed_energy)
            self.look_energy = p1a.look_energy+random.random()* \
                (p2a.look_energy-p1a.look_energy)
            self.eat_rate = p1a.eat_rate+random.random()* \
                (p2a.eat_rate - p1a.eat_rate)
            self.eat_energy = p1a.eat_energy+random.random()* \
                (p2a.eat_energy - p1a.eat_energy)
            self.defense = p1a.defense + random.random()* \
                (p2a.defense - p1a.defense)
            self.attack_energy = p1a.attack_energy + random.random()* \
                (p2a.attack_energy-p1a.attack_energy)
            