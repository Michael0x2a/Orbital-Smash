#!/usr/bin/env python

from __future__ import division

import pygame
import math
import random

import physics
import entities

class AI(object):
    def __init__(self, timer):
        self.timer = timer
        self.avoid = []
        
    def initialize(self, things):
        for e in things:
            if entities.HUMAN in e:
                self.avoid.append(e)
        for e in things:
            if entities.JAGGED_PATH in e:
                e.last_movement_time = pygame.time.get_ticks()
                e.move_timer_delta = 10000 # milliseconds
                e.speed = random.choice([14, 15, 16])
            if entities.TRACKING_PATH in e:
                e.speed = random.choice([3, 4, 5])
            if entities.BULLDOZE_PATH in e:
                e.last_movement_time = pygame.time.get_ticks()
                e.move_timer_delta = random.choice([4500, 5000, 5500])
                e.speed = random.choice([14, 15, 16])
                
            if entities.CONTACT_ATTACK in e:
                e.additional_damage = random.choice(range(5, 15))
            if entities.SHOOTING_ATTACK in e:
                e.last_shoot_time = pygame.time.get_ticks()
                e.shoot_timer_delta = 1000
            if entities.WIDE_SHOOTING_ATTACK in e:
                e.last_shoot_time = pygame.time.get_ticks()
                e.shoot_timer_delta = 1000
            if entities.SWARMING_ATTACK in e:
                e.last_shoot_time = pygame.time.get_ticks()
                e.shoot_timer_delta = 6000
            if entities.EXPLODING_ATTACK in e:
                pass
                
            
        
    def process(self, things):
        time = pygame.time.get_ticks()
        new = []
        for e in things:
            if entities.AI not in e:
                continue
            
            if entities.JAGGED_PATH in e:
                if (time - e.last_movement_time) >= e.move_timer_delta / 2:
                    if e.velocity.magnitude == 0:
                        e.velocity = physics.Polar(e.speed, random.random() * math.pi * 2)
                if (time - e.last_movement_time) >= e.move_timer_delta:
                    e.last_movement_time = time
                    e.velocity = physics.Cartesian(0, 0)
            if entities.TRACKING_PATH in e:
                target = random.choice(self.avoid)
                e.velocity = target.position - e.position
                e.velocity.magnitude = e.speed
            if entities.BULLDOZE_PATH in e:
                if (time - e.last_movement_time) >= e.move_timer_delta / 2:
                    if e.velocity.magnitude == 0:
                        target = random.choice(self.avoid)
                        e.velocity = target.position - e.position
                        e.velocity.magnitude = e.speed
                if (time - e.last_movement_time) >= e.move_timer_delta:
                    e.last_movement_time = time
                    e.velocity = physics.Cartesian(0, 0)
            if entities.CIRCLE_PATH in e:
                human = random.choice(self.avoid)
                distance = physics.get_distance(e.position, human.position)
                normal = physics.calculate_normal(human.position, e.position)
                        
                if distance > human.draw_radius + 200:
                    e.position = human.position - (human.draw_radius + 175) * normal
                            
                if distance < human.draw_radius + 150:
                    e.position = human.position - (human.push_radius + 175) * normal
                
                normal.magnitude = e.mass * human.mass / distance**2
                normal.angle += random.choice([math.pi / 2, -math.pi / 2])
                e.velocity += normal
                        
                        
            if entities.SHOOTING_ATTACK in e:
                if (time - e.last_shoot_time)  >= e.shoot_timer_delta:
                    e.last_shoot_time = time
                    bullet = entities.make_bullet(e.position, random.choice(self.avoid).position, e.radius)
                    new.append(bullet)
            if entities.WIDE_SHOOTING_ATTACK in e:
                if (time - e.last_shoot_time)  >= e.shoot_timer_delta:
                    e.last_shoot_time = time
                    for i in range(8):
                        target = e.position + physics.Polar(16, i / 4.0 * math.pi)
                        bullet = entities.make_bullet(e.position, target, e.radius)
                        new.append(bullet)
            if entities.SWARMING_ATTACK in e:
                if (time - e.last_shoot_time)  >= e.shoot_timer_delta:
                    e.last_shoot_time = time
                    for i in range(2):
                        target = e.position + physics.Polar(16, i * math.pi)
                        star = entities.make_star(e.position, target, e.radius)
                        new.append(star)
            
        return new, None
        
    def heartbeat(self):
        '''Called after the loop, for anything which is vital for keeping
        the game running but doesn't actually process anything.'''
        pass
        