#!/usr/bin/env python


import math
import random

import entities

def remove(list, item):
    del list[list.index(item)]

def get_distance(a, b):
    return (a - b).to_polar().magnitude
    

class Cartesian(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def pos(self):
        return (int(self.x), int(self.y))
        
    def to_polar(self):
        magnitude = math.sqrt(self.x**2 + self.y**2)
        angle = math.atan2(self.y, self.x)
        return Polar(magnitude, angle)
        
    def to_cartesian(self):
        print "Warning: coercing cartesian to cartesian"
        return self
        
    def copy(self):
        return Cartesian(self.x, self.y)
        
    def dot(self, other):
        return self.x * other.x + self.y * other.y
        
    def magnitude(self):
        return self.to_polar().magnitude
        
    def angle(self):
        return self.to_polar().angle
        
    def __add__(self, other):
        return Cartesian(self.x + other.x, self.y + other.y)
        
    def __sub__(self, other):
        return Cartesian(self.x - other.x, self.y - other.y)
        
    def __div__(self, num):
        return Cartesian(self.x / num, self.y / num)
    
    def __mul__(self, num):
        return Cartesian(self.x * num, self.y * num)
        
    def __rmul__(self, num):
        return self.__mul__(num)
        
    def __repr__(self):
        return 'Cartesian({0}, {1})'.format(self.x, self.y)
        
class Polar(object):
    def __init__(self, magnitude, angle):
        self.magnitude = magnitude
        self.angle = angle
        
    def to_cartesian(self):
        x = math.cos(self.angle) * self.magnitude
        y = math.sin(self.angle) * self.magnitude
        return Cartesian(x, y)
        
    def to_polar(self):
        print "Warning: coercing polar to polar"
        return self
        
    def copy(self):
        return Polar(self.magnitude, self.angle)
        
    def __add__(self, other):
        return (self.to_cartesian() + other.to_cartesian()).to_polar()
        
        
        
def is_colliding(a, b):
    distance = get_distance(a.position, b.position)
    epsilon = 1
    collision_distance = a.radius + b.radius + epsilon
    return distance <= collision_distance
    
def calculate_midpoint(position_1, position_2, radius_1, radius_2):
    normal = calculate_normal(position_1, position_2)
    normal = normal.to_polar()
    normal.magnitude = radius_2
    intersection = position_2 + normal.to_cartesian()
    return intersection
    
def calculate_normal(center, intersection):
    normal = center - intersection
    normal = normal.to_polar()
    normal.magnitude = 1
    return normal.to_cartesian()
    
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
    
    reflection = reflection.to_polar()
    a_vel = a.velocity.to_polar()
    b_vel = b.velocity.to_polar()
    total_momentum = a.mass * a_vel.magnitude + b.mass * b_vel.magnitude
    new_magnitude = total_momentum / (a.mass + b.mass)
    reflection.magnitude = new_magnitude
    
    return reflection.to_cartesian()
    
def calculate_individual_damage(object, step):
    acceleration = object.velocity.magnitude() * step
    force = object.mass * acceleration
    return force
    
def calculate_damage(a, b, step):
    damage_to_a = calculate_individual_damage(b, step) + 1
    damage_to_b = calculate_individual_damage(a, step) + 1
    if entities.ContactAttack in a:
        damage_to_b += a.additional_damage
    if entities.ContactAttack in b:
        damage_to_a += b.additional_damage
    return damage_to_a, damage_to_b
    
        
    

class Physics(object):
    def __init__(self, step):
        self.gravity = -900
        self.step = step
        
    def initialize(self, things):
        for e in things:
            if entities.UserControllable in e:
                e.position = Cartesian(400, 400)
                e.mass = 20.0
                e.dampening = 0.92                    
                if entities.Damageable in e:
                    e.health = 400
                    e.max_health = 400
                if entities.Rotates in e:
                    e.angle = 0
            if entities.Rock in e:
                # TODO: randomize position
                e.position = Cartesian(random.randint(50, 750), random.randint(50, 750))
                e.mass = random.randint(40, 55)
                e.dampening = random.choice([0.98, 0.99, 0.999])
                if entities.Damageable in e:
                    e.health = random.choice(range(500, 1000, 20))
                    e.max_health = e.health
                if entities.Rotates in e:
                    e.angle = random.random() * math.pi * 2
            if entities.Enemy in e:
                e.position = Cartesian(random.randint(50, 750), random.randint(50, 750))
                e.mass = random.randint(10, 55)
                e.dampening = random.choice([0.98, 0.99, 0.999])
                if entities.Damageable in e:
                    e.health = random.choice(range(40, 300, 20))
                    e.max_health = e.health
                if entities.Rotates in e:
                    e.angle = random.random() * math.pi * 2
            if entities.Star in e:
                e.position = Cartesian(random.randint(50, 750), random.randint(50, 750))
                e.mass = random.randint(5, 15)
                e.dampening = random.choice([0.98, 0.99, 0.999])
                if entities.Damageable in e:
                    e.health = random.choice(range(20, 40))
                    e.max_health = e.health
                if entities.Rotates in e:
                    e.angle = random.random() * math.pi * 2
            if entities.Moveable in e:
                e.velocity = Cartesian(0, 0)
                e.acceleration = Cartesian(0, 0)
            if entities.Collector in e:
                e.draw_radius = 150
                e.push_radius = 50
                e.max_collectable = 1 # Anything else is too buggy for me to bother.
            if entities.Bullet in e:
                e.position = e.initial_position
                e.velocity = e.initial_velocity
                e.mass = 0
                e.dampening = 1.0
                if entities.Damageable in e:
                    e.health = 1
                    e.max_health = 1
        
    def process(self, things):
        score = 0
        collectors = [e for e in things if entities.Collector in e]
        humans = [e for e in collectors if entities.UserControllable in e]
        if len(humans) == 0:
            human = None
        else:
            human = humans[0]
            
        output = []
        for e in things:
            if entities.Solid in e:
                for other in things:
                    if other == e:
                        continue
                    if entities.Solid not in other:
                        continue
                    if is_colliding(e, other):
                        self.calculate_collision(e, other)
                        self.calculate_entity_damage(e, other)
                        if entities.Bullet not in e and entities.Bullet not in other:
                            explosion = entities.make_explosion(
                                calculate_midpoint(e.position, other.position, e.radius, other.radius),
                                'Collision')
                            output.append(explosion)
                        else:
                            explosion = entities.make_explosion(
                                calculate_midpoint(e.position, other.position, e.radius, other.radius),
                                'Bullet')
                            output.append(explosion)
                        
                # Wall collision
                self.calculate_wall_collision(e)
                
            if entities.Orbitable in e:
                for collector in collectors:
                    if not collector.is_collector_active:
                        continue
                    distance = get_distance(e.position, collector.position)
                    if distance >= collector.draw_radius and e not in collector.collected_objects:
                        continue
                        
                    if len(collector.collected_objects) < collector.max_collectable:                    
                        if e not in collector.collected_objects:
                            collector.collected_objects.append(e)
                            
                    for orbiting in collector.collected_objects:
                        if entities.Dead in orbiting:
                            remove(collector.collected_objects, orbiting)
                            
                        o_distance = get_distance(orbiting.position, collector.position)
                        
                        normal = calculate_normal(collector.position, orbiting.position)
                        
                        if o_distance > collector.draw_radius:
                            orbiting.position = collector.position - collector.draw_radius * normal
                            
                        if o_distance < collector.push_radius + orbiting.radius:
                            orbiting.position = collector.position - (collector.push_radius + orbiting.radius) * normal
                        
                        normal.magnitude = orbiting.mass * collector.mass / o_distance**2
                        orbiting.velocity += normal
                                
            if entities.Moveable in e:
                e.velocity += e.acceleration
                e.velocity *= e.dampening
                
                e.velocity = e.velocity.to_polar()
                if e.velocity.magnitude >= 15:
                    e.velocity.magnitude = 15
                e.velocity = e.velocity.to_cartesian()
                
                e.position += e.velocity
                
            if entities.Rotates in e:
                if entities.FacesUser in e:
                    if human is not None:
                        vector = (e.position - human.position).to_polar()
                        e.angle = -vector.angle
                    
        return output
            
    def calculate_collision(self, e, other):
        e.position, other.position = fix_overlap(e, other)
        e.velocity = calculate_sphere_collision(e, other)
        other.velocity = calculate_sphere_collision(other, e)
        
    def calculate_wall_collision(self, e):
        if entities.Bounded in e:
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
                e.add(entities.Dead)
        
    def calculate_entity_damage(self, e, other):
        damage_to_a, damage_to_b = calculate_damage(e, other, self.step)
        if entities.Damageable in e:
            e.health -= damage_to_a
            if e.health <= 0:
                e.add(entities.Dead)
        if entities.Damageable in other:
            other.health -= damage_to_b
            if other.health <= 0:
                other.add(entities.Dead)
        
                
            