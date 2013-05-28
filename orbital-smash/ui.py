#!/usr/bin/env python

from __future__ import division

import pygame
import entities
import physics
import frames

class Events(object):
    def __init__(self):
        pygame.init()
        
    def initialize(self, things):
        for e in things:
            if entities.Collector in e:
                e.is_collector_active = False
                e.collected_objects = []
    
    def process(self, things):
        frame = None
        event = pygame.event.poll()
        
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit(0)
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_p]:
                frame = frames.make_pause_menu
        #if not pygame.mouse.get_focused():
        #    frame = frames.make_pause_menu
        
            
        for e in things:
            if entities.UserControllable in e:
                target = physics.Cartesian(*pygame.mouse.get_pos())
                force = 20
                e.acceleration = target - e.position
                e.acceleration.magnitude = force / e.mass
                if entities.Collector in e:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        e.is_collector_active = True
                    if event.type == pygame.MOUSEBUTTONUP:
                        e.is_collector_active = False
                        e.collected_objects = []
                
        return frame
                
        