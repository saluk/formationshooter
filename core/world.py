import pygame
import random
import os
from agents import *

class Position:
    def __init__(self,pos,rot):
        self.pos = pos
        self.rot = rot
    def realpos(self,spread=32):
        return [320//2+self.pos[0]*spread,240//2+self.pos[1]*spread]

class Formation:
    def __init__(self,name):
        self.name = name
        self.positions = []
        self.icon = None
    def order_positions(self):
        """Sorts positions starting with the center"""
        self.positions.sort(key=lambda p:(p.pos[0])**2+(p.pos[1])**2)
    def assign_units(self,units):
        self.order_positions()
        open = units[:]
        for p in self.positions:
            u = self.find_unit(p,open)
            if not u:
                continue
            open.remove(u)
            u.set_formation_position(p)
        #~ for u in units:
            #~ pos = self.find_pos(u,open)
            #~ if not pos:
                #~ continue
            #~ open.remove(pos)
            #~ u.set_formation_position(pos)
    def find_unit(self,p,units):
        best = None
        d = 1000
        rp = p.realpos()
        for u in units:
            if not best:
                best = u
                continue
            cd = (rp[0]-u.pos[0])**2+(rp[1]-u.pos[1])**2
            if cd<d:
                best = u
                d = cd
        return best
    def find_pos(self,u,positions):
        best = None
        d = 1000
        for p in positions:
            if not best:
                best = p
                continue
            rp = p.realpos()
            cd = (rp[0]-u.pos[0])**2+(rp[1]-u.pos[1])**2
            if cd<d:
                best = p
                d = cd
        return best
    def load(self,image):
        self.icon = Agent(image)
        self.icon.hotspot = [0,0]
        self.icon.load()
        image = pygame.image.load(image)
        si = image.get_size()
        c = [si[0]//2,si[1]//2]
        y=0
        while y<si[1]:
            x = 0
            while x<si[0]:
                index = image.map_rgb(image.get_at((x,y)))
                dir = None
                if index==0:
                    dir=[1,0]
                elif index==1:
                    dir=[0,-1]
                elif index==2:
                    dir=[0,1]
                elif index==3:
                    dir=[-1,0]
                if dir:
                    self.positions.append(Position([x-c[0],y-c[1]],dir))
                x+=1
            y+=1
        
class Squad:
    def __init__(self):
        self.formation = None
        self.units = []
        self.spread = 1
        self.center = [0,0]
    def set_formation(self,formation):
        self.formation = formation
        self.formation.assign_units(self.units)
    def update(self,world):
        spread = 16*self.spread
        for u in self.units:
            u.spread = spread
            u.center = self.center
            u.update(world)
    def force(self):
        """Force all units into their positions"""
        for u in self.units:
            u.pos = u.formation_pos.realpos(16*self.spread)
    def remove_unit(self,u):
        if u in self.units:
            self.units.remove(u)
            self.set_formation(self.formation)

class World:
    def __init__(self,engine):
        self.background = None
        self.sprites = []
        self.bullets = []
        self.squads = []
        self.enemies = []
        self.engine = engine
        self.formations = {}
        self.movement = [1,0]
        self.step = 0
        self.score = 0
    def collide(self,agent,type):
        all = self.enemies[:]
        for s in self.squads:
            all.extend(s.units)
        ret = []
        p = agent.pos
        for u in all:
            r = u.rect()
            if r.collidepoint(p):
                ret.append(u)
        return ret
    def remove_unit(self,u):
        """Hacky remove"""
        if u in self.enemies:
            self.score += 1
            return self.enemies.remove(u)
        for s in self.squads:
            if u in s.units:
                s.remove_unit(u)
                if not s.units:
                    self.level1()
    def remove_bullet(self,b):
        if b in self.bullets:
            self.bullets.remove(b)
    def set_enemy_pos(self,e,pos,offset):
        d,ai=pos[:2],pos[2:]
        if d=="xx":
            e.pos[0]=320+offset
            e.pos[1]=random.randint(32,240-offset)
            e.walk_angle = 180
            e.rot = [-1,0]
        elif d=="uu":
            e.pos[0]=320//2
            e.pos[1]=-offset
            e.walk_angle = 270
            e.rot = [0,1]
        elif d=="ur":
            e.pos[0]=320+offset
            e.pos[1]=2*offset
            e.walk_angle = 180
            e.rot = [-1,0]
        elif d=="rr":
            e.pos[0]=320+offset
            e.pos[1]=240//2
            e.walk_angle = 180
            e.rot = [-1,0]
        elif d=="br":
            e.pos[0]=320+offset
            e.pos[1]=240-2*offset
            e.walk_angle = 180
            e.rot = [-1,0]
        elif d=="bb":
            e.pos[0]=320//2
            e.pos[1]=240+offset
            e.walk_angle = 90
            e.rot = [0,-1]
        elif d=="ul":
            e.pos[0]=-offset
            e.pos[1]=2*offset
            e.walk_angle = 0
            e.rot = [1,0]
        elif d=="ll":
            e.pos[0]=-offset
            e.pos[1]=240//2
            e.walk_angle = 0
            e.rot = [1,0]
        elif d=="bl":
            e.pos[0]=-offset
            e.pos[1]=240-2*offset
            e.walk_angle = 0
            e.rot = [1,0]
    def make_grunt(self,pos):
        enemy = Unit("art/fg/grunt.png")
        enemy.team = "enemy"
        enemy.max_speed = 1
        self.set_enemy_pos(enemy,pos,16)
        enemy.set_fire_rate(100)
        self.enemies.append(enemy)
    def make_tank(self,pos):
        enemy = Unit("art/fg/tank.png")
        enemy.team = "enemy"
        enemy.max_speed = 0.5
        enemy.hotspot = [32,32]
        enemy.health = 20
        self.set_enemy_pos(enemy,pos,32)
        enemy.set_fire_rate(120)
        enemy.shoot_stream = True
        enemy.stream_length = 40
        self.enemies.append(enemy)
    def update(self):
        self.sprites = []
        
        self.movement = [1,0]
        #~ if self.formations:
            #~ if "_right" in self.squads[0].formation.name:
                #~ self.movement = [1,0]
        if self.movement[0]:
            self.step += self.movement[0]
            if self.level:
                if isinstance(self.level[0],float):
                    self.level[0]-=1/320.0
                    if self.level[0]<=0:
                        del self.level[0]
                else:
                    u = self.level.pop(0)
                    if u.startswith("g"):
                        self.make_grunt(u[1:])
                    elif u.startswith("t"):
                        self.make_tank(u[1:])
            #~ if self.step==2:
                #~ self.make_grunt()
            #~ if self.step==100:
                #~ self.make_tank()

        self.background.update(self)
        for b in self.bullets:
            b.update(self)
        [s.update(self) for s in self.squads]
        [e.update(self) for e in self.enemies]
    def draw(self):
        if self.background:
            self.background.draw(self.engine)
        [s.draw(self.engine) for s in self.sprites]
        x = 0
        if self.squads and self.squads[0].formation:
            for fname in ["line","corridor"]:
                dir = self.squads[0].formation.name.split("_")[1]
                form = self.formations[fname+"_"+dir]
                if form == self.squads[0].formation:
                    pygame.draw.rect(self.engine.surface,[255,0,0],[[x,0],[17,17]])
                if self.squads[0].formation.name.split("_")[1]==form.name.split("_")[1]:
                    if form.icon:
                        form.icon.pos = [x+1,1]
                        form.icon.draw(self.engine)
                    x+=16
    def select_formation(self,i):
        formation = self.formations[i]
        self.squads[0].set_formation(formation)
    def formation_dir(self,dir):
        s = self.squads[0]
        if s.formation:
            self.select_formation(s.formation.name.split("_")[0]+"_"+dir)
    def change_formation(self,form):
        s = self.squads[0]
        if s.formation:
            dir = s.formation.name.split("_")[1]
            self.select_formation(form+"_"+dir)
    def level1(self):
        self.score = 0
        self.background = ScrollingBackground("art/bg/grassbleh.png")
        for formimg in os.listdir("art/formations"):
            formation = Formation(formimg.replace(".png",""))
            formation.load("art/formations/"+formimg)
            self.formations[formation.name] = formation
        squad = Squad()
        for i in range(7):
            squad.units.append(Unit("art/fg/unit.png"))
        self.squads = [squad]
        self.select_formation("line_right")
        squad.force()
        self.level = [0.5,"grr",1.,"gll",1.2,"tur",1.,"gbr","grr",0.3,"grr","gbb",1.,"tur","gll",1.,"guu","gbb","gll","grr",1.,"guu","gbb","gll","grr",0.1,"grr",0.1,"gur",0.1,"gbr",0.1,"gur",0.1,"grr",0.1,"gbr",0.1,"tuu",0.1,"tbb"]
        self.wait = 0