#!/usr/bin/env python

from __future__ import division

import copy
import random

class Entity(object):
    '''Represents an entity object.'''
    def __init__(self, *components):
        self.components = list(components)

    def __contains__(self, value):
        return value in self.components

    def remove(self, value):
        '''Removes a component. This is idempotent.'''
        if value in self.components:
            del self.components[self.components.index(value)]

    def add(self, value):
        '''Adds a component. This is idempotent.'''
        if value not in self.components:
            self.components.append(value)

    def copy(self):
        '''Returns a complete copy of the entity.'''
        return copy.deepcopy(self)

USER_CONTROLLABLE = "USER_CONTROLLABLE"

# Sprites
HUMAN_SPRITE = "HUMAN_SPRITE"
ROCK_SPRITE = "ROCK_SPRITE"
UFO_SPRITE = "UFO_SPRITE"
BULLET_SPRITE = "BULLET_SPRITE"
SHOOTER_SPRITE = "SHOOTER_SPRITE"
MINE_SPRITE = "MINE_SPRITE"
STEEL_SPRITE = "STEEL_SPRITE"
STAR_SPRITE = "STAR_SPRITE"

# Fundamental characteristics
HUMAN = "HUMAN"
ENEMY = "ENEMY"
ROCK = "ROCK"
BULLET = "BULLET"
STAR = "STAR"
EXPLOSION = "EXPLOSION"

# Interactions with others.
MOVEABLE = "MOVEABLE"
SOLID = "SOLID"
ORBITABLE = "ORBITABLE"
COLLECTOR = "COLLECTOR"
DRAWABLE = "DRAWABLE"
DAMAGEABLE = "DAMAGEABLE"

# Object State
ROTATES = "ROTATES"
FACES_USER = "FACES_USER"
DEAD = "DEAD"
AI = "AI"
COLLECTOR_ACTIVE = "COLLECTOR_ACTIVE"

# Attack patterns
SHOOTING_ATTACK = "SHOOTING_ATTACK"
CONTACT_ATTACK = "CONTACT_ATTACK"
WIDE_SHOOTING_ATTACK = "WIDE_SHOOTING_ATTACK"
EXPLODING_ATTACK = "EXPLODING_ATTACK"
SWARMING_ATTACK = "SWARMING_ATTACK"

# Movement patterns
JAGGED_PATH = "JAGGED_PATH"
TRACKING_PATH = "TRACKING_PATH"
BULLDOZE_PATH = "BULLDOZE_PATH"
CIRCLE_PATH = "CIRCLE_PATH"

# Todo
BOUNDED = "BOUNDED"
REMOVE_WHEN_UNBOUNDED = "REMOVE_WHEN_UNBOUNDED"



# Premade entities:

def make_human():
    '''Returns an entity representing a human.'''
    return Entity(
        USER_CONTROLLABLE,
        HUMAN,
        HUMAN_SPRITE,
        DRAWABLE,
        SOLID,
        MOVEABLE,
        BOUNDED,
        DAMAGEABLE,
        COLLECTOR
    )

def make_rock():
    '''Returns an entity representing a rock.'''
    return Entity(
        ROCK,
        ROCK_SPRITE,
        DRAWABLE,
        ROTATES,
        MOVEABLE,
        SOLID,
        ORBITABLE,
        DAMAGEABLE,
        BOUNDED)

def make_steel():
    '''Returns an entity representing a steel rock.'''
    return Entity(
        ROCK,
        STEEL_SPRITE,
        DRAWABLE,
        ROTATES,
        MOVEABLE,
        SOLID,
        ORBITABLE,
        BOUNDED)

def make_shooter():
    '''Returns an entity representing a shooter.'''
    return Entity(
        AI,
        ENEMY,
        SHOOTER_SPRITE,
        ROTATES,
        FACES_USER,
        MOVEABLE,
        SOLID,
        DRAWABLE,
        BOUNDED,
        DAMAGEABLE,
        JAGGED_PATH,
        ORBITABLE,
        SHOOTING_ATTACK,
    )

def make_enemy():
    '''Generates a randomzied enemy.'''
    sprites = [
        UFO_SPRITE,
        SHOOTER_SPRITE,
        MINE_SPRITE,
        STAR_SPRITE]

    attacks = [
        SHOOTING_ATTACK,
        WIDE_SHOOTING_ATTACK,
        CONTACT_ATTACK,
        SWARMING_ATTACK
    ]
    random.shuffle(attacks)

    movements = [
        JAGGED_PATH,
        TRACKING_PATH,
        BULLDOZE_PATH,
        CIRCLE_PATH
    ]

    args = [
        AI,
        ENEMY,
        MOVEABLE,
        SOLID,
        ORBITABLE,
        DRAWABLE,
        DAMAGEABLE,
        random.choice(sprites),
        ROTATES,
        FACES_USER,
        BOUNDED,
        random.choice(movements)
    ]
    args.extend(attacks[0: random.randint(1, len(attacks) + 1)])

    return Entity(*args)

def make_explosion(position, reason):
    '''Returns an entity representing an explosion.'''
    explosion = Entity(
        EXPLOSION
    )
    explosion.position = position
    explosion.reason = reason
    return explosion

def make_bullet(start, target, radius):
    '''Returns an entity representing a bullet that flys towards 
    a target from a given starting position, with offsets to prevent
    the bullet from harming the shooter.'''
    bullet = Entity(
        AI,
        ENEMY,
        BULLET,
        BULLET_SPRITE,
        MOVEABLE,
        SOLID,
        DRAWABLE,
        DAMAGEABLE,
        CONTACT_ATTACK,
        REMOVE_WHEN_UNBOUNDED
    )

    vector = target - start
    normal = vector.copy()

    vector.magnitude = 8
    normal.magnitude = (radius + 25)

    bullet.initial_velocity = vector
    bullet.initial_position = start + normal
    bullet.additional_damage = 50
    return bullet

def make_star(start, target, radius):
    '''Returns an object representing a star from a swarmer.'''
    star = Entity(
        AI,
        ENEMY,
        STAR,
        STAR_SPRITE,
        MOVEABLE,
        SOLID,
        DRAWABLE,
        DAMAGEABLE,
        CONTACT_ATTACK,
        ROTATES,
        FACES_USER,
        BOUNDED,
        random.choice([
            JAGGED_PATH,
            TRACKING_PATH,
            BULLDOZE_PATH
        ])
    )

    vector = target - start

    normal = vector.copy()

    vector.magnitude = 8
    normal.magnitude = (radius + 25)

    star.initial_velocity = vector
    star.initial_position = start + normal
    return star
