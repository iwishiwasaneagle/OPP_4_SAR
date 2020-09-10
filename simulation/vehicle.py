from math import cos, sin
import numpy as np
import matplotlib.pyplot as plt
from simulation.parameters import *
from models.positional.pose import Pose
from models.positional.RPY import RPY

class Vehicle():
    def __init__(self, pos=Pose.zero(), dpos=Pose.zero(), ddpos= Pose.zero(), RPY=RPY.zero(), dRPY=RPY.zero(), size=0.25, des_yaw=0, animate=True):

        self.p1 = np.array([size / 2, 0, 0, 1]).T
        self.p2 = np.array([-size / 2, 0, 0, 1]).T
        self.p3 = np.array([0, size / 2, 0, 1]).T
        self.p4 = np.array([0, -size / 2, 0, 1]).T

        self.pos = pos
        self.dpos = dpos
        self.ddpos = ddpos
        self.RPY = RPY
        self.dRPY = dRPY

        self.animate = animate

        self.data = {'pos':{'x':[],'y':[],'z':[]}, 'vel':[], 'acc':[], 'RPY':[]}
        self.pos_data = []

        self.des_yaw = des_yaw

        if self.animate:
            plt.ion()
            fig = plt.figure()
            # for stopping simulation with the esc key.
            fig.canvas.mpl_connect('key_release_event',
                    lambda event: [exit(0) if event.key == 'escape' else None])

            self.ax = fig.add_subplot(111)


    def step(self, des_pos, des_vel, des_acc):

        des_x_pos, des_y_pos, des_z_pos = des_pos
        des_x_vel, des_y_vel, des_z_vel = des_vel
        des_x_acc, des_y_acc, des_z_acc = des_acc

        thrust = m * (g + des_z_acc + Kp_z * (des_z_pos -
                                              self.pos.z) + Kd_z * (des_z_vel - self.dpos.z))

        roll_torque = Kp_roll * \
            (((des_x_acc * sin(self.des_yaw) - des_y_acc * cos(self.des_yaw)) / g) - self.RPY.roll)
        pitch_torque = Kp_pitch * \
            (((des_x_acc * cos(self.des_yaw) - des_y_acc * sin(self.des_yaw)) / g) - self.RPY.pitch)
        yaw_torque = Kp_yaw * (self.des_yaw - self.RPY.yaw)

        self.dRPY.roll += roll_torque * dt / Ixx
        self.dRPY.pitch += pitch_torque * dt / Iyy
        self.dRPY.yaw += yaw_torque * dt / Izz

        self.RPY.roll += self.dRPY.roll * dt
        self.RPY.pitch += self.dRPY.pitch * dt
        self.RPY.yaw += self.dRPY.yaw * dt

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

        self.store()
        
        if self.animate:
            self.plot()


    def store(self):
        self.data['pos']['x'].append(self.pos.x)
        self.data['pos']['y'].append(self.pos.y)
        self.data['pos']['z'].append(self.pos.z)

    def transformation_matrix(self):
        x = self.pos.x
        y = self.pos.y
        z = self.pos.z
        roll = self.RPY.roll
        pitch = self.RPY.pitch
        yaw = self.RPY.yaw
        return np.array(
            [[cos(yaw) * cos(pitch), -sin(yaw) * cos(roll) + cos(yaw) * sin(pitch) * sin(roll), sin(yaw) * sin(roll) + cos(yaw) * sin(pitch) * cos(roll), x],
             [sin(yaw) * cos(pitch), cos(yaw) * cos(roll) + sin(yaw) * sin(pitch)
              * sin(roll), -cos(yaw) * sin(roll) + sin(yaw) * sin(pitch) * cos(roll), y],
             [-sin(pitch), cos(pitch) * sin(roll), cos(pitch) * cos(yaw), z]
             ])

    def rotation_matrix(self):
        roll = self.RPY.roll
        pitch = self.RPY.pitch
        yaw = self.RPY.yaw

        return np.array(
        [[cos(yaw) * cos(pitch), -sin(yaw) * cos(roll) + cos(yaw) * sin(pitch) * sin(roll), sin(yaw) * sin(roll) + cos(yaw) * sin(pitch) * cos(roll)],
         [sin(yaw) * cos(pitch), cos(yaw) * cos(roll) + sin(yaw) * sin(pitch) *
          sin(roll), -cos(yaw) * sin(roll) + sin(yaw) * sin(pitch) * cos(roll)],
         [-sin(pitch), cos(pitch) * sin(roll), cos(pitch) * cos(yaw)]
         ])

    def plot(self):  
        T = self.transformation_matrix()

        p1_t = np.matmul(T, self.p1)
        p2_t = np.matmul(T, self.p2)
        p3_t = np.matmul(T, self.p3)
        p4_t = np.matmul(T, self.p4)

        plt.cla()

        self.ax.plot([p1_t[0], p2_t[0], p3_t[0], p4_t[0]],
                     [p1_t[1], p2_t[1], p3_t[1], p4_t[1]], 'k.')

        self.ax.plot([p1_t[0], p2_t[0]], [p1_t[1], p2_t[1]], 'r-')
        self.ax.plot([p3_t[0], p4_t[0]], [p3_t[1], p4_t[1]], 'r-')

        self.ax.plot(self.data['pos']['x'], self.data['pos']['y'], 'b:')

        plt.xlim(-10, 15)
        plt.ylim(-10, 15)

        plt.pause(0.001)
    
    