import numpy as np
from models.positional.waypoint import Waypoint, Waypoints
from models.positional.pose import Pose

class Trajectories:
    def __init__(self, items=[]):
        self.items=items

    def __getitem__(self, key):
        return self.items[key]
    def __len__(self):
        return len(self.items)
    def __iter__(self):
        self.n = 0
        self.loop = 0
        return self
    def __next__(self):
        if self.n<self.__len__():
            result = self.__getitem__(self.n)
            self.n+=1
            return result
        else:
            self.n = 0
            self.loop += 1
            return self.__next__()
            
    def add(self, trajectory):
        self.items.append(trajectory)
    
    
class Trajectory:
    def __init__(self, start_pos, dest_pos, T, start_vel=Waypoint.zero(), dest_vel=Waypoint.zero(), start_acc=Waypoint.zero(), dest_acc=Waypoint.zero()):

        self.start = start_pos
        self.dest = dest_pos

        self.start_vel = start_vel
        self.dest_vel = dest_vel

        self.start_acc = start_acc
        self.dest_acc = dest_acc

        self.T = T

        self.solve()

    def solve(self):
        A = np.array(
            [[0, 0, 0, 0, 0, 1],
             [self.T**5, self.T**4, self.T**3, self.T**2, self.T, 1],
             [0, 0, 0, 0, 1, 0],
             [5*self.T**4, 4*self.T**3, 3*self.T**2, 2*self.T, 1, 0],
             [0, 0, 0, 2, 0, 0],
             [20*self.T**3, 12*self.T**2, 6*self.T, 2, 0, 0]
            ])

        b_x = np.array(
            [[self.start.x],
             [self.dest.x],
             [self.start_vel.x],
             [self.dest_vel.x],
             [self.start_acc.x],
             [self.dest_acc.x]
            ])

        b_y = np.array(
            [[self.start.y],
             [self.dest.y],
             [self.start_vel.y],
             [self.dest_vel.y],
             [self.start_acc.y],
             [self.dest_acc.y]
            ])
            
        b_z = np.array(
            [[self.start.z],
             [self.dest.z],
             [self.start_vel.z],
             [self.dest_vel.z],
             [self.start_acc.z],
             [self.dest_acc.z]
            ])
        

        self.x = np.linalg.solve(A, b_x)
        self.y = np.linalg.solve(A, b_y)
        self.z = np.linalg.solve(A, b_z)
    
    def __getitem__(self,key):
        if key<len(self.x):
            return (self.x[self.n], self.y[self.n], self.z[self.n])
        else:
            raise KeyError(f"Index key:{key} out of range for XYZ indexing (max. {self.__len__()})")
    def __iter__(self):
        self.n = 0
        return self
    def __next__(self):
        if self.n < self.__len__():
            return self.__getitem__(self.n)
        else:
            raise StopIteration

    def __len__(self):
        return len(self.x_c)

    def acceleration(self, t):
        calc = lambda c,t: 20 * c[0] * t**3 + 12 * c[1] * t**2 + 6 * c[2] * t + 2 * c[3]

        return calc(self.x, t), calc(self.y, t), calc(self.z, t)
    
    def velocity(self, t):
        calc = lambda c,t: 5 * c[0] * t**4 + 4 * c[1] * t**3 + 3 * c[2] * t**2 + 2 * c[3] * t + c[4]

        return calc(self.x, t), calc(self.y, t), calc(self.z, t)

    def position(self, t):
        calc = lambda c,t: c[0] * t**5 + c[1] * t**4 + c[2] * t**3 + c[3] * t**2 + c[4] * t + c[5]

        return calc(self.x, t), calc(self.y, t), calc(self.z, t)
