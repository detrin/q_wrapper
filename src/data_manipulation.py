# -*- coding: utf-8 -*-
"""
    Module saveable

    Saveable objects can save themselves to and load themselves from a file.
    
"""

import sys
import os
from os import path as p

import time
import uuid
import pickle
import copy


def loadSave(fun, filename, force_save=False, args=(), path=None):
    """This method will run stated funtion and save its output. On next call
        the output will be automatically loaded.
    """
    if path is None:
        packet = Saveable(filename)
    else:
        packet = Saveable(filename, path=path)

    if packet.is_saved() or force_save:
        data = packet.load()
    else:
        data = fun(*args)
        packet.save(data=data)

    return data


class Saveable:
    """Saveble objects will help you with saving data."""

    def __init__(self, name, path=None):
        self.internal_name = name
        self.filename = name
        self.data = None
        if path is not None:
            self.fullpath = p.join(path, name) + ".pkl"
        else:
            self.fullpath = name + ".pkl"
        # self.hash = None
        self.comment = ""
        self.time = None

    def is_saved(self):
        """Checks if the file exists. """
        return os.path.exists(self.fullpath)

    def save(self, data=None, comment=""):
        """Save data with some additional information."""
        if data is None:
            data = self.data
        data_parcel = {}
        data_parcel["internal_name"] = self.internal_name
        data_parcel["time_saved"] = time.time()
        data_parcel["data"] = data
        data_parcel["uuid"] = self._get_fname()
        # data_parcel["hash"] = hash(data)
        data_parcel["comment"] = comment
        with open(self.fullpath, "wb") as f:
            pickle.dump(data_parcel, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self):
        """Load saved data with additional information."""
        with open(self.fullpath, "rb") as f:
            data_parcel = pickle.load(f)
        self.internal_name = data_parcel["internal_name"]
        self.data = data_parcel["data"]
        # self.hash = data_parcel["hash"]
        self.comment = data_parcel["comment"]
        self.time = data_parcel["time_saved"]

        return self.data

    def _get_fname(self):
        """"Generate UUID."""
        str40 = str(uuid.uuid4())

        return str40

    def __str__(self):
        """In case you want to printing information about saved data."""
        out = []
        out += ["##### Saved object info #####"]
        out += ["Name: " + self.filename]
        out += ["Path: " + self.fullpath]
        out += ["Time saved: " + time.asctime(time.localtime(self.time))]
        out += ["Data type: " + str(type(self.data))]
        # out += ["Hash: "+self.hash]
        size = sys.getsizeof(self.data)
        out += ["Size: " + str(size)]
        if self.comment != "":
            out += ["Comment: " + self.comment]

        return "\n".join(out)
