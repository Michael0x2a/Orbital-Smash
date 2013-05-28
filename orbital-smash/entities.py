#!/usr/bin/env python

from __future__ import division

import copy
import random

class Entity(object):
    def __init__(self, *components):
        self.components = list(components)
        
    def __contains__(self, value):
        return value in self.components
        
    def remove(self, value):
        if value in self.components:
            del self.components[self.components.index(value)]
            
    def add(self, value):
        if value not in self.components:
            self.components.append(value)
            
    def copy(self):
        return copy.deepcopy(self)
    
UserControllable = "UserControllable"

# Sprites
HumanSprite = "Human Sprite"
RockSprite = "Rock Sprite"
UfoSprite = "UFO Sprite"
BulletSprite = "Bullet Sprite"
ShooterSprite = "Shooter Sprite"
MineSprite = "Mine Sprite"
SteelSprite = "Steel sprite"
StarSprite = "Asterisk Sprite"


# Fundamental characteristics
Human = "Human"
Enemy = "Enemy"
Rock = "Rock"
Bullet = "Bullet"
Star = "Star"

# Interactions
Moveable = "Moveable"
Solid = "Solid"
Orbitable = "Orbitable"
Collector = "Collector"
Drawable = "Drawable"
Damageable = "Damageable"

# Misc
Rotates = "Rotates"
FacesUser = "FacesUser"
Dead = "Dead"
Explosion = "Explosion"
AI = "AI"

# Attack patterns
ShootingAttack = "Shooting Attack"
ContactAttack = "Contact Attack"
WideShootingAttack = "Wide Shooting Attack"
ExplodingAttack = "Exploding Attack"
SwarmingAttack = "Swarming Attack"

# Movement patterns
JaggedPath = "Jagged Path"
TrackingPath = "Tracking Path"
BulldozePath = "Bulldoze Path"
CirclePath = "Circle Path"


# Todo
Bounded = "Bounded"
RemoveWhenUnbounded = "RemoveWhenUnbounded"



# Premade entities:

def make_human():
    return Entity(
        UserControllable, 
        Human, 
        HumanSprite, 
        Drawable,
        Solid, 
        Moveable, 
        Bounded,  
        Damageable,
        Collector
    )

def make_rock():
    return Entity(
        Rock, 
        RockSprite, 
        Drawable, 
        Rotates, 
        Moveable, 
        Solid, 
        Orbitable, 
        Damageable, 
        Bounded)
        
def make_steel():
    return Entity(
        Rock, 
        SteelSprite, 
        Drawable, 
        Rotates, 
        Moveable, 
        Solid, 
        Orbitable, 
        Bounded)
    
def make_shooter():
    return Entity(
        AI, 
        Enemy, 
        ShooterSprite, 
        Rotates, 
        FacesUser, 
        Moveable, 
        Solid, 
        Drawable, 
        Bounded,
        Damageable, 
        JaggedPath, 
        Orbitable,
        ShootingAttack,
    )
    
def make_enemy():
    sprites = [
        UfoSprite,
        ShooterSprite,
        MineSprite,
        StarSprite]
        
    attacks = [
        ShootingAttack,
        WideShootingAttack,
        ContactAttack,
        SwarmingAttack
    ]
    random.shuffle(attacks)

    movements = [
        JaggedPath,
        TrackingPath,
        BulldozePath,
        CirclePath
    ]
    
    args = [
        AI,
        Enemy,
        Moveable,
        Solid,
        Orbitable,
        Drawable,
        Damageable,
        random.choice(sprites),
        Rotates,
        FacesUser,
        Bounded,
        random.choice(movements)
    ]
    args.extend(attacks[0: random.randint(1, len(attacks) + 1)])
    
    return Entity(*args)
        
        
        
    
def make_explosion(position, reason):
    e = Entity(
        Explosion,
    )
    e.position = position
    e.reason = reason
    return e
    
def make_bullet(start, target, radius):
    bullet = Entity(
        AI, 
        Enemy, 
        Bullet, 
        BulletSprite, 
        Moveable, 
        Solid, 
        Drawable, 
        Damageable, 
        ContactAttack, 
        RemoveWhenUnbounded
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
    star = Entity(
        AI, 
        Enemy, 
        Star,
        StarSprite, 
        Moveable, 
        Solid, 
        Drawable, 
        Damageable, 
        ContactAttack, 
        Rotates,
        FacesUser,
        Bounded,
        random.choice([
            JaggedPath,
            TrackingPath,
            BulldozePath,
            CirclePath
        ])
    )
    
    vector = target - start

    normal = vector.copy()
    
    vector.magnitude = 8
    normal.magnitude = (radius + 25)
    
    star.initial_velocity = vector
    star.initial_position = start + normal
    return star
    
    