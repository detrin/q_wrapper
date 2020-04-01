# -*- coding: utf-8 -*-
"""All tools for debugging and comparing code performance."""

import timeit
import time


class Timer:
    """Timer object for debbuging purposes only. """

    def __init__(self, use_timeit=False):
        self.time_flags = []
        self.time_names = []
        self.use_timeit = use_timeit

    def flag(self, name):
        """Flag point in code."""
        if self.use_timeit:
            self.time_flags.append(timeit.timer())
        else:
            self.time_flags.append(time.time())
        self.time_names.append(name)

    def evaluate(self):
        """Eval time spent on each flag."""
        self.flag("")
        print("### Beginning of timer info ###")
        for ind in range(len(self.time_flags) - 1):
            delta_t = self.time_flags[ind + 1] - self.time_flags[ind]
            print(self.time_names[ind], delta_t)
        print("### End of timer info ###")
