import os, sys
import pygame
import pytmx

from pygame.locals import *
from helpers import *
from pytmx.util_pygame import load_pygame

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

class PyManMain:
    """The Main PyMan Class - This class handles the main 
    initialization and creating of the Game."""
    
    def __init__(self, width=1280,height=640):
        """Initialize PyGame"""
        pygame.init()

        self.width = width
        self.height = height

        self.camera_x = 0
        self.camera_y = 0

        self.clock = pygame.time.Clock()

        self.coin_sound = pygame.mixer.Sound("coin.wav")

        self.score = 0
        self.score_font = pygame.font.Font('American Captain.ttf', 64)
        self.UpdateScore()

        self.collectables = []
        self.collectable_sprites = pygame.sprite.RenderPlain()

        self.obstacles = []
        self.obstacle_sprites = pygame.sprite.RenderPlain()

        pygame.display.set_caption("Testing")

        self.screen = pygame.display.set_mode((self.width, self.height))

    def Restart(self):
        self.collectables = []
        self.collectable_sprites = pygame.sprite.RenderPlain()
        self.score = 0

        self.player.rect.center = (0, 0)
        self.player.Respawn()

        self.UpdateScore()
        self.SpawnCollectables()

    def UpdateScore(self):
        self.score_text = self.score_font.render(str(self.score), True, (255, 0, 0))

    def SpawnCollectables(self):
        collectables_layer = self.tiled_map.get_layer_by_name("Collectables")
        for obj in collectables_layer:
            self.PlaceCollectable(obj.x, obj.y)

    def LoadSprites(self):
        """Load the sprites that we need"""
        self.player = Player(self)
        self.player_sprites = pygame.sprite.RenderPlain((self.player))

        self.tiled_map = load_pygame('map.tmx')
        self.tile_size = 40

        obstacles_layer = self.tiled_map.get_layer_by_name("Obstacles")
        for obj in obstacles_layer:
            self.PlaceObstacle(obj.x, obj.y)

        self.Restart()

    def ChaseCamera(self, target, rate=0.05):
        vert_offset = 80

        dest_x = target.rect.center[0] - self.width * 0.5
        dest_y = target.rect.center[1] - self.height * 0.5 - vert_offset

        self.camera_x = int(self.camera_x + (dest_x - self.camera_x) * rate)
        self.camera_y = int(self.camera_y + (dest_y - self.camera_y) * rate)

    def PlaceCollectable(self, pos_x, pos_y):
        """Add a collectable at position (pos_x, pos_y)"""
        collectable = Collectable(pos_x, pos_y)

        self.collectables.append(collectable)
        self.collectable_sprites.add(collectable)

    def PlaceObstacle(self, pos_x, pos_y):
        """Add an obstacle at position (pos_x, pos_y)"""
        obstacle = Obstacle(pos_x, pos_y)

        self.obstacles.append(obstacle)
        self.obstacle_sprites.add(obstacle)

    def PickUpCollectable(self, collectable):
        self.collectables.remove(collectable)
        self.collectable_sprites.remove(collectable)

        self.score += 10
        self.UpdateScore()

        self.coin_sound.play()

    def Run(self):
        self.LoadSprites();
        self.MainLoop();

    def UpdateFrame(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()

        self.player.Update()
        self.ChaseCamera(self.player)

    def RenderTiles(self, layer):
        """Render all the tiles in a layer"""
        tile_layer = self.tiled_map.layers[layer]
        for x, y, image in tile_layer.tiles():
            if image is not None:
                self.screen.blit(image, (x * self.tile_size - self.camera_x, y * self.tile_size - self.camera_y))

    def IsTileCollidingWithRect(self, x, y, rect):
        if x * self.tile_size >= rect.right:
            return False
        if y * self.tile_size >= rect.bottom:
            return False
        if (x + 1) * self.tile_size <= rect.left:
            return False
        if (y + 1) * self.tile_size <= rect.top:
            return False
        return True

    def IsCollidingWithTile(self, layer, rect):
        """Check to see if a rectangle is colliding with the tiles in a layer"""
        tile_layer = self.tiled_map.layers[layer]
        for x, y, image in tile_layer.tiles():
            if image is not None and self.IsTileCollidingWithRect(x, y, rect):
                return True
                
        return False

    def DrawSpriteGroup(self, sprite_group):
        for sprite in sprite_group.sprites():
            rect = sprite.rect.move(-self.camera_x, -self.camera_y)
            self.screen.blit(sprite.image, rect)

    def RenderFrame(self):
        """Draw any sprites"""
        self.screen.fill((0, 0, 0))
        self.RenderTiles(0)
        self.DrawSpriteGroup(self.player_sprites)
        self.DrawSpriteGroup(self.collectable_sprites)
        self.DrawSpriteGroup(self.obstacle_sprites)
        self.screen.blit(self.score_text, (8, 8))

        pygame.display.flip()

    def MainLoop(self):
        """This is the Main Loop of the Game"""
        while 1:
            self.UpdateFrame()
            self.RenderFrame()
            self.clock.tick(60)

class Player(pygame.sprite.Sprite):     
    def __init__(self, game): 
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image, self.rect = load_image('snake.png',-1)
        self.jump_sound = pygame.mixer.Sound("jump.wav")
        self.velocity_x = 0
        self.velocity_y = 0
        self.jump_speed = 12
        self.walk_speed = 4
        self.fall_accel = 0.5
        self.alive = True

    def Die(self):
        self.alive = False

    def Respawn(self):
        self.alive = True
        self.velocity_x = 0
        self.velocity_y = 0

    def Update(self):
        pressed = pygame.key.get_pressed()

        if not self.alive:
            if pressed[K_SPACE]:
                self.game.Restart()
            return
        
        self.velocity_x *= 0.75

        if pressed[K_LEFT]: 
            self.velocity_x = -self.walk_speed

        if pressed[K_RIGHT]: 
            self.velocity_x = self.walk_speed

        self.rect.move_ip(self.velocity_x, 0)
        if self.game.IsCollidingWithTile(0, self.rect):
            self.rect.move_ip(-self.velocity_x, 0)
            self.velocity_x = 0

        self.velocity_y -= self.fall_accel

        self.rect.move_ip(0, -self.velocity_y)
        if self.game.IsCollidingWithTile(0, self.rect):
            self.rect.move_ip(0, self.velocity_y)

            if self.velocity_y <= 0 and pressed[K_UP]:
                self.velocity_y = self.jump_speed
                self.jump_sound.play()
            else:
                self.velocity_y = 0

        for collectable in self.game.collectables:
            if self.rect.colliderect(collectable.rect):
                self.game.PickUpCollectable(collectable)

        for obstacle in self.game.obstacles:
            if self.rect.colliderect(obstacle.rect):
                self.Die()
                return


class Collectable(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('coin.png')
        self.rect.move_ip(pos_x, pos_y)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('spike.png')
        self.rect.move_ip(pos_x, pos_y)

if __name__ == "__main__":
    MainWindow = PyManMain()
    MainWindow.Run()
