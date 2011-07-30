import pygame
import math

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
        if not world.movement[0]:
            return
        self.scroll[0]+=self.speed[0]
        self.scroll[1]+=self.speed[1]
        if self.scroll[0]>320:
            self.scroll[0]-=320
        if self.scroll[0]<-320:
            self.scroll[0]+=320
        if self.graphics:
            self.surface = self.graphics.convert()
            self.surface.blit(self.graphics,[int(self.scroll[0]),self.scroll[1]])
            self.surface.blit(self.graphics,[int(self.scroll[0])+320,self.scroll[1]])
            
class Bullet(Agent):
    def update(self,world):
        self.pos[0]+=self.rot[0]*4
        self.pos[1]+=self.rot[1]*4
        super(Bullet,self).update(world)
        
class Unit(Agent):
    def __init__(self,*args,**kwargs):
        super(Unit,self).__init__(*args,**kwargs)
        self.formation_pos = None
        self.max_speed = 3
        
        self.fire_rate = 30
        self.next_bullet = self.fire_rate
    def set_formation_position(self,p):
        self.formation_pos = p
        self.next_bullet = self.fire_rate
    def shoot(self,world):
        sp = [self.pos[0]+16*self.rot[0],self.pos[1]+16*self.rot[1]]
        b = Bullet("art/fg/bullet.png",sp,self.rot)
        world.bullets.append(b)
    def update(self,world,spread,center):
        #head towards formation spot
        if self.formation_pos:
            rp = self.formation_pos.realpos(spread)
            rp[0]+=center[0]*64
            rp[1]+=center[1]*64
            change = [0,0]
            dx = rp[0]-self.pos[0]
            dy = rp[1]-self.pos[1]
            if dx==0:
                if dy:
                    change = [0,dy/abs(dy)*min(self.max_speed,abs(dy))]
            else:
                slope = dy/float(dx)
                if dx**2+dy**2<=self.max_speed**2:
                    change = [dx,dy]
                else:
                    ang = math.atan2(dy,dx)
                    dx = math.cos(ang)*self.max_speed
                    dy = math.sin(ang)*self.max_speed
                    change = [dx,dy]
            #~ if change[0] or change[1]:
                #~ self.next_bullet += 2
            self.pos[0]+=change[0]
            self.pos[1]+=change[1]
            self.rot = self.formation_pos.rot
        #fire
        self.next_bullet-=1
        if self.next_bullet<=0:
            self.shoot(world)
            self.next_bullet = self.fire_rate
        super(Unit,self).update(world)