#!/usr/bin/env python

from __future__ import division

import pygame
import math
import random
import sys
import os.path

import entities
import physics


def load_resource(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath('.')
    
    return os.path.join(base_path, relative_path)
        
def load_image(path):
    return pygame.image.load(load_resource(path)).convert_alpha()

def generate_stargrid(image_name, offset):
    image = load_image(image_name)
    field = []
    for i in range(30):
        position = physics.Cartesian(
            random.randint(-offset, 800 + offset), 
            random.randint(-offset, 800 + offset))
        field.append({'image': image, 'dest': position})
    return field
        

class Renderer(object):
    def __init__(self, size=(800, 800), caption="Orbital Smash"):
        pygame.init()
        
        self.size = size
        self.caption = caption
        
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption(self.caption)
        
        self.clear_screen()
        
        self.human_image = load_image(r'images\human.png')
        self.rock_image = load_image(r'images\spaceArt\png\meteorSmall.png')
        self.steel_rock_image = load_image(r'images\spaceArt\png\steelMeteorSmall.png')
        
        self.ufo_image = load_image(r'images\spaceArt\png\enemyUFO.png')
        self.ufo_image = pygame.transform.scale(self.ufo_image, (45, 45))
        self.shooter_image = load_image(r'images\spaceArt\png\enemyShip.png')
        self.shooter_image = pygame.transform.rotate(self.shooter_image, -90)
        self.bullet_image = load_image(r'images\bullet.png')
        self.mine_image = load_image(r'images\spaceArt/png/laserRedShot.png')
        self.star_image = load_image(r'images\asterisk.png')
        
        self.blast_wave = load_image(r'images\blast_wave.png')
        self.blast_wave_minor = load_image(r'images\blast_wave_yellow.png')
        self.blast_wave_player_death = load_image(r'images\blast_wave_green.png')
        
        self.large_starfield = generate_stargrid(r'images\spaceArt\png\Background\starBig.png', 16)
        self.small_starfield = generate_stargrid(r'images\spaceArt\png\Background\starSmall.png', 8)
        
        self.title_font = pygame.font.Font(load_resource(r'fonts\orbitron\OrbitronMedium.ttf'), 32)
        self.font = pygame.font.Font(load_resource(r'fonts\orbitron\OrbitronMedium.ttf'), 16)
        
        self.animations = []
        
    def initialize(self, things):
        for e in things:
            if entities.HumanSprite in e:
                e.scaled_image = e.image = self.human_image
                e.radius = 8
            if entities.RockSprite in e:
                e.scaled_image = e.image = self.rock_image
                e.radius = 21
            if entities.SteelSprite in e:
                e.scaled_image = e.image = self.steel_rock_image
                e.radius = 21
            if entities.UfoSprite in e:
                e.scaled_image = e.image = self.ufo_image
                e.radius = 22
            if entities.ShooterSprite in e:
                e.scaled_image = e.image = self.shooter_image
                e.radius = 25
            if entities.MineSprite in e:
                e.scaled_image = e.image = self.mine_image
                e.radius = 12
            if entities.BulletSprite in e:
                e.scaled_image = e.image = self.bullet_image
                e.radius = 4
            if entities.StarSprite in e:
                e.scaled_image = e.image = self.star_image
                e.radius = 8
            
    def process(self, things):
        self.clear_screen()
        
        self.draw_starfield(pygame.mouse.get_pos())
        
        new_animations = []
        
        for animation in self.animations:
            centerpoint, growth, image = animation
            width, height = image.get_size()
            image = pygame.transform.scale(image, ((width + growth), (height + growth)))
            self.draw_image(image, centerpoint)
            growth -= 1
            if growth > 0:
                new_animations.append((centerpoint, growth, image))
        self.animations = new_animations
            
        
        for e in things:
            if entities.Rotates in e:
                e.scaled_image = pygame.transform.rotate(e.image, e.angle/math.pi * 180)
            if entities.Drawable in e:
                self.draw_image(e.scaled_image, e.position)
            if entities.Dead in e:
                if entities.UserControllable in e:
                    self.add_explosion((4, 6), e.position, 20, self.blast_wave_player_death, 255)
                elif entities.Bullet not in e:
                    self.add_explosion((4, 6), e.position, 20, self.blast_wave, 255)
            if entities.Explosion in e:
                if e.reason == 'Collision':
                    self.add_explosion((2, 3), e.position, 4, self.blast_wave_minor, 127)
                elif e.reason == 'Bullet':
                    self.add_explosion((2, 3), e.position, 4, self.blast_wave, 127)
                    
            if entities.Damageable in e:
                # Boundary
                if e.health != e.max_health and e.health > 0:
                    width, height = e.scaled_image.get_size()
                    sides = int(10.0 * e.health / e.max_health) + 1
                    corner = (e.position.x - sides, e.position.y - height / 2 - 10)
                    size = (sides * 2, 5)
                    pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(corner, size))
            if entities.Collector in e:
                for orbiting in e.collected_objects:
                    distance = physics.get_distance(orbiting.position, e.position) 
                    width = 7 - 5 * distance / e.draw_radius
                    pygame.draw.line(
                        self.screen, 
                        (0, 255, 0), 
                        e.position.pos(),
                        orbiting.position.pos(), 
                        int(width))
                        
    def add_explosion(self, wave_range, position, growth, image, size):
        for i in xrange(random.randint(*wave_range)):
            image = pygame.transform.rotate(image, random.random() * 360)
            scale = (int(51 + random.random() * size), int(51 + random.random() * size))
            image = pygame.transform.scale(image, scale)
            self.animations.append((position, growth, image))
                        
    def draw_image(self, image, position):
        width, height = image.get_size()
        x, y = position.pos()
        self.screen.blit(image, (x - width / 2, y - height / 2))
                
    def draw_starfield(self, input_coords):
        x, y = input_coords
        offset = physics.Cartesian(x - 400, y - 400)
        for star in self.large_starfield:
            self.screen.blit(
                star['image'],
                (star['dest'] - offset * 16 / 400).pos())
        for star in self.small_starfield:
            self.screen.blit(
                star['image'],
                (star['dest'] - offset * 8 / 400).pos())
                
    def shadeout(self):
        shade = pygame.Surface((800, 800))
        shade.set_alpha(200)
        shade.fill((0,0,0))
        self.screen.blit(shade, (0, 0))
        
    def draw_menu_background(self, width, height):
        menu = pygame.Surface((width, height))
        menu.set_alpha(200)
        menu.fill((255,255,255))
        self.screen.blit(menu, (400 - width/2, 400 - height / 2))
                
    def draw_menu(self, menu_name, options, size=200):
        self.shadeout()
        height = 40 + len(options) * 20 + 10
        self.draw_menu_background(size, height)
        counter = 400 - height / 2 + 10
        
        color = (0, 150, 33)
        if "lost" in menu_name:
            color = (255, 0, 0)
        
        self.screen.blit(self.title_font.render(
            menu_name,
            True,
            color,
        ), (400 - size/2 + 10, counter))
        
        counter += 40
        
        current = None
        
        for option in options:
            display = pygame.Rect((400 - size/2 + 5, counter - 2), (190, 20))
            if display.collidepoint(pygame.mouse.get_pos()):
                current = option
                color = (0, 150, 33) # green
                extra = "=> {0} <="
            else:
                color = (14,2,40) 
                extra = "-> {0}"
                
            self.screen.blit(self.font.render(
                extra.format(option),
                True,
                color
            ), (400 - size/2 + 10, counter))
            counter += 20
            
        return current
        
    def draw_dialog(self, menu_name, text):
        self.shadeout()
        height = 40 + len(text) * 20 + 10
        self.draw_menu_background(500, height)
        counter = 400 - height / 2 + 10
        
        color = (0, 150, 33)
        if "lost" in menu_name:
            color = (255, 0, 0)
        
        self.screen.blit(self.title_font.render(
            menu_name,
            True,
            color
        ), (160, counter))
        
        counter += 40
        
        for t in text:
            self.screen.blit(self.font.render(
                t,
                True,
                (14,2,40)
            ), (160, counter))
            counter += 20

    def clear_screen(self):
        self.screen.fill((14,2,40)) # A deep purple
        
    def display(self):
        pygame.display.flip()
        
        