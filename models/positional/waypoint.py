import numpy as np

class Waypoints:
    def __init__(self, *argv):
        self.wps = []
        for arg in argv:
            if isinstance(arg, Waypoint):
                self.wps.append(arg)
    def __getitem__(self,key):
        return self.wps[key]
    def __iter__(self):
        self.n = 0
        return self
    def __next__(self):
        if self.n<self.__len__():
            result = self.wps[self.n]
            self.n += 1
            return result
        else:
            raise StopIteration
    def __len__(self):
        return len(self.wps)

class Waypoint:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    @staticmethod
    def zero():
        return Waypoint(0,0,0)

    def __getitem__(self,key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        else:
            raise KeyError(f"Index key:{key} out of range for XYZ indexing (max. 2)")
    def __iter__(self):
        self.n = 0
        return self
    def __next__(self):
        if self.n < self.__len__():
            result = self.__getitem__(self.n)
            self.n += 1
            return result  
        else:
            raise StopIteration
    def __len__(self):
        return 3