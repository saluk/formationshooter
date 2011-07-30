import random
import math
import pygame

class Position:
    def __init__(self,pos,rot):
        self.pos = pos
        self.rot = rot
    def realpos(self,spread=32):
        return [320//2+self.pos[0]*spread,240//2+self.pos[1]*spread]

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
            rp = p.realpos()
            cd = (rp[0]-u.pos[0])**2+(rp[1]-u.pos[1])**2
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
        self.graphics = None
        self.surface = None
        self.pos = pos
        self.rot = rot
        self.art = art
        self.hotspot = [16,16]
        self.rotation_on_rot = True
    def load(self,art=None):
        if not art:
            art = self.art
        if not art in memory:
            memory[art] = pygame.image.load(art).convert()
            memory[art].set_colorkey([255,0,255])
        self.graphics = memory[art]
        self.surface = self.graphics
    def update(self,world):
        if self.rotation_on_rot and self.surface:
            ang = {(1,0):0,(0,-1):90,(-1,0):180,(0,1):270}[tuple(self.rot)]
            self.surface = pygame.transform.rotate(self.graphics,ang)
        world.sprites.append(self)
    def draw(self,engine):
        if not self.surface and self.art:
            self.load()
        engine.surface.blit(self.surface,[self.pos[0]-self.hotspot[0],self.pos[1]-self.hotspot[1]])

class ScrollingBackground(Agent):
    def __init__(self,*args,**kwargs):
        super(ScrollingBackground,self).__init__(*args,**kwargs)
        self.hotspot = [0,0]
        self.speed = [-0.5,0]
        self.scroll = [0,0]
    def update(self,world):
        self.scroll[0]+=self.speed[0]
        self.scroll[1]+=self.speed[1]
        if self.scroll[0]>320:
            self.scroll[0]-=320
        if self.scroll[0]<-320:
            self.scroll[0]+=320
        print self.scroll
        if self.graphics:
            self.surface = self.graphics.convert()
            self.surface.blit(self.graphics,[int(self.scroll[0]),self.scroll[1]])
            self.surface.blit(self.graphics,[int(self.scroll[0])+320,self.scroll[1]])
        
class Unit(Agent):
    def __init__(self,*args,**kwargs):
        super(Unit,self).__init__(*args,**kwargs)
        self.formation_pos = None
        self.max_speed = 3
    def set_formation_position(self,p):
        self.formation_pos = p
    def update(self,world,spread):
        #head towards formation spot
        if self.formation_pos:
            rp = self.formation_pos.realpos(spread)
            change = [0,0]
            dx = rp[0]-self.pos[0]
            dy = rp[1]-self.pos[1]
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
        self.spread = 1
    def set_formation(self,formation):
        self.formation = formation
        self.formation.assign_units(self.units)
    def update(self,world):
        spread = 16*self.spread
        for u in self.units:
            u.update(world,spread)

class World:
    def __init__(self,engine):
        self.background = None
        self.sprites = []
        self.bullets = []
        self.squads = []
        self.enemies = []
        self.engine = engine
        self.formations = {}
    def update(self):
        self.sprites = []
        self.background.update(self)
        [b.update(self) for b in self.bullets]
        [s.update(self) for s in self.squads]
        [e.update(self) for e in self.enemies]
    def draw(self):
        if self.background:
            self.background.draw(self.engine)
        [s.draw(self.engine) for s in self.sprites]
    def select_formation(self,i):
        formation = self.formations[i]
        self.squads[0].set_formation(formation)
    def change_spread(self):
        s = self.squads[0]
        if s.spread==1:
            s.spread = 3
        else:
            s.spread = 1
    def level1(self):
        self.background = ScrollingBackground("art/bg/grassbleh.png")
        formation = Formation()
        formation.positions = [Position([0,0],[1,0]),Position([0,1],[1,0]),Position([0,-1],[1,0])]
        self.formations["right"] = formation
        formation = Formation()
        formation.positions = [Position([0,0],[0,-1]),Position([-1,0],[0,-1]),Position([1,0],[0,-1])]
        self.formations["up"] = formation
        formation = Formation()
        formation.positions = [Position([0,0],[0,1]),Position([-1,0],[0,1]),Position([1,0],[0,1])]
        self.formations["down"] = formation
        formation = Formation()
        formation.positions = [Position([0,0],[-1,0]),Position([0,1],[-1,0]),Position([0,-1],[-1,0])]
        self.formations["left"] = formation
        squad = Squad()
        squad.units.append(Unit("art/fg/unit.png"))
        squad.units.append(Unit("art/fg/unit.png"))
        squad.units.append(Unit("art/fg/unit.png"))
        squad.set_formation(formation)
        self.squads = [squad]