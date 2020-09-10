class RPY:
    def __init__(self,roll, pitch, yaw):
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
    
    @staticmethod
    def zero():
        return RPY(0,0,0)

    def __getitem__(self,key):
        if key == 0:
            return self.roll
        elif key == 1:
            return self.pitch
        elif key == 2:
            return self.yaw
        else:
            raise KeyError(f"Index key:{key} out of range for RPY indexing (max. 2)")
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