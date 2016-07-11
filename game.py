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

        self.screen = pygame.display.set_mode((self.width, self.height))

    def LoadSprites(self):
        """Load the sprites that we need"""

    def Run(self):
        self.LoadSprites();
        self.MainLoop();

    def UpdateFrame(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()

    def RenderFrame(self):
        """Draw any sprites"""

    def MainLoop(self):
        """This is the Main Loop of the Game"""
        while 1:
            self.UpdateFrame();
            self.RenderFrame();

if __name__ == "__main__":
    MainWindow = PyManMain()
    MainWindow.Run()
