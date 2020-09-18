from math import cos, sin
import numpy as np
from simulation.vehicle import Vehicle
from simulation.trajectory import Trajectory, Trajectories
from simulation.parameters import *
from data_models.positional.waypoint import Waypoint, Waypoints
from data_models.positional.pose import Pose
from typing import List, Tuple

class simulation:
    def __init__(self, waypoints: Waypoints=Waypoints()):
        self.waypoints=waypoints
        self.trajectories=Trajectories()
    
    def run(self) -> Vehicle:
        for i,wp in enumerate(self.waypoints):
            trajectory = Trajectory(self.waypoints[i], self.waypoints[(i + 1) % len(self.waypoints)], 0.5, start_vel=Pose(1,1), dest_vel=Pose(1,1))
            self.trajectories.add(trajectory)

        vehicle = Vehicle(pos=Pose.fromWP(self.waypoints[0]), animate=animate)

        t = 0   
        for trajectory in self.trajectories:
            t_local = 0
            while t_local <= trajectory.T:
                # Calc desired position, velocity and acceleration from generated polynomial trajectory
                des_pos = trajectory.position(t_local)
                des_vel = trajectory.velocity(t_local)
                des_acc = trajectory.acceleration(t_local)

                # Step the vehicle
                vehicle.step(des_pos, des_vel, des_acc)

                # Update time
                t_local += dt
                t += dt

        return vehicle
