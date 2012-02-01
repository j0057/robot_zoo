#!/usr/bin/python2.7 -B

import sys
import time
import threading, Queue

import twitter

class CronRunner(twitter.LoggingObject):
    def start_executor(self):
        threading.Thread(target=self.execute).start()

    def stop_executor(self):
        self.queue.put(None)

    def execute(self):
        timeout = 1
        while True:
            action = self.queue.get()
            if not action:
                break
            try:
                (f, a, k) = action
                if f(*a, **k):
                    timeout = 1
                elif timeout <= 8: # try 4 times
                    self.queue.put((f, a, k))
                    time.sleep(timeout)
                    timeout *= 2
                else:
                    timeout = 1
            except:
                self.error('Starting new executor thread!')
                self.start_executor()
                raise

    def __init__(self, *rules):
        self.name = 'main'
        self.info('-------- -------- -------- -------- -------- -------- -------- ---------------- --------------------------------')
        self.info('seconds  minutes  hours    monthday month    year     weekday  bot              function                        ')
        self.info('-------- -------- -------- -------- -------- -------- -------- ---------------- --------------------------------')
        self.rules = [ self.parse_rule(*r) for r in rules ]
        self.info('-------- -------- -------- -------- -------- -------- -------- ---------------- --------------------------------')
        self.queue = Queue.Queue()

    def parse_rule(self, rule, action):
        FIRSTS   = '00-00/01 00-00/01 00-00/01 01-01/01 01-01/01 00-99/01 00-06/01'.split()
        DEFAULTS = '00-59/01 00-59/01 00-23/01 01-31/01 01-12/01 00-99/01 00-06/01'.split()

        rule = rule.split()
        name = action.im_self.name if hasattr(action, 'im_self') else ''
        self.log('{0} {1:16} {2:32}', ' '.join('{0:8}'.format(r) for r in rule), name, action.__name__)

        for (i, v) in enumerate(rule):          
            if v == '*':
                rule[i] = FIRSTS[i]
            else:
                break

        for (j, v) in enumerate(rule):          
            if j <= i:
                continue
            if v == '*':
                rule[j] = DEFAULTS[j]

        rule = (p if '-' in p else p + '-' + p for p in rule)   # double values without -
        rule = (p if '/' in p else p + '/01' for p in rule)     # add interval to values without /

        rule = (p.replace('-','/') for p in rule)               # change - to /
        rule = (r.split('/') for r in rule)                     # split into three parts
        rule = ((int(f), int(t)+1, int(s)) for (f,t,s) in rule) # convert three values to ints
        rule = list(rule)

        yf, yt, ys = rule[-2]                                   # add 2000 to year if needed
        if yf < 100: yf += 2000
        if yt < 101: yt += 2000
        rule[-2] = (yf, yt, ys)

        return (list(rule), action)                 

    def get_runnable_actions(self, t):
        check = lambda x, f, t, s: (f <= x < t) and (((x - f) % s) == 0)
        prev_owner = object()
        curr_owner = None
        for rule, action in self.rules:
            values = zip([t.tm_sec, t.tm_min, t.tm_hour, t.tm_mday, t.tm_mon, t.tm_year, t.tm_wday], rule)
            if all(check(x, *r) for (x, r) in values):
                curr_owner = action.im_self if hasattr(action, 'im_self') else None
                if curr_owner != prev_owner:
                    prev_owner = curr_owner
                    yield action

    def run_utc(self):
        self.run(time.gmtime)

    def run_local(self):
        self.run(time.localtime)

    def run(self, get_time):
        try:
            while True:
                time.sleep(1)
                t = get_time()
                for action in self.get_runnable_actions(t):
                    self.queue.put((action, [t], {}))
        finally:
            self.queue.put(None)

