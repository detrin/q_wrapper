# -*- coding: utf-8 -*-

from timeit import default_timer as timer

class Timer():
    """Timer object for debbuging purposes only. """
    def __init__(self):
        self.time_flags = []
        self.time_names = []
        pass

    def flag(self, name):
        """Flag point in code."""
        self.time_flags.append(timer())
        self.time_names.append(name)
    
    def evaluate(self):
        """Eval time spent on each flag."""
        self.flag("")
        print("### Beginning of timer info ###")
        for ind in range(len(self.time_flags)-1):
            delta_t = self.time_flags[ind+1]-self.time_flags[ind]
            print(self.time_names[ind], delta_t)
        print("### End of timer info ###")