import pygame
import math
import random

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
            ang = math.atan2(-self.rot[1],self.rot[0])*180.0/math.pi
            self.surface = pygame.transform.rotate(self.graphics,ang)
        world.sprites.append(self)
    def draw(self,engine):
        if not self.surface and self.art:
            self.load()
        engine.surface.blit(self.surface,[self.pos[0]-self.hotspot[0],self.pos[1]-self.hotspot[1]])
    def rect(self):
        if not self.surface:
            return pygame.Rect([[0,0],[0,0]])
        r = self.surface.get_rect()
        r = r.move(self.pos[0]-self.hotspot[0],self.pos[1]-self.hotspot[1])
        r = r.inflate(-2,-2)
        return r
        

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
        die = False
        self.pos[0]+=self.rot[0]*4
        self.pos[1]+=self.rot[1]*4
        for col in world.collide(self,"bullet"):
            if col.team!=self.team:
                col.hit(self)
                die = 1
        if self.pos[0]<0 or self.pos[0]>320 or self.pos[1]<0 or self.pos[1]>240:
            die = 1
        if die:
            world.remove_bullet(self)
        super(Bullet,self).update(world)
        
class Unit(Agent):
    def __init__(self,*args,**kwargs):
        super(Unit,self).__init__(*args,**kwargs)
        self.formation_pos = None
        self.spread = 1
        self.center = [0,0]
        
        self.walk_angle = None
        self.max_speed = 3
        
        self.health = 2
        
        self.set_fire_rate(30)
        self.shoot_stream = False
        self.stream_length = 20
        self.stream_time = 0
        
        self.team = "player"
    def hit(self,bullet):
        self.health -= 1
    def set_fire_rate(self,spd):
        self.fire_rate = spd
        self.next_bullet = self.fire_rate
    def set_formation_position(self,p):
        self.formation_pos = p
        self.next_bullet = self.fire_rate
    def shoot(self,world):
        sp = [self.pos[0]+self.hotspot[0]*self.rot[0],self.pos[1]+self.hotspot[1]*self.rot[1]]
        b = Bullet("art/fg/bullet.png",sp,[self.rot[0],self.rot[1]])
        b.team = self.team
        world.bullets.append(b)
    def update(self,world):
        if self.health<=0:
            world.remove_unit(self)
        #head towards formation spot
        change = [0,0]
        if self.walk_angle is not None:
            ang = self.walk_angle*math.pi/180.0
            dx = math.cos(ang)*self.max_speed
            dy = -math.sin(ang)*self.max_speed
            print dx,dy
            change = [dx,dy]
        if self.formation_pos:
            rp = self.formation_pos.realpos(self.spread)
            rp[0]+=self.center[0]*64
            rp[1]+=self.center[1]*64
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
            if change[0] or change[1]:
                self.next_bullet += 2
            self.rot = self.formation_pos.rot
        #fire
        self.next_bullet-=1
        if self.next_bullet<=0:
            self.shoot(world)
            self.next_bullet = self.fire_rate
            if self.shoot_stream:
                self.stream_time += 1
                if self.stream_time>=self.stream_length:
                    self.stream_time = 0
                else:
                    self.next_bullet = 0
        super(Unit,self).update(world)
        self.pos[0]+=change[0]
        self.pos[1]+=change[1]