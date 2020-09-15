import numpy as np
from data_models.positional.waypoint import Waypoint, Waypoints
from data_models.positional.pose import Pose
from data_models.positional.abstractListObject import AbstractListObject

from typing import List, TypeVar, Tuple


T = TypeVar('T', bound='Trajectories')
U = TypeVar('U', bound='Trajectory')
class Trajectories(AbstractListObject):
    def __init__(self, *argv):
        super().__init__(*argv)
    
    
class Trajectory:
    def __init__(self, start_pos: Waypoint=Waypoint.zero(), dest_pos: Waypoint=Waypoint.zero(), T: float=5, start_vel:Pose=Pose.zero(), dest_vel:Pose=Pose.zero(), start_acc:Pose=Pose.zero(), dest_acc:Pose=Pose.zero()):

        self.start_pos = start_pos
        self.dest_pos = dest_pos

        self.start_vel = start_vel
        self.dest_vel = dest_vel

        self.start_acc = start_acc
        self.dest_acc = dest_acc

        self.T = T

        self.solve()

    def solve(self) -> None:
        A = np.array(
            [[0, 0, 0, 0, 0, 1], # f(t=0)
             [self.T**5, self.T**4, self.T**3, self.T**2, self.T, 1], # f(t=T)
             [0, 0, 0, 0, 1, 0], # f'(t=0)
             [5*self.T**4, 4*self.T**3, 3*self.T**2, 2*self.T, 1, 0], # f'(t=T)
             [0, 0, 0, 2, 0, 0], # f''(t=0)
             [20*self.T**3, 12*self.T**2, 6*self.T, 2, 0, 0] # f''(t=T)
            ])

        b_x = np.array(
            [[self.start_pos.x],
             [self.dest_pos.x],
             [self.start_vel.x],
             [self.dest_vel.x],
             [self.start_acc.x],
             [self.dest_acc.x]
            ])

        b_y = np.array(
            [[self.start_pos.y],
             [self.dest_pos.y],
             [self.start_vel.y],
             [self.dest_vel.y],
             [self.start_acc.y],
             [self.dest_acc.y]
            ])
            
        b_z = np.array(
            [[self.start_pos.z],
             [self.dest_pos.z],
             [self.start_vel.z],
             [self.dest_vel.z],
             [self.start_acc.z],
             [self.dest_acc.z]
            ])
        

        self.coeffs = {'x':np.linalg.solve(A, b_x),'y':np.linalg.solve(A, b_y),'z':np.linalg.solve(A, b_z)}
    
    def __getitem__(self,key: int) -> Tuple[float]:
        if key<len(self.x):
            return (self.x[self.n], self.y[self.n], self.z[self.n])
        else:
            raise KeyError(f"Index key:{key} out of range for XYZ indexing (max. {self.__len__()})")
    def __iter__(self) -> U:
        self._n = 0
        return self
    def __next__(self) -> U:
        if self._n < self.__len__():
            return self.__getitem__(self._n)
        else:
            raise StopIteration

    def __len__(self) -> int:
        return len(self.x)

    def acceleration(self, t: float) -> Pose:
        calc = lambda c,t: 20 * c[0] * t**3 + 12 * c[1] * t**2 + 6 * c[2] * t + 2 * c[3]

        return Pose(calc(self.coeffs['x'], t), calc(self.coeffs['y'], t), calc(self.coeffs['z'], t))
    
    def velocity(self, t: float) -> Pose:
        calc = lambda c,t: 5 * c[0] * t**4 + 4 * c[1] * t**3 + 3 * c[2] * t**2 + 2 * c[3] * t + c[4]

        return Pose(calc(self.coeffs['x'], t), calc(self.coeffs['y'], t), calc(self.coeffs['z'], t))

    def position(self, t: float) -> Pose:
        calc = lambda c,t: c[0] * t**5 + c[1] * t**4 + c[2] * t**3 + c[3] * t**2 + c[4] * t + c[5]

        return Pose(calc(self.coeffs['x'], t), calc(self.coeffs['y'], t), calc(self.coeffs['z'], t))
