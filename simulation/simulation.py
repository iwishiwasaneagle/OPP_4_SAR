from math import cos, sin
import numpy as np
from simulation.vehicle import Vehicle
from simulation.trajectory import Trajectory, Trajectories
from simulation.parameters import *
from models.positional.waypoint import Waypoint, Waypoints
from models.positional.pose import Pose

def simulation(waypoints): 

    trajectories = Trajectories()    
    for i,wp in enumerate(waypoints):
        trajectory = Trajectory(waypoints[i], waypoints[(i + 1) % len(waypoints)], 5)
        trajectories.add(trajectory)

    vehicle = Vehicle(pos=Pose.fromWP(waypoints[0]),size=3, animate=animate)

    t = 0    
    n_run = 2
    for trajectory in trajectories:
        
        if trajectories.loop >= n_run:
            break

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

    print("Done")

def main():
    waypoints = Waypoints(Waypoint(5,0,0), Waypoint(10, 0, 0), Waypoint(10, 10, 0),Waypoint(0, 10, 0))

    simulation(waypoints)

if __name__ == "__main__":
    main()