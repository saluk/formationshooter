import random
import math
import pygame

class Position:
    def __init__(self,pos,rot):
        self.pos = [320//2+pos[0]*32,240//2+pos[1]*32]
        self.rot = rot

class Formation:
    def __init__(self):
        self.positions = []
    def assign_units(self,units):
        open = self.positions[:]
        for u in units:
            pos = self.find_pos(u,open)
            open.remove(pos)
            u.set_formation_position(pos)
    def find_pos(self,u,positions):
        best = None
        d = 1000
        for p in positions:
            if not best:
                best = p
                continue
            cd = (p.pos[0]-u.pos[0])**2+(p.pos[1]-u.pos[1])**2
            if cd<d:
                best = p
                d = cd
        return best

memory = {}
class Agent(object):
    def __init__(self,art,pos=None,rot=None):
        if not pos:
            pos = [0,0]
        if not rot:
            rot = [1,0]
        self.surface = None
        self.pos = pos
        self.rot = rot
        self.art = art
        self.hotspot = [16,16]
    def load(self,art=None):
        if not art:
            art = self.art
        if not art in memory:
            memory[art] = pygame.image.load(art).convert()
        self.surface = memory[art]
    def update(self,world):
        world.sprites.append(self)
    def draw(self,engine):
        if not self.surface and self.art:
            self.load()
        engine.surface.blit(self.surface,[self.pos[0]-self.hotspot[0],self.pos[1]-self.hotspot[1]])
        
class Unit(Agent):
    def __init__(self,*args,**kwargs):
        super(Unit,self).__init__(*args,**kwargs)
        self.formation_pos = None
        self.max_speed = 3
    def set_formation_position(self,p):
        self.formation_pos = p
    def update(self,world):
        #head towards formation spot
        if self.formation_pos:
            change = [0,0]
            dx = self.formation_pos.pos[0]-self.pos[0]
            dy = self.formation_pos.pos[1]-self.pos[1]
            if dx==0:
                if dy:
                    change = [0,dy/abs(dy)*self.max_speed]
            else:
                slope = dy/float(dx)
                if dx**2+dy**2<self.max_speed**2:
                    change = [dx,dy]
                else:
                    ang = math.atan2(dy,dx)
                    dx = math.cos(ang)*self.max_speed
                    dy = math.sin(ang)*self.max_speed
                    change = [dx,dy]
            self.pos[0]+=change[0]
            self.pos[1]+=change[1]
            self.rot = self.formation_pos.rot
        super(Unit,self).update(world)
        
class Squad:
    def __init__(self):
        self.formation = None
        self.units = []
    def update(self,world):
        self.formation.assign_units(self.units)
        for u in self.units:
            u.update(world)

class World:
    def __init__(self,engine):
        self.background = None
        self.sprites = []
        self.bullets = []
        self.squads = []
        self.enemies = []
        self.engine = engine
        self.formations = []
    def update(self):
        self.sprites = []
        [b.update(self) for b in self.bullets]
        [s.update(self) for s in self.squads]
        [e.update(self) for e in self.enemies]
    def draw(self):
        if self.background:
            self.background.draw(self.engine)
        [s.draw(self.engine) for s in self.sprites]
    def level1(self):
        formation = Formation()
        formation.positions = [Position([0,0],[1,0]),Position([0,1],[1,0]),Position([0,-1],[1,0])]
        self.formations.append(formation)
        formation = Formation()
        formation.positions = [Position([0,0],[0,1]),Position([-1,0],[0,1]),Position([1,0],[0,1])]
        self.formations.append(formation)
        squad = Squad()
        squad.formation = formation
        squad.units.append(Unit("art/fg/unit.png"))
        squad.units.append(Unit("art/fg/unit.png"))
        squad.units.append(Unit("art/fg/unit.png"))
        self.squads = [squad]