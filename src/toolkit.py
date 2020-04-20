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

class Time_counter:
    def __init__(self):
        self.name_times = []
        self.time_names = []
        self.last_timeflag = time.time()

    def flag(self, name):
        current_flag = time.time()

        if name in self.time_names:
            name_ind = self.time_names.index(name)
        else:
            name_ind = len(self.time_names)
            self.time_names.append(name)
            self.name_times.append(0)

        self.name_times[name_ind] += current_flag - self.last_timeflag
        self.last_timeflag = current_flag

    def evaluate(self, percentage=True):
        if percentage:
            time_total = sum(self.name_times)

        self.flag("")
        print("### Beginning of timer info ###")
        for ind in range(len(self.time_names) - 1):
            r = self.name_times[ind] / time_total * 100
            if percentage:
                time_str = "%.2f %%" % r
            else:
                time_str = str(self.name_times[ind])

            print(self.time_names[ind], time_str)
        print("### End of timer info ###")
