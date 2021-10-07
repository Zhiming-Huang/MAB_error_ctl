#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math import floor
from time import time


class Timer:
    def __init__(self):
        self.start_time = None

    def start(self, interval):
        self.start_time = Timer.current_time_in_millis()
        self.interval = interval

    def has_timeout_occured(self):
        cur_time = Timer.current_time_in_millis()
        return cur_time - self.start_time > self.interval

    def is_running(self):
        return self.start_time != None

    def stop(self):
        self.start_time = None
        self.interval = None

    def restart(self, interval):
        self.start(interval)

    @staticmethod
    def current_time_in_millis():
        return int(floor(time() * 1000))
