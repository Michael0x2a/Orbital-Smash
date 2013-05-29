#!/usr/bin/env python
'''
Contains the code necessary render the graphics using pygame.
'''

from __future__ import division

import math
import random
import sys
import os.path

import pygame

import entities
import physics


def load_resource(relative_path):
    '''Safely loads all resources (images and fonts).
    
    Pygame does not load things normally, so requires some
    boilerplate code as a hack.'''
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath('.')
    
    return os.path.join(base_path, relative_path)
        
def load_image(path):
    '''Loads an image and converts it into a format pygame likes.
    
    Note: this automatically looks in the 'images' folder.'''
    relative = os.path.join('images', path)
    return pygame.image.load(load_resource(relative)).convert_alpha()

def generate_stargrid(image_name, offset):
    '''Generates a stargrid for the background (parallax effect).'''
    image = load_image(image_name)
    field = []
    for _ in range(30):
        position = physics.Cartesian(
            random.randint(-offset, 800 + offset), 
            random.randint(-offset, 800 + offset))
        field.append({'image': image, 'dest': position})
    return field
        

class Renderer(object):
    '''An object which processes a list of entities and renders all
    graphics. Also works with menus and dialogs.'''
    def __init__(self, size=(800, 800), caption="Orbital Smash"):
        self.animations = []
        
        pygame.init()
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption(caption)
        self.clear_screen()
        
        self.sprites = {
            entities.HUMAN_SPRITE: (8, r'human.png'),
            entities.ROCK_SPRITE:  (21, r'spaceArt\png\meteorSmall.png'),
            entities.STEEL_SPRITE: (21, r'spaceArt\png\steelMeteorSmall.png'),
            entities.UFO_SPRITE:   (22, r'spaceArt\png\enemyUFO.png'),
            entities.SHOOTER_SPRITE: (25, r'spaceArt\png\enemyShip.png'),
            entities.BULLET_SPRITE: (4, r'bullet.png'),
            entities.MINE_SPRITE: (12, r'spaceArt/png/laserRedShot.png'),
            entities.STAR_SPRITE: (8, r'asterisk.png')
        }
        
        for name, (radius, path) in self.sprites.items():
            self.sprites[name] = (radius, load_image(path))
        
        self.explosions = {
            "normal": load_image(r'blast_wave.png'),
            "minor": load_image(r'blast_wave_yellow.png'),
            "player_death": load_image(r'blast_wave_green.png')
        }
        
        self.large_starfield = generate_stargrid(
            r'spaceArt\png\Background\starBig.png', 16)
        self.small_starfield = generate_stargrid(
            r'spaceArt\png\Background\starSmall.png', 8)
            
        self.title_font = pygame.font.Font(
            load_resource(r'fonts\orbitron\OrbitronMedium.ttf'), 32)
        self.font = pygame.font.Font(
            load_resource(r'fonts\orbitron\OrbitronMedium.ttf'), 16)
        
    def initialize(self, things):
        '''Initializes all sprites and entities.'''
        for entity in things:
            for sprite, (radius, _) in self.sprites.items():
                if sprite in entity:
                    entity.radius = radius
                    # Technically unnecessary, but makes lookup easier.
                    entity.sprite = sprite
            
    def process(self, things):
        '''Draws everything, and returns a tuple containing a 
        list of all new entities to be added and any frames.'''
        self.clear_screen()
        self.draw_starfield(pygame.mouse.get_pos())
        self.handle_animations()
        self.process_entities(things)
        
        return [], None
        
    def process_entities(self, things):
        '''Processes all entities.'''
        components = [
            entities.DRAWABLE,
            entities.DEAD,
            entities.EXPLOSION,
            entities.DAMAGEABLE,
            entities.COLLECTOR_ACTIVE
        ]
        
        for entity in things:
            for component in components:
                if component in entity:
                    func_name = 'handle_{0}'.format(component.lower())
                    func = getattr(self, func_name)
                    func(entity)

    def handle_drawable(self, entity):
        '''Draws any drawable image.'''
        image = self.get_image(entity)
        self.draw_image(image, entity.position)
        
    def handle_dead(self, entity):
        '''Handles any dead entities, primarily through explosions.'''
        if entities.USER_CONTROLLABLE in entity:
            self.add_explosion(
                (4, 6), 
                entity.position, 
                20, 
                'player_death', 
                255)
        elif entities.BULLET not in entity:
            self.add_explosion(
                (4, 6), 
                entity.position, 
                20, 
                'normal', 
                255)
                
    def handle_explosion(self, entity):
        '''Handles any explosions.'''
        if entity.reason == 'Collision':
            self.add_explosion(
                (2, 3), 
                entity.position, 
                4, 
                'minor', 
                127)
        elif entity.reason == 'BULLET':
            self.add_explosion(
                (2, 3), 
                entity.position, 
                4, 
                'normal', 
                127)

    def handle_damageable(self, entity):
        '''Draws a health bar.'''
        # Boundary
        if entity.health != entity.max_health and entity.health > 0:
            _, height = self.get_image(entity).get_size()
            sides = int(10.0 * entity.health / entity.max_health) + 1
            corner = (entity.position.x - sides, 
                      entity.position.y - height / 2 - 10)
            size = (sides * 2, 5)
            pygame.draw.rect(
                self.screen, 
                (255, 0, 0), 
                pygame.Rect(corner, size))
                
    def handle_collector_active(self, entity):
        '''Draws a tractor beam.'''
        for orbiting in entity.collected_objects:
            distance = physics.get_distance(
                orbiting.position, 
                entity.position)
            width = 7 - 5 * distance / entity.draw_radius
            pygame.draw.line(
                self.screen, 
                (0, 255, 0), 
                entity.position.pos(),
                orbiting.position.pos(), 
                int(width))
                
    def get_image(self, entity):
        '''Gets the image of a sprite, and handles all scaling.'''
        image = self.sprites[entity.sprite][1]
        if entities.ROTATES in entity:
            image = pygame.transform.rotate(
                image, entity.angle / math.pi * 180)
        return image
                        
    def heartbeat(self):
        '''Called after the loop, for anything which is vital for keeping
        the game running but doesn't actually process anything.'''
        self.display()
        
    def handle_animations(self):
        '''Processes, updates, and handles all animations.'''
        new_animations = []
        
        for animation in self.animations:
            centerpoint, growth, image = animation
            width, height = image.get_size()
            image = pygame.transform.scale(
                image, 
                ((width + growth), (height + growth)))
            self.draw_image(image, centerpoint)
            growth -= 1
            if growth > 0:
                new_animations.append((centerpoint, growth, image))
        self.animations = new_animations
                        
    def add_explosion(self, wave_range, position, growth, image, size=255):
        '''Adds an explosion using the a random `n` number of waves specified
        by the image (`n` is within `wave_range`) at the given position, which
        starts with the initial `size` and grows specified by `growth`'''
        min_wave, max_wave = wave_range
        image = self.explosions[image]
        for _ in xrange(random.randint(min_wave, max_wave)):
            image = pygame.transform.rotate(image, random.random() * 360)
            scale = (int(101 + random.random() * (size - 80)), 
                     int(101 + random.random() * (size - 80)))
            image = pygame.transform.scale(image, scale)
            self.animations.append((position, growth, image))
                        
    def draw_image(self, image, position):
        '''Draws a sprite to the screen, accounting for offsets.'''
        width, height = image.get_size()
        x_coord, y_coord = position.pos()
        self.screen.blit(image, (x_coord - width / 2, y_coord - height / 2))
                
    def draw_starfield(self, input_coords):
        '''Draws a starfield, with parallax given the input mouse
        coordinates.'''
        x_coord, y_coord = input_coords
        offset = physics.Cartesian(x_coord - 400, y_coord - 400)
        for star in self.large_starfield:
            self.screen.blit(
                star['image'],
                (star['dest'] - offset * 16 / 400).pos())
        for star in self.small_starfield:
            self.screen.blit(
                star['image'],
                (star['dest'] - offset * 8 / 400).pos())
                
    def shadeout(self):
        '''Shades the display screen for menus and such.'''
        shade = pygame.Surface((800, 800))
        shade.set_alpha(200)
        shade.fill((0, 0, 0))
        self.screen.blit(shade, (0, 0))
        
    def draw_menu_background(self, width, height):
        '''Draws the background for the menu.'''
        menu = pygame.Surface((width, height))
        menu.set_alpha(200)
        menu.fill((255, 255, 255))
        self.screen.blit(menu, (400 - width/2, 400 - height / 2))
                
    def draw_menu(self, menu_name, options, size=200):
        '''Draws the text of the menu itself.'''
        self.shadeout()
        height = 40 + len(options) * 20 + 10
        self.draw_menu_background(size, height)
        counter = 400 - height / 2 + 10
        
        color = (0, 150, 33)
        if "lost" in menu_name:
            color = (255, 0, 0)
        
        self.screen.blit(
            self.title_font.render(menu_name, True, color), 
            (400 - size/2 + 10, counter))
        
        counter += 40
        
        current = None
        
        for option in options:
            display = pygame.Rect((400 - size/2 + 5, counter - 2), (190, 20))
            if display.collidepoint(pygame.mouse.get_pos()):
                current = option
                color = (0, 150, 33) # green
                extra = "=> {0} <="
            else:
                color = (14, 2, 40) 
                extra = "-> {0}"
                
            self.screen.blit(
                self.font.render(extra.format(option), True, color), 
                (400 - size/2 + 10, counter))
            counter += 20
            
        return current
        
    def draw_dialog(self, menu_name, text):
        '''Draws a dialog.'''
        self.shadeout()
        height = 40 + len(text) * 20 + 10
        self.draw_menu_background(500, height)
        counter = 400 - height / 2 + 10
        
        color = (0, 150, 33)
        if "lost" in menu_name:
            color = (255, 0, 0)
        
        self.screen.blit(
            self.title_font.render(menu_name, True, color), 
            (160, counter))
        
        counter += 40
        
        for line in text:
            self.screen.blit(
                self.font.render(line, True, (14,2,40)), 
                (160, counter))
            counter += 20

    def clear_screen(self):
        '''Fills the screen with the background color'''
        self.screen.fill((14, 2, 40)) # A deep purple
        
    def display(self):
        '''Displays the screen.'''
        pygame.display.flip()
        
        