import numpy
from models import Pose

class Vehicle:
    def __init__(self, pos=Pose(0,0), vel=Pose(0,0), acc=Pose(0,0)):
        self.pos = pos 
        self.vel = vel
        self.acc = acc

        self.pos_store = []
        self.vel_store = []
        self.acc_store = []

    def update(self, pos=Pose(0,0), vel=Pose(0,0), acc=Pose(0,0)):
        self.pos += pos
        self.vel += vel
        self.acc += acc

    def step(self, dt=0.01):
        self.vel = self.vel + self.acc*dt
        self.pos = self.pos + self.vel*dt

    def store(self):
        self.pos_store.append(self.pos)
        self.vel_store.append(self.vel)
        self.acc_store.append(self.acc)
