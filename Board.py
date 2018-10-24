''' Board class manages board and game'''
import random, math
import Animal as a
#import matplotlib.pyplot as plt
#import numpy as np

def get_dist(r1, r2):
    x1, y1 = r1
    x2, y2 = r2
    return ((x2-x1)**2+(y2-y1)**2)**0.5
    
class Board():

    def __init__(self, clock, size = 75, scale = 5, seed = 0, min_pop = 25, min_species = 5):
        if seed == 0: seed = random.randint(1,1000000)
        print(seed)
        self.clock = clock
        self.size = size
        self.scale = scale
        self.b, self.default, self.t = self.make_board(seed, size)
        self.min_pop = min_pop
        self.min_species = min_species
        self.animals = {} # Stores visible characteristics that can be passed to other animals
        self.next_key = 0
        self.help_count = 0
        self.populate(min_species, min_pop)
        self.time = 0
        
    def make_board(self, seed, size):
        random.seed(seed)
        size2pi = 2*math.pi*size
        xshift = random.randint(0,size+1)
        yshift = random.randint(0,size+1)
        wetness = 0.1+random.random()/3
        board = []
        default = []
        t = []
        maxv = -1000
        minv = 1000
        octaves = random.randint(3,10)
        freqx = []
        freqy = []
        for i in range(octaves):
            freqx.append(random.random())
            freqy.append(random.random())
        for i in range(size):
            board.append([])
            default.append([])
            t.append([])
            for j in range(size):
                val = 0
                for o in range(1,octaves+1):
                    val += (octaves-o)**0.5*(math.sin(o**2*freqx[o-1]*(i+xshift)/(size)) * \
                        math.sin(o**2*freqy[o-1]*(j+yshift)/(size)))
                maxv = max(maxv, val)
                minv = min(minv, val)
                board[i].append(val)
        for i in range(size):
            for j in range(size):
                board[i][j] = (board[i][j]-minv)/(maxv-minv)
                board[i][j] = max(0,(board[i][j]-wetness)/(1-wetness))
                default[i].append(board[i][j]*100)
                t[i].append(0)
        print("%f, %f, wet %f, o %d" %(maxv, minv, wetness, octaves))
        return board, default, t
     
    def populate(self, min_species, min_pop):
        self.species = {}
        for s in range(min_species):
            location = [random.random()*self.scale*self.size, 
                random.random()*self.scale*self.size]
            self.species[self.next_key] = a.Species(self.next_key,
                random.randint(0,3), random.randint(1,10),location,self.size,
                self.scale, self.min_species)
            self.next_key += 1
            if s < min_species - 1:
                spop = int(min_pop/min_species -3+ (random.random()*5-2.5)**2)
            else:
                spop = min_pop/min_species
            for i in range(spop):
                self.species[s].add_member()

    def get_population(self):
        sum = 0
        for s in self.animals.values():
            sum += len(s)
        return sum
        
    def get_avg_health(self):
        sum = 0
        for s in self.animals.values():
            for v in s.values():
                sum += v[1]
        pop = self.get_population()
        if pop == 0: return 0
        else: return sum/pop
    
    def was_eaten(self,x,y,amt):
        self.b[x][y] -= amt/1.5
    
    def update_square(self, x,y):
        diff = self.default[x][y] - self.b[x][y]
        diff = diff*0.999**(self.time-self.t[x][y])
        self.b[x][y] = self.default[x][y] - diff
        self.t[x][y] = self.time
        
    def go(self):
        self.time += 1
        # First update animal informaion
        self.animals = {}  
        for k,s in self.species.items():
            d = {}
            keys,locs,health,colors = s.get_details()
            for i in range(len(locs)):
                d[keys[i]] = [locs[i],health[i],colors[i]]
                x,y = locs[i]
                x = int(x/self.scale)
                y = int(y/self.scale)
                self.update_square(x,y)
                d[keys[i]].append(self.b[x][y])
            self.animals[k] = d
        # Then give information to each animal
        # And see what they do with it
        self.actions = []
        for i,s in self.species.items():
            self.actions.append(s.take_turn(self.animals))
            
        # Now evaluate actions and tell the animals what changed 
        for s in range(len(self.actions)):  # A dict of actions made by each animal
            for key, a in self.actions[s].items():   # A list of actions made by one animal
                if key in self.species[s].dead: continue
                
                x,y = self.animals[s][key][0]
                x = int(x/self.scale)
                y = int(y/self.scale)
                # Action format: [speed, turn, look, eat, fight, breed]
                self.species[s].member_looked(key)
                self.species[s].change_speed(key,a[0])
                self.species[s].add_direction(key,a[1])
                if a[2]>0:
                    amt = self.species[s].member_ate(key,a[2],self.b[x][y])
                    self.was_eaten(x,y,amt)
                if a[3]>0: # Will attack closest animal within range (scale)
                    min_dist = self.scale
                    for sp in range(len(self.animals)):
                        if sp == s: continue
                        for k, v in self.animals[sp].items():
                            d = get_dist(v[0], self.animals[s][key][0])
                            if d < min_dist:
                                min_dist = d
                                attacked = [sp, k]
                    if min_dist != self.scale:
                        died = self.species[attacked[0]].member_was_attacked(attacked[1],a[3])
                        if died != 0:
                            self.b[x][y] += died
                        self.species[s].member_attacked(key,a[3])
                if a[4] > 0: # Will breed with closest animal of same species within range
                    min_dist = self.scale
                    for k, v in self.species[s].members.items():
                        if k == key: continue
                        #if v.sex + \
                        #    self.species[s].members[key].sex != 1: continue
                        d = get_dist(v.location, self.species[s].members[key].location)
                        if d < min_dist:
                            min_dist = d
                            co_parent = k
                    if min_dist != self.scale:
                        self.species[s].breed(key, k)
        if self.get_population() < 4*self.min_pop:
            for k,s in self.animals.items():
                if len(s) < self.min_pop/self.min_species:
                    self.species[k].add_member()
                    self.help_count += 1