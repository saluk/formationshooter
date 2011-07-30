import pygame

class Controller:
    def __init__(self,engine):
        self.engine = engine
    def input(self):
        pygame.event.pump()
        for e in pygame.event.get():
            if e.type==pygame.ACTIVEEVENT:
                if e.gain==0 and (e.state==6 or e.state==2 or e.state==4):
                    print "minimize"
                    self.engine.pause()
                if e.gain==1 and (e.state==6 or e.state==2 or e.state==4):
                    print "maximize"
                    self.engine.unpause()
            if e.type==pygame.VIDEORESIZE:
                w,h = e.w,e.h
                engine.swidth = w
                engine.sheight = h
                engine.make_screen()
            if e.type == pygame.QUIT:
                self.engine.stop()
            if e.type==pygame.KEYDOWN and\
            e.key==pygame.K_RETURN and pygame.key.get_mods() & pygame.KMOD_ALT:
                engine.fullscreen = 1-engine.fullscreen
                engine.make_screen()