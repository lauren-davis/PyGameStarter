import os, sys
import pygame
import pytmx
import math
from pytmx.util_pygame import load_pygame
from pygame.locals import *
from helpers import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

class PyManMain:
        
    def __init__(self, width=1200,height=720):
        """Initialize PyGame"""
        pygame.init()
        pygame.display.set_caption("Mario")
        self.score = 0
        self.font = pygame.font.Font('MarioLuigi2.ttf', 64)
        self.UpdateScore()
        self.coin_sound = pygame.mixer.Sound("pickup_coin.wav")
        self.collectables = []
        self.collectable_sprites = pygame.sprite.RenderPlain()
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()  
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.fill((17, 133, 255))
        self.camera_x = 0
        self.camera_y = 0
        self.obstacles = [] 
        self.obstacle_sprites = pygame.sprite.RenderPlain() 
        
        self.alive = True

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

    def ClampTileX(self, val):
        if val <= 0:
            return 0
        if val >= self.tiled_map.width:
            return self.tiled_map.width
        return int(math.floor(val))

    def ClampTileY(self, val):
        if val <= 0:
            return 0
        if val >= self.tiled_map.height:
            return self.tiled_map.height
        return int(math.floor(val))

    def IsCollidingWithTile(self, layer, rect):
        """Check to see if a rectangle is colliding with the tiles in a layer"""

        min_x = self.ClampTileX(rect.left / self.tile_size)
        min_y = self.ClampTileY(rect.top / self.tile_size)
        max_x = self.ClampTileX(rect.right / self.tile_size + 1)
        max_y = self.ClampTileY(rect.bottom / self.tile_size + 1)

        for x in range(min_x, max_x):
            for y in range(min_y, max_y):
                image = self.tiled_map.get_tile_image(x, y, layer)
                if image is not None and self.IsTileCollidingWithRect(x, y, rect):
                    return True
                
        return False

    def RenderTiles(self, layer):
        """Render all the tiles in a layer that are on-screen"""
        min_x = self.ClampTileX(self.camera_x / self.tile_size)
        min_y = self.ClampTileY(self.camera_y / self.tile_size)
        max_x = self.ClampTileX((self.camera_x + self.width) / self.tile_size + 1)
        max_y = self.ClampTileY((self.camera_y + self.height) / self.tile_size + 1)

        for x in range(min_x, max_x):
            for y in range(min_y, max_y):
                image = self.tiled_map.get_tile_image(x, y, layer)
                if image is not None:
                    self.screen.blit(image, (x * self.tile_size - self.camera_x, y * self.tile_size - self.camera_y))
    
    def SpawnCollectables(self):  
         collectables_layer = self.tiled_map.get_layer_by_name("collectables") 
         for obj in collectables_layer:
            self.PlaceCollectable(obj)
            if "level exits" in self.tiled_map.layernames:
                exits_layer = self.tiled_map.get_layer_by_name("level exits")
            for obj in exits_layer:
                self.PlaceLevelExit(obj)
    def DrawSpriteGroup(self, sprite_group):
        for sprite in sprite_group.sprites():
            rect = sprite.rect.move(-self.camera_x, -self.camera_y)
            self.screen.blit(sprite.image, rect)
   
    def UpdateScore(self):
        self.score_text = self.font.render(str(self.score), True, (255, 0, 0))
      
    def PlaceCollectable(self, obj):
        """Add a collectable with object info 'obj'"""
        collectable = Collectable(obj)

        self.collectables.append(collectable)
        self.collectable_sprites.add(collectable)

    def PickUpCollectable(self, collectable):
        self.collectables.remove(collectable)
        self.collectable_sprites.remove(collectable)
        self.score += 10
        self.UpdateScore()
        self.coin_sound.play()

    def PlaceObstacle(self, obj):
        """Add an obstacle from object data"""
        obstacle = Obstacle(obj)

        self.obstacles.append(obstacle)
        self.obstacle_sprites.add(obstacle)
    def SpawnObstacles(self):
        if "obstacles" in self.tiled_map.layernames:
            obstacles_layer = self.tiled_map.get_layer_by_name("obstacles")
            for obj in obstacles_layer:
                   self.PlaceObstacle(obj)
       
    def LoadSprites(self):
        """Load the sprites that we need"""
        self.player = Player(self)
        self.player_sprites = pygame.sprite.RenderPlain((self.player))
        self.gameover_text = self.font.render("Game Over: Press SPACE to restart", True, (255, 0, 0))

        self.ChangeLevel('untitled.tmx')
        
    def Run(self):
        self.LoadSprites();
        self.MainLoop();

    def UpdateFrame(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()

        self.player.Update()

        if self.player.alive == True:
            self.ChaseCamera(self.player)
       
    def RenderFrame(self):
       self.screen.fill((17, 133, 255)) 
       self.RenderTiles(0)
       self.DrawSpriteGroup(self.player_sprites)
       self.DrawSpriteGroup(self.collectable_sprites)
       self.DrawSpriteGroup(self.obstacle_sprites)
       self.screen.blit(self.score_text, (8,8))
       if not self.player.alive:
            self.screen.blit(self.gameover_text, (5, 4))

       pygame.display.flip()
    def PlaceLevelExit(self, obj):
        """Add a level exit using the given object data"""
        exit = LevelExit(obj)

        self.collectables.append(exit)
        self.collectable_sprites.add(exit)
    def MainLoop(self):

        """This is the Main Loop of the Game"""
        while 1:
            self.UpdateFrame();
            self.RenderFrame();
            self.clock.tick(60)

    def ChaseCamera(self, target, rate=0.25):
        vert_offset = 80

        dest_x = target.rect.center[0] - self.width * 0.5
        dest_y = target.rect.center[1] - self.height * 0.5 - vert_offset

        self.camera_x = int(self.camera_x + (dest_x - self.camera_x) * rate)
        self.camera_y = int(self.camera_y + (dest_y - self.camera_y) * rate)

    def Restart(self):
        self.collectables = []
        self.collectable_sprites = pygame.sprite.RenderPlain()
        self.score = 0
        
        self.player.rect.center = (0, 0)
        self.player.Respawn()

        self.UpdateScore()
        self.SpawnCollectables()

    def ChangeLevel(self, level):
        self.obstacles = []
        self.obstacle_sprites = pygame.sprite.RenderPlain()

        self.tiled_map = load_pygame(level)
        self.tile_size = 64

        self.SpawnObstacles()

        self.Restart()

class Player(pygame.sprite.Sprite):    
     def __init__(self, game):
        self.game = game
        pygame.sprite.Sprite.__init__(self) 
        self.image, self.rect = load_image('8_bit_mario.png',-1)
        self.velocity_y = 0
        self.velocity_x = 0
        self.jump_speed = 12
        self.walk_speed = 4
        self.fall_accel = 0.5
        self.end_sound = pygame.mixer.Sound("pacman_death.wav")
        self.alive = True
     def Die(self):
        self.alive = False
        self.end_sound.play()
        self.die_time = pygame.time.get_ticks()

     def Respawn(self):
        self.alive = True
        self.velocity_x = 0
        self.velocity_y = 0

     def Update(self):
        pressed = pygame.key.get_pressed()

        if not self.alive:
            if pressed[K_SPACE]:
                self.game.Restart()
            if pygame.time.get_ticks() < self.die_time + 1000:
                self.velocity_y = self.jump_speed
            else:
                self.velocity_y -= self.fall_accel
                self.rect.move_ip(0, -self.velocity_y)
                self.velocity_x = 0
            return 
        self.velocity_x = 0
        
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
            else:
                self.velocity_y = 0

        for collectable in self.game.collectables:
            if self.rect.colliderect(collectable.rect):
                  collectable.OnPickup(self)
        for obstacle in self.game.obstacles:
            if self.rect.colliderect(obstacle.rect):
                self.Die()
                return


class Collectable(pygame.sprite.Sprite):
    def __init__(self, obj):
        pygame.sprite.Sprite.__init__(self)
        self.image = obj.image
        self.rect = Rect(obj.x, obj.y, obj.width, obj.height)
    def OnPickup(self, player):
        player.game.PickUpCollectable(self)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obj):
        pygame.sprite.Sprite.__init__(self)
        self.image = obj.image
        self.rect = Rect(obj.x, obj.y, obj.width, obj.height)

class LevelExit(pygame.sprite.Sprite):
    def __init__(self, obj):
        pygame.sprite.Sprite.__init__(self)
        self.image = obj.image
        self.rect = Rect(obj.x, obj.y, obj.width, obj.height)
        self.nextmap = obj.nextmap
    def OnPickup(self, player):
        player.game.ChangeLevel(self.nextmap)

    def OnPickup(self, player):
        player.game.ChangeLevel(self.nextmap)  
if __name__ == "__main__":
    MainWindow = PyManMain()
    MainWindow.Run()
