import os, sys
import pygame
import math

import pytmx
from pytmx.util_pygame import load_pygame

from pygame.locals import *
from helpers import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

class PyManMain:
    """The Main PyMan Class - This class handles the main 
    initialization and creating of the Game."""
   
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

    def ChaseCamera(self, target, rate=0.25):
        vert_offset = 80

        dest_x = target.rect.center[0] - self.width * 0.5
        dest_y = target.rect.center[1] - self.height * 0.5 - vert_offset

        self.camera_x = int(self.camera_x + (dest_x - self.camera_x) * rate)
        self.camera_y = int(self.camera_y + (dest_y - self.camera_y) * rate)
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
   
    def PlaceCollectable(self, obj):
        """Add a collectable with object info 'obj'"""
        collectable = Collectable(obj)
        self.collectables.append(collectable)
        self.collectable_sprites.add(collectable)

    def PlaceObstacle(self, obj):
        """Add an obstacle at position (pos_x, pos_y)"""
        obstacle = Obstacle(obj)
        self.obstacles.append(obstacle)
        self.obstacle_sprites.add(obstacle)

    def PlaceEnemy(self, obj):
        """Add an enemy with object properties"""
        enemy = Enemy(obj)

        self.obstacles.append(enemy)
        self.obstacle_sprites.add(enemy)

    def PlaceLevelExit(self, obj):
        """Add a level exit at position (pos_x, pos_y)"""
        exit = LevelExit(obj)
        self.collectables.append(exit)
        self.collectable_sprites.add(exit)
    
    def __init__(self, width=1000,height=650):
        """Initialize PyGame"""
        pygame.init()

        self.camera_x = 0
        self.camera_y = -200
        self.coin_sound = pygame.mixer.Sound("beep9.wav")
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        self.score = 0
        self.font = pygame.font.Font('game_over.ttf', 64)
        self.UpdateScore()
        self.collectables = []
        self.collectable_sprites = pygame.sprite.RenderPlain()
        self.obstacles = []
        self.obstacle_sprites = pygame.sprite.RenderPlain()

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("The Hackathon 2K16")
        self.screen.fill((9,28,0))
        self.gameover_text = self.font.render('Game Over: Press space to restart', True, (255, 0, 0))
        self.GameOver_sound = pygame.mixer.Sound("JohnCena.wav")

    def Restart(self):
        self.collectables = []
        self.collectable_sprites = pygame.sprite.RenderPlain()
        self.score = 0

        self.player.rect.center = (0, 0)
        self.player.Respawn()

        self.UpdateScore()
        self.SpawnCollectables()


    def UpdateScore(self):
        self.score_text = self.font.render(str(self.score), True, (255, 0, 0))

    def SpawnCollectables(self):
        if "Collectables" in self.tiled_map.layernames:
            collectables_layer = self.tiled_map.get_layer_by_name("Collectables")
            for obj in collectables_layer:
                self.PlaceCollectable(obj)

        if "LevelExit" in self.tiled_map.layernames:
            exits_layer = self.tiled_map.get_layer_by_name("LevelExit")
            for obj in exits_layer:
                self.PlaceLevelExit(obj)

    def LoadSprites(self):
        """Load the sprites that we need"""
        self.player = Player(self)
        self.player_sprites = pygame.sprite.RenderPlain((self.player))

        self.ChangeLevel('map.tmx')

    def PickUpCollectable(self, collectable):
        self.collectables.remove(collectable)
        self.collectable_sprites.remove(collectable)
        self.score += 1
        self.coin_sound.play()
        self.UpdateScore()

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
        for obstacle in self.obstacles:
            if obstacle.Update is not None:
                obstacle.Update()

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

    def DrawSpriteGroup(self, sprite_group):
        for sprite in sprite_group.sprites():
            rect = sprite.rect.move(-self.camera_x, -self.camera_y)
            self.screen.blit(sprite.image, rect)


    def RenderFrame(self):
        """Draw any sprites"""
        self.screen.fill((55,169,255))
        self.RenderTiles( 0 )
        self.DrawSpriteGroup(self.player_sprites)
        self.DrawSpriteGroup(self.collectable_sprites)
        self.DrawSpriteGroup(self.obstacle_sprites)
        self.screen.blit(self.score_text, (8, 8))
        if not self.player.alive:
            self.screen.blit(self.gameover_text, (300, 300))
            self.GameOver_sound.play()
        pygame.display.flip()


    def MainLoop(self):
        """This is the Main Loop of the Game"""
        while 1:
            self.UpdateFrame();
            self.RenderFrame();
            self.clock.tick(60)

    def ChangeLevel(self, level):
        self.obstacles = []
        self.obstacle_sprites = pygame.sprite.RenderPlain()

        self.tiled_map = load_pygame(level)
        self.tile_size = 40

        if "Obstacles" in self.tiled_map.layernames:
            obstacles_layer = self.tiled_map.get_layer_by_name("Obstacles")
            for obj in obstacles_layer:
                self.PlaceObstacle(obj)

        if "Enemy" in self.tiled_map.layernames:
            enemies_layer = self.tiled_map.get_layer_by_name("Enemy")
            for obj in enemies_layer:
                if obj.image is not None:
                    self.PlaceEnemy(obj)

        self.Restart()

class Player(pygame.sprite.Sprite):     
    def __init__(self, game): 
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image, self.rect = load_image('harambe.png')
        self.jump_sound = pygame.mixer.Sound("Jump.wav")
        self.velocity_y = 0
        self.velocity_x = 0
        self.jump_speed = 12
        self.walk_speed = 5
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
                self.jump_sound.play()
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
        self.image = obj.image.convert_alpha()
        self.rect = Rect(obj.x, obj.y, obj.width, obj.height)
    def OnPickup(self, player):
        player.game.PickUpCollectable(self)

class Obstacle(pygame.sprite.Sprite):

    def __init__(self, obj):
        pygame.sprite.Sprite.__init__(self)
        self.image = obj.image.convert_alpha()
        self.rect = Rect(obj.x, obj.y, obj.width, obj.height)
    def Update(self):
        return

class Enemy(pygame.sprite.Sprite):
    def __init__(self, obj):
        pygame.sprite.Sprite.__init__(self)
        self.image = obj.image.convert_alpha()
        self.rect = Rect(obj.x, obj.y, obj.width, obj.height)
        
        if "movespeed" in obj.properties:
            self.move_speed = float(obj.movespeed)
        else:
            self.move_speed = 2

        if "Path" in obj.properties:
            self.path = obj.parent.get_object_by_name(obj.Path).points
            self.path_index = 0
            self.rect.center = self.path[self.path_index]
            self.has_path = True
        else:
            self.has_path = False
        if self.has_path and not "cycle" in obj.properties:
            path_length = len(self.path)
            for index in range(1, path_length - 1):
                self.path += (self.path[path_length - index],)

    def Update(self):
        if not self.has_path:
            return

        dest_x = self.path[self.path_index][0]
        dest_y = self.path[self.path_index][1]

        diff_x = dest_x - self.rect.center[0]
        diff_y = dest_y - self.rect.center[1]

        distance = math.sqrt(diff_x * diff_x + diff_y * diff_y)

        if distance <= self.move_speed:
            self.rect.center = self.path[self.path_index]
            self.path_index += 1
            if self.path_index >= len(self.path):
                self.path_index = 0
        else:
            self.rect.move_ip(diff_x * self.move_speed / distance, diff_y * self.move_speed / distance)

class LevelExit(pygame.sprite.Sprite):
    def __init__(self, obj):
        pygame.sprite.Sprite.__init__(self)
        self.image = obj.image.convert_alpha()
        self.rect = Rect(obj.x, obj.y, obj.width, obj.height)
        self.NextMap = obj.NextMap
        
    def OnPickup(self, player):
        player.game.ChangeLevel(self.NextMap)

if __name__ == "__main__":
    MainWindow = PyManMain()
MainWindow.Run()

