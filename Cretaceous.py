''' This is an evolution simulator which attempts to emulate
    predatory and vegetarian relationships. We may have evolving
    plants, but we will definitely have evolving animals.
    Sexual reproduction.
'''
import Board as b #, Plant as p, Animal as a
import pygame as pg, numpy as np
from pygame.locals import *

def get_dist(r1, r2):
    x1, y1 = r1
    x2, y2 = r2
    return ((x2-x1)**2+(y2-y1)**2)**0.5
    
def go():
    screen = pg.display.set_mode((width,height))
    font = pg.font.SysFont('arial', 14)
    zoom = 1
    render = 1
    x = 0
    y = 0
    b = board.b
    img = pg.Surface((width-200, height))
    for i in range(size):
        for j in range(size):
            col = Color(0,0,0)
            if b[i][j] != 0:
                col.hsla = b[i][j]*130,25,25
            pg.draw.rect(img,col,(i*scale,j*scale,scale,scale))
    screen.blit(img,(0,0))
    text_img = pg.Surface((100, height))
    ans_img = pg.Surface((100,height))
    text_img.fill((0,0,0))
    ans_img.fill((0,0,0))
    text_img.blit(font.render("Time:",0,(255,255,255)),(0,10))
    text_img.blit(font.render("Mouse square:",0,(255,255,255)),(0,30))
    text_img.blit(font.render("Square value:",0,(255,255,255)),(0,50))
    text_img.blit(font.render("Square default:",0,(255,255,255)),(0,70))
    text_img.blit(font.render("Animal:",0,(255,255,255)),(0,90))
    text_img.blit(font.render("Spd E:",0,(255,255,255)),(0,110))
    text_img.blit(font.render("Look E:",0,(255,255,255)),(0,130))
    text_img.blit(font.render("Eat Rt:",0,(255,255,255)),(0,150))
    text_img.blit(font.render("Eat E:",0,(255,255,255)),(0,170))
    text_img.blit(font.render("Def:",0,(255,255,255)),(0,190))
    text_img.blit(font.render("Atk E:",0,(255,255,255)),(0,210))
    text_img.blit(font.render("Health:",0,(255,255,255)),(0,230))
    text_img.blit(font.render("Energy:",0,(255,255,255)),(0,250))
    text_img.blit(font.render("Food:",0,(255,255,255)),(0,270))
    text_img.blit(font.render("Age:",0,(255,255,255)),(0,290))
    text_img.blit(font.render("Parents:",0,(255,255,255)),(0,310))
    text_img.blit(font.render("Neural Net:",0,(255,255,255)),(0,330))
    screen.blit(text_img,(width-200,0))
    pg.display.flip()
    surf = pg.Surface((6,6))
    loopcounter = years = -1
    mx_b = my_b = mx = my = 0
    id_lock = 0
    history = []
    while True:
        loopcounter += 1
        if loopcounter % 400 == 0:
            loopcounter = 0
            years += 1
            print("Year: %d" %years)
            print("Total population: %d" %board.get_population())
            print("Average health: %d" %board.get_avg_health())
            print("Help count: %d\n" %board.help_count)
            board.help_count = 0
            lis = []
            hist_cols = {}
            for s, l in board.species.items():
                lis.append(len(l.members))
                hist_cols[s] = l.color
            history.append(lis)
            history = history[-100:]
            graph = get_histogram(history, hist_cols,font)
            screen.blit(text_img,(width-200,0))
            population = board.get_population()
            if population <= board.min_pop:
                board.species[0].inc_ENERGY_RATE()
            if population > 75:
                board.species[0].dec_ENERGY_RATE()
        clock.tick(30*render)
        for e in pg.event.get():
            if e.type == QUIT: return 0
            if e.type == MOUSEBUTTONDOWN:
                id_lock = 1 - id_lock
            if e.type == KEYDOWN:
                render = 1 - render
        if render:
            locations = []
            colors = []
            ids = []
            min_d = 10
            if id_lock == 0:
                id = [-1,-1]
            for sk,s in board.animals.items():
                for k,v in s.items():
                    if loopcounter %3 == 0 and sk == id[0] and k == id[1]: continue
                    locations.append(v[0])
                    colors.append(v[2])
                    ids.append([sk,k])
            ans_img.fill((0,0,0))
            if pg.mouse.get_focused():
                mx, my = pg.mouse.get_pos()
                mx_b, my_b = mx//scale, my//scale
            if mx_b >= 0 and mx_b < size and my_b >= 0 and my_b < size:
                ans_img.blit(font.render(str(years+int(loopcounter/4)/100.),0,(255,255,255)),(0,10))
                ans_img.blit(font.render(str((mx_b, my_b)),0,(255,255,255)),(0,30))
                board.update_square(mx_b,my_b)
                ans_img.blit(font.render(str(board.b[mx_b][my_b]),0,(255,255,255)),(0,50))
                ans_img.blit(font.render(str(board.default[mx_b][my_b]),0,(255,255,255)),(0,70))
                for i in range(len(locations)):
                    d = get_dist([mx,my],locations[i])
                    if d < min_d:
                        min_d = d
                        if id_lock == 0:
                            id = ids[i]
                if id[0] != -1:
                    ans_img.blit(font.render(str(id),0,(255,255,255)),(0,90))
                    if id[1] not in board.species[id[0]].dead:
                        a = board.species[id[0]].members[id[1]]
                        ans_img.blit(font.render(str(a.speed_energy),0,(255,255,255)),(0,110))
                        ans_img.blit(font.render(str(a.look_energy),0,(255,255,255)),(0,130))
                        ans_img.blit(font.render(str(a.eat_rate),0,(255,255,255)),(0,150))
                        ans_img.blit(font.render(str(a.eat_energy),0,(255,255,255)),(0,170))
                        ans_img.blit(font.render(str(a.defense),0,(255,255,255)),(0,190))
                        ans_img.blit(font.render(str(a.attack_energy),0,(255,255,255)),(0,210))
                        ans_img.blit(font.render(str(int(a.health)),0,(255,255,255)),(0,230))
                        ans_img.blit(font.render(str(int(a.energy)),0,(255,255,255)),(0,250))
                        ans_img.blit(font.render(str(int(a.food)),0,(255,255,255)),(0,270))
                        ans_img.blit(font.render(str(int(a.age*10)/10.),0,(255,255,255)),(0,290))
                        ans_img.blit(font.render(str(a.parents),0,(255,255,255)),(0,310))
                        ans_img.blit(get_net_img(id[0],id[1]),(0,330))
            screen.blit(img,(0,0))
            screen.blit(ans_img,(width-100,0))
            screen.blit(graph,(width-200,height-100))
            for i in range(len(locations)):
                surf.fill(colors[i])
                screen.blit(surf,locations[i])
            pg.display.flip()
        board.go()
        
def get_net_img(skey, akey):
    # Just gives an image that helps visualize what the neural net is doing
    img = pg.Surface((150,500))
    img.fill((0,0,0))
    def get_col(val):
        return ((val<0)*min(1,-val)*255,(val>0)*min(1,val)*255,0)
    square = 10
    net = board.species[skey].member_nets[akey]
    n = net.nodes
    w = net.weights
    nodes = []
    layer = board.species[skey].members[akey].get_input(board.animals, skey, False)
    for i in range(len(n)):
        nodes.append([])
        for j in range(n[i]):
            nodes[i].append(pg.Surface((square,square)))
            col = get_col(layer[j])
            nodes[i][j].fill(col)
        if i < len(n)-1:
            layer = np.dot(layer, w[i])
        if i < len(n)-2:
            layer = net.activation(layer)
    for i in range(len(nodes)):
        for j in range(len(nodes[i])):
            img.blit(nodes[i][j],(i*(square+10),j*(square+10)))
    for i in range(len(w)):
        s1, s2 = np.shape(w[i])
        for j in range(s1):
            for k in range(s2):
                pg.draw.line(img, get_col(w[i][j,k]),
                    ((i+0.5)*(square+10)-5, (j+0.5)*(square+10)-5),
                    ((i+1.5)*(square+10)-5, (k+0.5)*(square+10)-5),
                    2)
    return img

def get_histogram(history, colors,font):
    graph = pg.Surface((200,100))
    graph.fill((0,0,0))
    max_sum = 0
    for i in range(len(history)):
        max_sum = float(max(max_sum, sum(history[i])))
    for i in range(len(history)):
        part_sum = 0
        for j in range(len(history[i])):
            pg.draw.rect(graph,colors[j],(i*200/len(history),100*(1-(part_sum+history[i][j])/max_sum),200/len(history),100*history[i][j]/max_sum))
            part_sum += history[i][j]
    graph.blit(font.render("POP: "+str(sum(history[-1])),0,(125,125,125)),(0,0))
    return graph

if __name__ == '__main__':
    scale = 10
    size = 60
    seed = 0 # 299226 # 31523 100535
    pop = 24
    spec = 4
    
    pg.init()
    clock = pg.time.Clock()
    pg.display.init()
    pg.font.init()
    width, height = (size*scale+200,size*scale)
    board = b.Board(clock,size,scale,seed, pop, spec)
    go()