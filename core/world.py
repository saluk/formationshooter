import random
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
            if self.squads[0].formation == self.formations["right"]:
                self.movement = [1,0]

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