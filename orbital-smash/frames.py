#!/usr/bin/env python

from __future__ import division

import pygame
import collections
import math
import random
import errors

import entities
import ai
import ui
import physics
import graphics

class EndFrame(Exception): pass

class EndFramePushNext(Exception): pass

def end_frame_push_next(next):
    ex = EndFramePushNext()
    ex.next = next
    raise ex

def end_frame():
    raise EndFrame()
    
def end_game():
    pygame.quit()
    raise SystemExit(0)
    
class Gameloop(object):
    def __init__(self, renderer, things, prev_score):
    
        self.timer = pygame.time.Clock()
        self.fps = 50.0
        
        self.brain = ai.AI(self.timer)
        self.events = ui.Events()
        self.engine = physics.Physics(1 / self.fps)
        self.renderer = renderer
        
        human = entities.make_human()
        
        self.queue = []
        
        self.things = [human, entities.make_steel()]
        
        floor = int(math.sqrt(prev_score / 100)) + 3
        for i in xrange(floor):
            if random.random() < 0.2 and i != 0:
                self.queue.append(entities.make_rock())
            else:
                self.queue.append(entities.make_enemy())
        
        self.brain.initialize(self.things)
        self.events.initialize(self.things)
        self.engine.initialize(self.things)
        self.renderer.initialize(self.things)
        
        self.brain.initialize(self.queue)
        self.events.initialize(self.queue)
        self.engine.initialize(self.queue)
        self.renderer.initialize(self.queue)
        
        self.max_score = prev_score + sum([e.max_health for e in self.queue if entities.Enemy in e])
    
    def initialize(self, processors, things):
        for p in processors:
            p.initialize(things)
        return things
        
    def loop(self):
        out = self.brain.process(self.things)
        self.things.extend(self.initialize([self.brain, self.events, self.engine, self.renderer], out))
        
        next_frame = self.events.process(self.things)
        if next_frame is not None:
            next_frame = next_frame(self.renderer, self.things)
        out = self.engine.process(self.things)
        self.things.extend(self.initialize([self.brain, self.events, self.engine, self.renderer], out))
                
        self.renderer.process(self.things)
        self.renderer.display()
        
        size = random.choice([5, 6, 7, 9, 10, 11])
        if len(self.things) < size:
            while len(self.things) < size and len(self.queue) > 0:
                self.things.append(self.queue.pop())
        
        for e in self.things:
            if entities.Dead in e or entities.Explosion in e:
                del self.things[self.things.index(e)]
            
        
        players_left = len([e for e in self.things if entities.UserControllable in e])
        if players_left == 0 and len(self.renderer.animations) == 0:
            next_frame = make_game_over(self.renderer, self.things, self.max_score)
            
        enemies_left = len([e for e in self.things if entities.Enemy in e])
        if enemies_left == 0:
            make_continue_game(self.renderer, self.things, self.max_score)
                
        self.timer.tick(self.fps)
        
        return next_frame

class Menu(object):
    def __init__(self, renderer, things, title, options, size=200):
        self.renderer = renderer
        self.things = things
        self.title = title
        self.options = options.keys()
        self.funcs = options
        self.size = size
    
    def attach(self, option, func):
        self.funcs[option] = func
        
    def loop(self):
        self.renderer.process(self.things)
        choice = self.renderer.draw_menu(self.title, self.options, self.size)
        self.renderer.display()
        
        event = pygame.event.poll()
        
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit(0)
            
        if choice is not None and event.type == pygame.MOUSEBUTTONDOWN:
            return self.funcs[choice]()
        
class Dialog(object):
    def __init__(self, renderer, things, title, text, next=end_frame):
        self.renderer = renderer
        self.things = things
        self.title = title
        if isinstance(text, basestring):
            text = text.split('\n')
        self.text = text
        self.text.extend(['', '(Press any key to continue)'])
        self.next = next
        
        
    def loop(self):
        self.renderer.process(self.things)
        self.renderer.draw_dialog(self.title, self.text)
        self.renderer.display()
        
        event = pygame.event.poll()
        
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit(0) 
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
            self.next()

        
def make_pause_menu(renderer, things):
    return Menu(renderer, things, 'Pause', collections.OrderedDict([
        ('Resume', end_frame), 
        ('Quit', end_game), 
        ('About', lambda: make_about_dialog(renderer, things))
    ]))
    
def make_about_dialog(renderer, things, next=end_frame):
    return Dialog(renderer, things, 'About', [
        'Orbital Smash',
        '',
        'Objective: ',
        '    Smash things before you get smashed!',
        '    How long can you last?'
        '',
        'How to play:',
        '    Move with your mouse',
        '    Attract objects by holding the left mouse button',
        '    Release to fling objects',
        '    Smash and fling objects you\'re holding',
        '    Try not to get hit',
        '    Press [p] or [esc] to pause',
        '',
        'Made for Codeday Seattle, 2013',
        'By Michael Lee',
        'Version {0} ({1})'.format(errors.__version__, errors.__release__)
    ],
    next)
    
def make_intro_to_game_sequence(renderer, things):
    return make_about_dialog(renderer, things, lambda: end_frame_push_next(
        Gameloop(renderer, things, 0)))
    
def make_start_menu(renderer, things):
    return Menu(renderer, things, 'ORBITAL SMASH', collections.OrderedDict([
            ('Start game', lambda: make_intro_to_game_sequence(renderer, things)),
            ('About', lambda: make_about_dialog(renderer, things)),
            ('Quit', end_game)
        ]), 350)
        
def get_random_hint():
    pool = [
        'Gray, steel rocks will never break!',
        'Hitting the walls will never cause damage!',
        'You can capture and fling enemy ships!',
        'Fling captured items by letting go of the mouse!',
        'Ram enemies as a last resort to hurt them!',
        'Captured objects cannot recoil and hit you!'
    ]
    return random.choice(pool)
    
    
def make_game_over(renderer, things, max_score):
    score = max_score - sum([e.health for e in things if entities.Enemy in e])
    end_frame_push_next(
        Dialog(
            renderer,
            things,
            'You lost.',
            ['Score: {0}'.format(int(score)),
             '',
             'Hint!',
             get_random_hint()],
            lambda : end_frame_push_next(
                Menu(
                    renderer, 
                    things, 
                    'You lost.'.format(int(score)), 
                    collections.OrderedDict([
                        ('Play again?', lambda: Gameloop(renderer, things, 0)),
                        ('Quit', end_game)
                    ])
                )
            )
        )
    )
    
def make_continue_game(renderer, things, max_score):
    score = max_score + sum([e.health for e in things if entities.Enemy in e]) # human health
    end_frame_push_next(
        Dialog(
            renderer,
            things,
            'You won!',
            ['Get ready for the next wave', 
             'Your score so far: {0}'.format(score),
             '',
             'Hint!',
             get_random_hint()],
            lambda: end_frame_push_next(
                Gameloop(renderer, things, score)
            )
        )
    )
            
    
    
def mainloop():
    renderer = graphics.Renderer()
    stack = []
    stack.append(make_start_menu(renderer, []))
    while True:
        try:
            next = stack[-1].loop()
            if next is not None:
                stack.append(next)
        except EndFrame as ex:
            stack.pop()
        except EndFramePushNext as ex:
            stack.pop()
            stack.append(ex.next)
        