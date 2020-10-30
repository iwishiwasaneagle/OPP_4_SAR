import matlab.engine

class MatlabHelper:
    def __init__(self):
        self.eng = matlab.engine.start_matlab()