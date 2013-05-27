#!/usr/bin/env python

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
            if entities.Human in e:
                self.avoid.append(e)
        for e in things:
            if entities.JaggedPath in e:
                e.last_movement_time = pygame.time.get_ticks()
                e.move_timer_delta = 10000 # milliseconds
                e.speed = random.choice([14, 15, 16])
            if entities.TrackingPath in e:
                e.speed = random.choice([3, 4, 5])
            if entities.BulldozePath in e:
                e.last_movement_time = pygame.time.get_ticks()
                e.move_timer_delta = random.choice([4500, 5000, 5500])
                e.speed = random.choice([14, 15, 16])
                
            if entities.ContactAttack in e:
                e.additional_damage = random.choice(range(5, 15))
            if entities.ShootingAttack in e:
                e.last_shoot_time = pygame.time.get_ticks()
                e.shoot_timer_delta = 1000
            if entities.WideShootingAttack in e:
                e.last_shoot_time = pygame.time.get_ticks()
                e.shoot_timer_delta = 1000
            if entities.SwarmingAttack in e:
                e.last_shoot_time = pygame.time.get_ticks()
                e.shoot_timer_delta = 6000
            if entities.ExplodingAttack in e:
                pass
                
            
        
    def process(self, things):
        time = pygame.time.get_ticks()
        new = []
        for e in things:
            if entities.AI not in e:
                continue
            
            if entities.JaggedPath in e:
                if (time - e.last_movement_time) >= e.move_timer_delta / 2:
                    if e.velocity.magnitude() == 0:
                        e.velocity = physics.Polar(e.speed, random.random() * math.pi * 2).to_cartesian()
                if (time - e.last_movement_time) >= e.move_timer_delta:
                    e.last_movement_time = time
                    e.velocity = physics.Cartesian(0, 0)
            if entities.TrackingPath in e:
                target = random.choice(self.avoid)
                vector = (target.position - e.position).to_polar()
                vector.magnitude = e.speed
                e.velocity = vector.to_cartesian()
            if entities.BulldozePath in e:
                if (time - e.last_movement_time) >= e.move_timer_delta / 2:
                    if e.velocity.magnitude() == 0:
                        target = random.choice(self.avoid)
                        vector = (target.position - e.position).to_polar()
                        vector.magnitude = e.speed
                        e.velocity = vector.to_cartesian()
                if (time - e.last_movement_time) >= e.move_timer_delta:
                    e.last_movement_time = time
                    e.velocity = physics.Cartesian(0, 0)
            if entities.CirclePath in e:
                human = random.choice(self.avoid)
                distance = physics.get_distance(e.position, human.position)
                normal = physics.calculate_normal(human.position, e.position)
                        
                if distance > human.draw_radius + 200:
                    e.position = human.position - (human.draw_radius + 175) * normal
                            
                if distance < human.draw_radius + 150:
                    e.position = human.position - (human.push_radius + 175) * normal
                
                normal = normal.to_polar()
                normal.magnitude = e.mass * human.mass / distance**2
                normal.angle += random.choice([math.pi / 2, -math.pi / 2])
                e.velocity += normal.to_cartesian()
                        
                        
            if entities.ShootingAttack in e:
                if (time - e.last_shoot_time)  >= e.shoot_timer_delta:
                    e.last_shoot_time = time
                    bullet = entities.make_bullet(e.position, random.choice(self.avoid).position, e.radius)
                    new.append(bullet)
            if entities.WideShootingAttack in e:
                if (time - e.last_shoot_time)  >= e.shoot_timer_delta:
                    e.last_shoot_time = time
                    for i in range(8):
                        target = e.position + physics.Polar(16, i / 4.0 * math.pi).to_cartesian()
                        bullet = entities.make_bullet(e.position, target, e.radius)
                        new.append(bullet)
            if entities.SwarmingAttack in e:
                if (time - e.last_shoot_time)  >= e.shoot_timer_delta:
                    e.last_shoot_time = time
                    for i in range(2):
                        target = e.position + physics.Polar(16, i * math.pi).to_cartesian()
                        star = entities.make_star(e.position, target, e.radius)
                        new.append(star)
            
        return new