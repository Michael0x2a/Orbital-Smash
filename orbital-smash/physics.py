#!/usr/bin/env python

from __future__ import division

import math
import random

import entities

def remove(list, item):
    del list[list.index(item)]

def get_distance(a, b):
    return (a - b).magnitude
    

class Delta(object):
    def __init__(self, a, b, type="cartesian"):
        assert type in ("cartesian", "polar")
        
        if type == "cartesian":
            self._x = a
            self._y = b
        elif type == "polar":
            magnitude, angle = a, b
            self._x = math.cos(angle) * magnitude
            self._y = math.sin(angle) * magnitude
            
    @property
    def x(self):
        return self._x
        
    @x.setter
    def x(self, x):
        self._x = x
        
    @property
    def y(self):
        return self._y
        
    @y.setter
    def y(self, y):
        self._y = y
        
    @property
    def magnitude(self):
        return math.sqrt(self._x**2 + self._y**2)
        
    @magnitude.setter
    def magnitude(self, magnitude):
        angle = self.angle
        self._x = math.cos(angle) * magnitude
        self._y = math.sin(angle) * magnitude
        
    @property
    def angle(self):
        return math.atan2(self._y, self._x)
        
    @angle.setter
    def angle(self, angle):
        magnitude = self.magnitude
        self._x = math.cos(angle) * magnitude
        self._y = math.sin(angle) * magnitude
        
    def pos(self):
        return (int(self.x), int(self.y))
        
    def copy(self):
        return Delta(self.x, self.y)
        
    def dot(self, other):
        return self.x * other.x + self.y * other.y
        
    def __add__(self, other):
        return Delta(self.x + other.x, self.y + other.y)
        
    def __sub__(self, other):
        return Delta(self.x - other.x, self.y - other.y)
        
    def __div__(self, num):
        return Delta(self.x / num, self.y / num)
        
    def __truediv__(self, num):
        return Delta(self.x / num, self.y / num)
    
    def __mul__(self, num):
        return Delta(self.x * num, self.y * num)
        
    def __rmul__(self, num):
        return self.__mul__(num)
        
    def __repr__(self):
        return 'Delta({0}, {1})'.format(self.x, self.y)

def Cartesian(x, y):
    return Delta(x, y, 'cartesian')
    
def Polar(magnitude, angle):
    return Delta(magnitude, angle, 'polar')
        
def is_colliding(a, b):
    distance = get_distance(a.position, b.position)
    epsilon = 1
    collision_distance = a.radius + b.radius + epsilon
    return distance <= collision_distance
    
def calculate_midpoint(position_1, position_2, radius_1, radius_2):
    normal = calculate_normal(position_1, position_2)
    normal.magnitude = radius_2
    intersection = position_2 + normal
    return intersection
    
def calculate_normal(center, intersection):
    normal = center - intersection
    normal.magnitude = 1
    return normal
    
def hard_push(a, b, distance_1, distance_2):
    collision_point = calculate_midpoint(a, b, distance_1, distance_2)
    a_normal = calculate_normal(a, collision_point)
    b_normal = calculate_normal(b, collision_point)
    return (collision_point + a_normal * (distance_1 + 1), collision_point + b_normal * (distance_2 + 1))
    
def try_hard_push(a, b, distance_1, distance_2):
    threshold = distance_1 + distance_2
    distance = get_distance(a, b)
    if distance < threshold:
        a, b = hard_push(a, b, distance_1, distance_2)
    return a, b
    
def fix_overlap(a, b):
    return hard_push(a.position, b.position, a.radius, b.radius)
    
def calculate_reflection(normal, vector):
    return vector - (2 * normal.dot(vector)) * normal
    
def calculate_sphere_collision(a, b):
    if a.mass == 0 or b.mass == 0:
        return a.velocity
        
    collision_point = calculate_midpoint(a.position, b.position, a.radius, b.radius)
    normal = calculate_normal(a.position, collision_point)
    reflection = calculate_reflection(normal, a.velocity)
    
    total_momentum = a.mass * a.velocity.magnitude + b.mass * b.velocity.magnitude
    reflection.magnitude = total_momentum / (a.mass + b.mass)
    
    return reflection
    
def calculate_individual_damage(object, step):
    acceleration = object.velocity.magnitude * step
    force = object.mass * acceleration
    return force
    
def calculate_damage(a, b, step):
    damage_to_a = calculate_individual_damage(b, step) + 1
    damage_to_b = calculate_individual_damage(a, step) + 1
    if entities.CONTACT_ATTACK in a:
        damage_to_b += a.additional_damage
    if entities.CONTACT_ATTACK in b:
        damage_to_a += b.additional_damage
    return damage_to_a, damage_to_b
    
        
    

class Physics(object):
    def __init__(self, step):
        self.gravity = -900
        self.step = step
        
    def initialize(self, things):
        for e in things:
            if entities.USER_CONTROLLABLE in e:
                e.position = Cartesian(400, 400)
                e.mass = 20.0
                e.dampening = 0.92                    
                if entities.DAMAGEABLE in e:
                    e.health = 400
                    e.max_health = 400
                if entities.ROTATES in e:
                    e.angle = 0
            if entities.ROCK in e:
                # TODO: randomize position
                e.position = Cartesian(random.randint(50, 750), random.randint(50, 750))
                e.mass = random.randint(40, 55)
                e.dampening = random.choice([0.98, 0.99, 0.999])
                if entities.DAMAGEABLE in e:
                    e.health = random.choice(range(500, 1000, 20))
                    e.max_health = e.health
                if entities.ROTATES in e:
                    e.angle = random.random() * math.pi * 2
            if entities.ENEMY in e:
                e.position = Cartesian(random.randint(50, 750), random.randint(50, 750))
                e.mass = random.randint(10, 55)
                e.dampening = random.choice([0.98, 0.99, 0.999])
                if entities.DAMAGEABLE in e:
                    e.health = random.choice(range(40, 300, 20))
                    e.max_health = e.health
                if entities.ROTATES in e:
                    e.angle = random.random() * math.pi * 2
            if entities.STAR in e:
                e.position = Cartesian(random.randint(50, 750), random.randint(50, 750))
                e.mass = random.randint(5, 15)
                e.dampening = random.choice([0.98, 0.99, 0.999])
                if entities.DAMAGEABLE in e:
                    e.health = random.choice(range(20, 40))
                    e.max_health = e.health
                if entities.ROTATES in e:
                    e.angle = random.random() * math.pi * 2
            if entities.MOVEABLE in e:
                e.velocity = Cartesian(0, 0)
                e.acceleration = Cartesian(0, 0)
            if entities.COLLECTOR in e:
                e.draw_radius = 150
                e.push_radius = 50
                e.max_collectable = 1 # Anything else is too buggy for me to bother.
            if entities.BULLET in e:
                e.position = e.initial_position
                e.velocity = e.initial_velocity
                e.mass = 0
                e.dampening = 1.0
                if entities.DAMAGEABLE in e:
                    e.health = 1
                    e.max_health = 1
        
    def process(self, things):
        score = 0
        collectors = [e for e in things if entities.COLLECTOR in e]
        humans = [e for e in collectors if entities.USER_CONTROLLABLE in e]
        if len(humans) == 0:
            human = None
        else:
            human = humans[0]
            
        output = []
        for e in things:
            if entities.SOLID in e:
                for other in things:
                    if other == e:
                        continue
                    if entities.SOLID not in other:
                        continue
                    if is_colliding(e, other):
                        self.calculate_collision(e, other)
                        self.calculate_entity_damage(e, other)
                        if entities.BULLET not in e and entities.BULLET not in other:
                            explosion = entities.make_explosion(
                                calculate_midpoint(e.position, other.position, e.radius, other.radius),
                                'Collision')
                            output.append(explosion)
                        else:
                            explosion = entities.make_explosion(
                                calculate_midpoint(e.position, other.position, e.radius, other.radius),
                                'BULLET')
                            output.append(explosion)
                        
                # Wall collision
                self.calculate_wall_collision(e)
                
            if entities.ORBITABLE in e:
                for collector in collectors:
                    if not entities.COLLECTOR_ACTIVE in collector:
                        continue
                    distance = get_distance(e.position, collector.position)
                    if distance >= collector.draw_radius and e not in collector.collected_objects:
                        continue
                        
                    if len(collector.collected_objects) < collector.max_collectable:                    
                        if e not in collector.collected_objects:
                            collector.collected_objects.append(e)
                            
            if entities.COLLECTOR_ACTIVE in e:
                for orbiting in e.collected_objects:
                    if entities.DEAD in orbiting:
                        remove(e.collected_objects, orbiting)
                        
                    o_distance = get_distance(orbiting.position, e.position)
                    
                    normal = calculate_normal(e.position, orbiting.position)
                    
                    if o_distance > e.draw_radius:
                        orbiting.position = e.position - e.draw_radius * normal
                        
                    if o_distance < e.push_radius + orbiting.radius:
                        orbiting.position = e.position - (e.push_radius + orbiting.radius) * normal
                    
                    #normal.magnitude = orbiting.mass * e.mass / o_distance**2
                    orbiting.velocity += normal
                                
            if entities.MOVEABLE in e:
                e.velocity += e.acceleration
                e.velocity *= e.dampening
                
                if e.velocity.magnitude >= 15:
                    e.velocity.magnitude = 15
                
                e.position += e.velocity
                
            if entities.ROTATES in e:
                if entities.FACES_USER in e:
                    if human is not None:
                        vector = e.position - human.position
                        e.angle = -vector.angle
                    
        return output, None
        
    def heartbeat(self):
        '''Called after the loop, for anything which is vital for keeping
        the game running but doesn't actually process anything.'''
        pass
            
    def calculate_collision(self, e, other):
        e.position, other.position = fix_overlap(e, other)
        e.velocity = calculate_sphere_collision(e, other)
        other.velocity = calculate_sphere_collision(other, e)
        
    def calculate_wall_collision(self, e):
        if entities.BOUNDED in e:
            if e.position.x - e.radius < 0:
                e.position.x = e.radius
                e.velocity = calculate_reflection(Cartesian(1, 0), e.velocity)
            if e.position.x + e.radius > 800:
                e.position.x = 800 - e.radius
                e.velocity = calculate_reflection(Cartesian(-1, 0), e.velocity)
            if e.position.y - e.radius < 0:
                e.position.y = e.radius
                e.velocity = calculate_reflection(Cartesian(0, 1), e.velocity)
            if e.position.y + e.radius > 800:
                e.position.y = 800 - e.radius
                e.velocity = calculate_reflection(Cartesian(0, -1), e.velocity)
        else:
            out = [
                e.position.x < 0 - e.radius * 2,
                e.position.x > 800 + e.radius * 2,
                e.position.y < 0 - e.radius * 2,
                e.position.y > 800 + e.radius * 2
            ]
            if True in out:
                e.add(entities.DEAD)
        
    def calculate_entity_damage(self, e, other):
        damage_to_a, damage_to_b = calculate_damage(e, other, self.step)
        if entities.DAMAGEABLE in e:
            e.health -= damage_to_a
            if e.health <= 0:
                e.add(entities.DEAD)
        if entities.DAMAGEABLE in other:
            other.health -= damage_to_b
            if other.health <= 0:
                other.add(entities.DEAD)
        
                
            