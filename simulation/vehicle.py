from math import cos, sin
import numpy as np
import matplotlib.pyplot as plt
from simulation.parameters import *
from data_models.positional.pose import Pose
from data_models.positional.RPY import RPY
from typing import List

class Vehicle():
    def __init__(self, pos=Pose.zero(), dpos=Pose.zero(), ddpos=Pose.zero(), rpy:RPY=RPY.zero(), drpy:RPY=RPY.zero(), size:float=0.25, des_yaw:float=0, animate=True):

        self._p1 = np.array([size / 2, 0, 0, 1]).T
        self._p2 = np.array([-size / 2, 0, 0, 1]).T
        self._p3 = np.array([0, size / 2, 0, 1]).T
        self._p4 = np.array([0, -size / 2, 0, 1]).T

        self.pos = pos
        self.dpos = dpos
        self.ddpos = ddpos
        self.rpy = rpy
        self.drpy = drpy

        self.animate = animate
        self.size = size

        self.data = {'pos':{'x':[],'y':[],'z':[]}, 'vel':[], 'acc':[], 'RPY':[]}

        self.des_yaw = des_yaw

        if self.animate:
            plt.ion()
            fig = plt.figure()
            # for stopping simulation with the esc key.
            fig.canvas.mpl_connect('key_release_event',
                    lambda event: [exit(0) if event.key == 'escape' else None])

            self._ax = fig.add_subplot(111)


    def step(self, des_pos: Pose, des_vel: Pose, des_acc: Pose) -> None:

        des_x_pos, des_y_pos, des_z_pos = des_pos
        des_x_vel, des_y_vel, des_z_vel = des_vel
        des_x_acc, des_y_acc, des_z_acc = des_acc

        thrust = m * (g + des_z_acc + Kp_z * (des_z_pos -
                                              self.pos.z) + Kd_z * (des_z_vel - self.dpos.z))

        roll_torque = Kp_roll * \
            (((des_x_acc * sin(self.des_yaw) - des_y_acc * cos(self.des_yaw)) / g) - self.rpy.roll)
        pitch_torque = Kp_pitch * \
            (((des_x_acc * cos(self.des_yaw) - des_y_acc * sin(self.des_yaw)) / g) - self.rpy.pitch)
        yaw_torque = Kp_yaw * (self.des_yaw - self.rpy.yaw)

        self.drpy.roll += roll_torque * dt / Ixx
        self.drpy.pitch += pitch_torque * dt / Iyy
        self.drpy.yaw += yaw_torque * dt / Izz

        self.rpy.roll += self.drpy.roll * dt
        self.rpy.pitch += self.drpy.pitch * dt
        self.rpy.yaw += self.drpy.yaw * dt

        R = self.rotation_matrix()

        acc = (np.matmul(R, np.array(
            [0, 0, thrust.item()]).T) - np.array([0, 0, m * g]).T) / m

        self.ddpos.x = acc[0]
        self.ddpos.y = acc[1]
        self.ddpos.z = acc[2]
        self.dpos.x += self.ddpos.x * dt
        self.dpos.y += self.ddpos.y * dt
        self.dpos.z += self.ddpos.z * dt
        self.pos.x += self.dpos.x * dt
        self.pos.y += self.dpos.y * dt
        self.pos.z += self.dpos.z * dt
        
        self._store()
        
        if self.animate:
            self._plot()


    def _store(self) -> None:
        self.data['pos']['x'].append(self.pos.x)
        self.data['pos']['y'].append(self.pos.y)
        self.data['pos']['z'].append(self.pos.z)

    def transformation_matrix(self) -> List[List[float]]:
        x = self.pos.x
        y = self.pos.y
        z = self.pos.z
        roll = self.rpy.roll
        pitch = self.rpy.pitch
        yaw = self.rpy.yaw
        return np.array(
            [[cos(yaw) * cos(pitch), -sin(yaw) * cos(roll) + cos(yaw) * sin(pitch) * sin(roll), sin(yaw) * sin(roll) + cos(yaw) * sin(pitch) * cos(roll), x],
             [sin(yaw) * cos(pitch), cos(yaw) * cos(roll) + sin(yaw) * sin(pitch)
              * sin(roll), -cos(yaw) * sin(roll) + sin(yaw) * sin(pitch) * cos(roll), y],
             [-sin(pitch), cos(pitch) * sin(roll), cos(pitch) * cos(yaw), z]
             ])

    def rotation_matrix(self) -> List[List[float]]:
        roll = self.rpy.roll
        pitch = self.rpy.pitch
        yaw = self.rpy.yaw

        return np.array(
        [[cos(yaw) * cos(pitch), -sin(yaw) * cos(roll) + cos(yaw) * sin(pitch) * sin(roll), sin(yaw) * sin(roll) + cos(yaw) * sin(pitch) * cos(roll)],
         [sin(yaw) * cos(pitch), cos(yaw) * cos(roll) + sin(yaw) * sin(pitch) *
          sin(roll), -cos(yaw) * sin(roll) + sin(yaw) * sin(pitch) * cos(roll)],
         [-sin(pitch), cos(pitch) * sin(roll), cos(pitch) * cos(yaw)]
         ])

    def _plot(self) -> None:
        T = self.transformation_matrix()

        p1_t = np.matmul(T, self._p1)
        p2_t = np.matmul(T, self._p2)
        p3_t = np.matmul(T, self._p3)
        p4_t = np.matmul(T, self._p4)

        plt.cla()

        self._ax.plot([p1_t[0], p2_t[0], p3_t[0], p4_t[0]],
                     [p1_t[1], p2_t[1], p3_t[1], p4_t[1]], 'k.')

        self._ax.plot([p1_t[0], p2_t[0]], [p1_t[1], p2_t[1]], 'r-')
        self._ax.plot([p3_t[0], p4_t[0]], [p3_t[1], p4_t[1]], 'r-')

        self._ax.plot(self.data['pos']['x'], self.data['pos']['y'], 'b:')

        plt.xlim(-10, 15)
        plt.ylim(-10, 15)

        plt.pause(0.001)
    
    