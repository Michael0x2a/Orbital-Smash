#!/usr/bin/env python
'''
Contains code to handle game state and menus.

A "frame" is a generic name for any item (such as the gameloop,
menu, or a dialog) that appears in the gameplay stack and 
must contain a "loop" function and accepts at minimum a 
"renderer" and "things" parameter in the constructor.

TODO: instead of passing around renderer and 'things', 
pass around a list of processors which have the 'heartbeat'
function called, the 'things', and the score all 
encapsulated in a single 'state' class (which can be 
serialized)
'''

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

class EndFrame(Exception): 
    '''Called when a frame has ended and should be removed.'''
    pass

class EndFramePushNext(Exception): 
    '''Called when a frame has ended and should be removed, and 
    starts a new frame. This is to prevent stacks from slowly
    overflowing'''
    def __init__(self, *args, **kwargs):
        super(EndFramePushNext, self).__init__(*args, **kwargs)
        self.next_frame = None

def end_frame_push_next(next_frame):
    '''Kills the current frame before starting the next frame.'''
    ex = EndFramePushNext()
    ex.next_frame = next_frame
    raise ex

def end_frame():
    '''Kills the current frame.'''
    raise EndFrame()
    
def end_game():
    '''Ends the game.'''
    pygame.quit()
    raise SystemExit(0)
    
class Gameloop(object):
    '''An object representing a gameloop. 
    
    Currently, each new level is rendered within the game loop.
    In the future, this should be changed.'''
    def __init__(self, renderer, _, prev_score):
        '''Initializes the game and all created entities.'''
    
        self.timer = pygame.time.Clock()
        self.fps = 50.0
        
        self.processors = [
            ai.AI(self.timer),
            ui.Events(),
            physics.Physics(1 / self.fps),
            renderer
        ]
        self.renderer = renderer
        
        self.things = [entities.make_human(), entities.make_steel()]
        self.queue = []
        floor = int(math.sqrt(prev_score / 100)) + 3
        for i in xrange(floor):
            if random.random() < 0.2 and i != 0:
                self.queue.append(entities.make_rock())
            else:
                self.queue.append(entities.make_enemy())
        
        self.initialize(self.things)
        self.initialize(self.queue)
        
        score = [e.max_health for e in self.queue if entities.ENEMY in e]
        self.max_score = prev_score + sum(score)
    
    def initialize(self, things):
        '''Initializes a list of entities. 
        
        Technically modifies in place, but returns a list of the new 
        entities just in case.'''
        for processor in self.processors:
            processor.initialize(things)
        return things
        
    def handle_processors(self):
        '''Passes the list of entities to all processors, and handles 
        whatever is needed to keep the processors alive.'''
        next_frame = None
        for processor in self.processors:
            out, possible_frame = processor.process(self.things)
            if possible_frame is not None:
                next_frame = possible_frame
            processor.heartbeat()
            self.things.extend(self.initialize(out))
        if next_frame is not None:
            next_frame = next_frame(self.renderer, self.things)
        return next_frame
        
    def loop(self):
        '''The main gameloop. All processors are repeatedly called on the
        list of active entities.'''
        self.timer.tick(self.fps)
        
        next_frame = self.handle_processors()
        self.attempt_entity_injection()
        self.prune_dead_entities()
        possible_frame = self.check_end_conditions()
        if possible_frame is not None:
            next_frame = possible_frame
        
        return next_frame
        
    def attempt_entity_injection(self):
        '''Injects entities from the queue if the number of on-screen enemies
        is too low.'''
        size = random.choice([5, 6, 7, 9, 10, 11])
        if len(self.things) < size:
            while len(self.things) < size and len(self.queue) > 0:
                self.things.append(self.queue.pop())
        
    def prune_dead_entities(self):
        '''Removes ephermeal entities or entities marked as dead.'''
        for entity in self.things:
            if entities.DEAD in entity or entities.EXPLOSION in entity:
                del self.things[self.things.index(entity)]
        
    def check_end_conditions(self):
        '''Checks if the game is won or lost and returns the appropriate
        frame.'''
        next_frame = None
        
        players = [e for e in self.things if entities.USER_CONTROLLABLE in e]
        if len(players) == 0 and len(self.renderer.animations) == 0:
            next_frame = make_game_over(
                self.renderer, 
                self.things, 
                self.max_score)
            
        enemies_left = len([e for e in self.things if entities.ENEMY in e])
        if enemies_left == 0:
            next_frame = make_continue_game(
                self.renderer, 
                self.things, 
                self.max_score)
        
        return next_frame

class Menu(object):
    '''An object representing a menu.'''
    def __init__(self, renderer, things, title, options, size=200):
        self.renderer = renderer
        self.things = things
        self.title = title
        self.options = options.keys()
        self.funcs = options
        self.size = size
        
    def loop(self):
        '''Checks if a user has selected an option and keeps the 
        game alive.'''
        self.renderer.process(self.things)
        choice = self.renderer.draw_menu(self.title, self.options, self.size)
        self.renderer.display()
        return self.keep_alive(choice)
        
    def keep_alive(self, choice):
        '''Processes pygame events and keeps the game alive. Also 
        handles what happens if the user clicks a choice.'''
        event = pygame.event.poll()
        
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit(0)
            
        if choice is not None and event.type == pygame.MOUSEBUTTONDOWN:
            return self.funcs[choice]()
        
class Dialog(object):
    '''An object representing a dialog, which conveys only text.'''
    def __init__(self, renderer, things, title, text, next_frame=end_frame):
        self.renderer = renderer
        self.things = things
        self.title = title
        if isinstance(text, basestring):
            text = text.split('\n')
        self.text = text
        self.text.extend(['', '(Press any key to continue)'])
        self.next_frame = next_frame
        
        
    def loop(self):
        '''Checks to see if the user has killed the dialog, and keeps
        the game alive.'''
        self.renderer.process(self.things)
        self.renderer.draw_dialog(self.title, self.text)
        self.renderer.display()
        self.keep_alive()
        
    def keep_alive(self):
        '''Processes games and keeps the pygame window alive.'''
        event = pygame.event.poll()
        
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit(0) 
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
            self.next_frame()

        
def make_pause_menu(renderer, things):
    '''Builds and returns a menu object for the "pause" screen.'''
    return Menu(renderer, things, 'Pause', collections.OrderedDict([
        ('Resume', end_frame), 
        ('Quit', end_game), 
        ('About', lambda: make_about_dialog(renderer, things))
    ]))
    
def make_about_dialog(renderer, things, next_frame=end_frame):
    '''Builds and returns a dialog object for the "about" screen.'''
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
    next_frame)
    
def make_intro_to_game(renderer, things):
    '''Builds and returns a sequence which first opens the "about" screen
    then starts the game.'''
    return make_about_dialog(renderer, things, lambda: end_frame_push_next(
        Gameloop(renderer, things, 0)))
    
def make_start_menu(renderer, things):
    '''Builds and returns a menu object for the initial "start" screen.'''
    return Menu(renderer, things, 'ORBITAL SMASH', collections.OrderedDict([
            ('Start game', lambda: make_intro_to_game(renderer, things)),
            ('About', lambda: make_about_dialog(renderer, things)),
            ('Quit', end_game)
        ]), 350)
        
def get_random_hint():
    '''Returns a random hint.'''
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
    '''Builds and returns a sequence displaying the score/hint then the 
    "you lost" screen.'''
    score = max_score - sum([e.health for e in things if entities.ENEMY in e])
    return end_frame_push_next(
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
    '''Builds and returns a sequence displaying the score/hint, then the 
    "you won" screen, then starts a new game.'''
    current_health = sum([e.health for e in things if entities.ENEMY in e])
    score = max_score + current_health # human health
    return end_frame_push_next(
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
    '''STARts the core of the game and manages the frames.'''
    renderer = graphics.Renderer()
    stack = []
    stack.append(make_start_menu(renderer, []))
    while True:
        try:
            next_frame = stack[-1].loop()
            if next_frame is not None:
                stack.append(next_frame)
        except EndFrame as ex:
            stack.pop()
        except EndFramePushNext as ex:
            stack.pop()
            stack.append(ex.next_frame)
        