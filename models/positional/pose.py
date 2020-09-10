from models.positional.waypoint import Waypoint

class Pose:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    @staticmethod
    def zero():
        return Pose(0,0,0)
    @staticmethod
    def fromWP(WP):
        return Pose(WP.x, WP.y, WP.z)

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