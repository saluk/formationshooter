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
    def __init__(self):
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
            u.update(world,spread,self.center)

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
    def update(self):
        self.sprites = []
        
        self.movement = [0,0]
        if self.formations:
            if self.squads[0].formation == self.formations["rightline"]:
                self.movement = [1,0]

        self.background.update(self)
        [b.update(self) for b in self.bullets]
        [s.update(self) for s in self.squads]
        [e.update(self) for e in self.enemies]
    def draw(self):
        if self.background:
            self.background.draw(self.engine)
        [s.draw(self.engine) for s in self.sprites]
        x = 0
        for form in self.formations.values():
            if form == self.squads[0].formation:
                pygame.draw.rect(self.engine.surface,[255,0,0],[[x,0],[17,17]])
            if form.icon:
                form.icon.pos = [x+1,1]
                form.icon.draw(self.engine)
            x+=16
    def select_formation(self,i):
        formation = self.formations[i]
        self.squads[0].set_formation(formation)
    def change_spread(self):
        s = self.squads[0]
        if s.spread==1:
            s.spread = 3
        else:
            s.spread = 1
    def center(self,dir):
        dx,dy = dir
        s = self.squads[0]
        s.center[0]+=dx
        s.center[1]+=dy
        if s.center[1]<-1:
            s.center[1]=-1
        if s.center[1]>1:
            s.center[1]=1
        print s.center
    def level1(self):
        self.background = ScrollingBackground("art/bg/grassbleh.png")
        for formimg in os.listdir("art/formations"):
            formation = Formation()
            formation.load("art/formations/"+formimg)
            self.formations[formimg.replace(".png","")] = formation
        squad = Squad()
        for i in range(8):
            squad.units.append(Unit("art/fg/unit.png"))
        squad.set_formation(formation)
        self.squads = [squad]