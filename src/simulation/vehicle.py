import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from src.simulation.parameters import *
from src.data_models.positional.pose import Pose, Poses
from src.data_models.positional.angle import Yaw

class Vehicle:
    def __init__(self, pos=Pose.zero(), dpos=Pose.zero(), ddpos=Pose.zero(), des_yaw:float=0):
        self.pos = pos
        self.dpos = dpos
        self.ddpos = ddpos
        self.t = 0
        self.c = -1

        self.data = VehicleSimData()

    @property
    def yaw(self):
        return Yaw(np.arctan2(self.dpos.y, self.dpos.x))

    @property
    def drag_force(self):
        d = 10
        return d*np.square(self.dpos.x), d*np.square(self.dpos.y)

    def step(self, des_pos: Pose, des_vel: Pose, des_acc: Pose) -> None:
        des_x_pos, des_y_pos = des_pos
        des_x_vel, des_y_vel = des_vel
        des_x_acc, des_y_acc = des_acc
        F_Dx, F_Dy = self.drag_force

        ## Controller
        T_x = m*des_x_acc + F_Dx
        T_y = m*des_y_acc + F_Dy        

        ## Dynamics
        self.ddpos.x = (T_x-F_Dx)/m
        self.ddpos.y = (T_y-F_Dy)/m

        ## Euler integration
        self.dpos.x += self.ddpos.x * dt
        self.dpos.y += self.ddpos.y * dt
        self.pos.x += self.dpos.x * dt
        self.pos.y += self.dpos.y * dt
        
        if self.c%int(0.5/dt) == 0:
            self._store()
        self.c+=1

        self.t += dt

    def _store(self) -> None:
        self.data.update(self.t, self.pos, self.dpos, self.ddpos)

class VehicleSimData:
    def __init__(self) -> None:
        self.t = []
        self.found = []
        self.pos = []
        self.dpos = []
        self.ddpos = []

    def update(self, t, pos, dpos, ddpos):
        self.t.append(t)
        self.pos.append([pos.x,pos.y])
        self.dpos.append([dpos.x,dpos.y])
        self.ddpos.append([ddpos.x,ddpos.y])


    def __str__(self) -> str:
        return f"VehicleSimData({self.__dict__})"