import os, sys
import pygame

from pygame.locals import *
from helpers import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

class PyManMain:
    """The Main PyMan Class - This class handles the main 
    initialization and creating of the Game."""
    
    def __init__(self, width=640,height=480):
        """Initialize PyGame"""
        pygame.init()

        self.width = width
        self.height = height

        self.clock = pygame.time.Clock()

        pygame.display.set_caption("Testing")

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.fill((255, 255, 255))

    def LoadSprites(self):
        """Load the sprites that we need"""
        self.player = Player()
        self.player_sprites = pygame.sprite.RenderPlain((self.player))

    def Run(self):
        self.LoadSprites();
        self.MainLoop();

    def UpdateFrame(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()

        self.player.Update()

    def RenderFrame(self):
        """Draw any sprites"""
        self.player_sprites.draw(self.screen)
        pygame.display.flip()

    def MainLoop(self):
        """This is the Main Loop of the Game"""
        while 1:
            self.UpdateFrame()
            self.RenderFrame()
            self.clock.tick(60)

class Player(pygame.sprite.Sprite):    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) 
        self.image, self.rect = load_image('snake.png',-1)

    def Update(self):
        pressed = pygame.key.get_pressed()
        
        if pressed[K_RIGHT]:
            self.rect.move_ip(1, 0);

if __name__ == "__main__":
    MainWindow = PyManMain()
    MainWindow.Run()
