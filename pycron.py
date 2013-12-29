#!/usr/bin/python2.7 -B

import re
import sys
import time
import threading, Queue
import traceback

import twitter

class CronExecutor(twitter.LoggingObject):
    def __init__(self, pool_size=1):
        self.name = 'executor'
        self.queue = Queue.Queue()
        self.pool_size = pool_size

    def start(self):
        for i in range(self.pool_size):
            threading.Thread(target=self.run, name="Executor-{0}".format(i)).start()

    def stop(self):
        for i in range(self.pool_size):
            self.queue.put(None)

    def run(self):
        try:
            self.log("{0} starting, #{1}", threading.current_thread().name, twitter.gettid())
            while True:
                action = self.queue.get()
                self.debug("{0}: {1}", threading.current_thread().name, action)
                if not action:
                    break
                try:
                    timeout = 1
                    (f, a, k) = action
                    while (timeout <= 8) and not f(*a, **k):
                        time.sleep(timeout)
                        timeout *= 2
                except Exception as e:
                    self.error("Exception on thread {0}:\n{1}",
                        threading.current_thread().name,
                        traceback.format_exc())
        finally:
            self.log("{0} exiting", threading.current_thread().name)

    def put_queue(self, obj):
        self.queue.put(obj)
        

class CronRunner(twitter.LoggingObject):
    def __init__(self, name, executor, *rules):
        self.name = name
        self.executor = executor
        self.stopped = False
        self.info('--------- --------- --------- --------- --------- --------- --------- ---------------- --------------------------------')
        self.info('seconds   minutes   hours     monthday  month     year      weekday   bot              function                        ')
        self.info('--------- --------- --------- --------- --------- --------- --------- ---------------- --------------------------------')
        self.rules = [ self.parse_rule(*r) for r in rules ]
        self.info('--------- --------- --------- --------- --------- --------- --------- ---------------- --------------------------------')

    def parse_rule(self, rule, action):
        #r = re.compile(r'(\d\d)?(-(\d\d))?(/(\d\d))?')
       
        FIRSTS   = '00-00/01 00-00/01 00-00/01 01-01/01 01-01/01 00-99/01 00-06/01'.split()
        DEFAULTS = '00-59/01 00-59/01 00-23/01 01-31/01 01-12/01 00-99/01 00-06/01'.split()
        MONTHS   = 'jan feb mar apr may jun jul aug sep oct nov dec'.split()
        DAYS     = 'mon tue wed thu fri sat sun'.split()

        rule = rule.lower().split()
        name = action.im_self.name if hasattr(action, 'im_self') else ''
        self.log('{0} {1:16} {2:32}', ' '.join('{0:9}'.format(r) for r in rule), name, action.__name__)

        # replace * with 00-00/01 on the left side of the first non-*
        for (i, v) in enumerate(rule):          
            if v == '*':
                rule[i] = FIRSTS[i]
            else:
                break

        # replace * with 00-max/01 on the right side of the first non-*
        for (j, v) in enumerate(rule):          
            if j <= i:
                continue
            if v == '*':
                rule[j] = DEFAULTS[j]

        # expand month names
        for (m_num, m_name) in enumerate(MONTHS):
            rule[4] = rule[4].replace(m_name, '{0:02}'.format(m_num + 1))

        # expand day names
        for (d_num, d_name) in enumerate(DAYS):
            rule[6] = rule[6].replace(d_name, '{0:02}'.format(d_num))

        rule = (p if '-' in p else p + '-' + p for p in rule)   # double values without -
        rule = (p if '/' in p else p + '/01' for p in rule)     # add interval to values without /

        rule = (re.split('[-/]', r) for r in rule)              # split into three parts
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

    threadnum = 0
    def start(self, get_time):
        name = 'Cron-{0}'.format(CronRunner.threadnum) 
        CronRunner.threadnum += 1
        threading.Thread(name=name, target=self.run, args=[get_time]).start()

    def stop(self):
        self.stopped = True

    def run(self, get_time):
        try:
            self.log("{0} starting, #{1}", threading.currentThread().getName(), twitter.gettid())
            prev = None
            while not self.stopped:
                time.sleep(0.5)
                t = get_time()
                if t.tm_sec == prev:
                    continue
                prev = t.tm_sec
                for action in self.get_runnable_actions(t):
                    self.executor.put_queue((action, [t], {}))
        finally:
            self.log("{0} exiting", threading.currentThread().getName())

