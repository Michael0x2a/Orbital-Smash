#!/usr/bin/env python
'''Contains code used to get input from the user.'''

from __future__ import division

import pygame
import entities
import physics
import frames

class Events(object):
    '''Processes all events and user input.'''
    def __init__(self):
        pygame.init()
        
    def initialize(self, things):
        '''Initializes a list of entities.'''
        for entity in things:
            if entities.COLLECTOR in entity:
                entity.add(entities.COLLECTOR_ACTIVE)
                entity.collected_objects = []
                
    def handle_events(self):
        '''Processes events from pygame.'''
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
        
        return event, frame
        
    def process(self, things):
        '''Processes all input and output.'''
        event, frame = self.handle_events()
        
        components = [
            entities.USER_CONTROLLABLE
        ]
        
        for entity in things:
            for component in components:
                if component in entity:
                    func_name = 'handle_{0}'.format(component.lower())
                    func = getattr(self, func_name)
                    func(entity, event)
                
        return [], frame
        
    def handle_user_controllable(self, entity, event):
        '''Handles any player entities.'''
        target = physics.Cartesian(*pygame.mouse.get_pos())
        force = 20
        entity.acceleration = target - entity.position
        entity.acceleration.magnitude = force / entity.mass
        if entities.COLLECTOR in entity:
            if event.type == pygame.MOUSEBUTTONDOWN:
                entity.add(entities.COLLECTOR_ACTIVE)
            if event.type == pygame.MOUSEBUTTONUP:
                entity.remove(entities.COLLECTOR_ACTIVE)
                entity.collected_objects = []
        
    def heartbeat(self):
        '''Called after the loop, for anything which is vital for keeping
        the game running but doesn't actually process anything.'''
        pygame.event.pump()
                
        