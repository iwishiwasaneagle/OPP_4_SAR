import numpy as np

class Pose:
    def __init__(self,x=0,y=0):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"Pose(x:{self.x},y:{self.y})"

    def __add__(self, other):
        if isinstance(other, Pose):
            return Pose(self.x+other.x,self.y+other.y)
        else:
            raise AttributeError(f"Not of type Pose [{type(other)}]")

    def __sub__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if isinstance(other, (float, int)):
            return Pose(self.x*other, self.y*other)
        elif isinstance(other, Pose):
            return Pose(self.x*other.x, self.y*other.y)
        else:
            raise AttributeError(f"Not of type Pose or float/int [{type(other)}]")

    def __eq__(self, value):
        return round(self.x,2)==round(value.x,2) and round(self.y,2)==round(value.y,2)

    def normalize(self):
        return np.linalg.norm((self.x,self.y))

    def toTuple(self):
        return (self.x, self.y)

if __name__ == "__main__":

    print(Pose(1,1)+Pose(1,1))
    print(Pose(1,1)*Pose(1,1))
    print(Pose(1,1)*3)