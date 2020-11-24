import json
import numpy as np
import matplotlib.pyplot as plt
from src.simulation.parameters import *
from src.data_models.positional.pose import Pose, Poses
from src.data_models.positional.angle import Yaw

class Vehicle:
    def __init__(self, pos=Pose.zero(), dpos=Pose.zero(), ddpos=Pose.zero(), des_yaw:float=0, animate:bool=False):
        self.pos = pos
        self.dpos = dpos
        self.ddpos = ddpos
        self.t = 0

        self.animate = animate

        self.data = VehicleSimData()

        if self.animate:
            plt.ion()
            fig = plt.figure()
            fig.canvas.mpl_connect('key_release_event',
                    lambda event: [exit(0) if event.key == 'escape' else None])

            self._ax = fig.add_subplot(111)

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
        
        self._store()

        self.t += dt
        
        if self.animate:
            self._plot()

    def _store(self) -> None:
        self.data.update(self.t, self.pos, self.dpos, self.ddpos)

    def _plot(self) -> None:
        plt.cla()

        self._ax.add_artist(plt.Circle((self.pos.x, self.pos.y), size, color='r'))
        self._ax.plot(self.data.pos.x, self.data.pos.y, 'b:')       

        plt.xlim(self.pos.x-10,self.pos.x+10)
        plt.ylim(self.pos.y-10,self.pos.y+10)

        plt.pause(0.1)

class VehicleSimData:
    def __init__(self) -> None:
        self.t = []
        self.found = []
        self.pos = Poses()
        self.dpos = Poses()
        self.ddpos = Poses()

    def update(self, t, pos, dpos, ddpos):
        self.t.append(np.copy(t))
        self.pos.add(np.copy(pos))
        self.dpos.add(np.copy(dpos))
        self.ddpos.add(np.copy(ddpos))

    def __str__(self) -> str:
        return f"VehicleSimData({self.__dict__})"