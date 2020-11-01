import logging
import re
import sys
import time
import threading, queue
import traceback

import twitter

class CronExecutor(object):
    def __init__(self):
        self.name = 'executor'
        self.log = logging.getLogger(__name__)
        self.queue = queue.Queue()

    @twitter.task('Executor-{0}')
    def run(self, cancel):
        while True:
            action = self.queue.get()
            self.log.debug("%s: %r", threading.current_thread().name, action)
            if not action:
                break
            try:
                (f, a, k) = action
                f(*a, **k)
            except Exception as e:
                self.log.exception('Executor caught %s; skipping task', type(e).__name__)

class CronRunner(object):
    def __init__(self, name, get_time, queue, *rules):
        self.name = name
        self.get_time = get_time
        self.queue = queue
        self.log = logging.getLogger(__name__)
        self.log.info('--------- --------- --------- --------- --------- --------- --------- ---------------- --------------------------------')
        self.log.info('seconds   minutes   hours     monthday  month     year      weekday   bot              function                        ')
        self.log.info('--------- --------- --------- --------- --------- --------- --------- ---------------- --------------------------------')
        self.rules = [ self.parse_rule(*r) for r in rules ]
        self.log.info('--------- --------- --------- --------- --------- --------- --------- ---------------- --------------------------------')

    def parse_rule(self, rule, action):
        FIRSTS   = '00-00/01 00-00/01 00-00/01 01-01/01 01-01/01 00-99/01 00-06/01'.split()
        DEFAULTS = '00-59/01 00-59/01 00-23/01 01-31/01 01-12/01 00-99/01 00-06/01'.split()
        MONTHS   = 'jan feb mar apr may jun jul aug sep oct nov dec'.split()
        DAYS     = 'mon tue wed thu fri sat sun'.split()

        rule = rule.lower().split()
        name = action.__self__.name if hasattr(action, 'im_self') else ''
        self.log.info('%s %-16s %-32s', ' '.join('{0:9}'.format(r) for r in rule), name, action.__name__)

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
            values = list(zip([t.tm_sec, t.tm_min, t.tm_hour, t.tm_mday, t.tm_mon, t.tm_year, t.tm_wday], rule))
            if all(check(x, *r) for (x, r) in values):
                curr_owner = action.__self__ if hasattr(action, 'im_self') else None
                if curr_owner != prev_owner:
                    prev_owner = curr_owner
                    yield action

    @twitter.task('Runner-{0}')
    def run(self, cancel):
        try:
            prev = None
            while not cancel:
                t = self.get_time()
                if t.tm_sec == prev:
                    time.sleep(0.2)
                    continue
                prev = t.tm_sec
                for action in self.get_runnable_actions(t):
                    self.queue.put((action, [t], {}))
        finally:
            if threading.current_thread().name.endswith('-0'):
                target_len = self.queue.qsize() + 10
                while self.queue.qsize() < target_len:
                    self.queue.put(None)
                    time.sleep(0.2)

