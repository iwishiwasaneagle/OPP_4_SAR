import matlab.engine
from loguru import logger
import io
import sys

class StdErr(io.StringIO):
    def write(self,string):
        if not string.isspace() and len(string)>0:
            logger.error("MATLAB "+string.rstrip())
        super().write(string)

class StdOut(io.StringIO):
    def write(self,string):
        if not string.isspace() and len(string)>0:
            logger.debug("MATLAB: "+string.rstrip())
        super().write(string)

class Singleton:
    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)
@Singleton
class MatlabHelper:
    def __init__(self):
        logger.debug(f"Starting {matlab.engine}")
        self.eng = matlab.engine.start_matlab()
        logger.debug(f"{matlab.engine} instance at {self.eng}")
    
    @property
    def kwargs(self) -> dict:
        return {}#'stdout':StdOut(), 'stderr':StdErr()} TODO: Make this work!
