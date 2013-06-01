#!/usr/bin/python

__version__ = '0.2'
__author__ = 'Joost Molenaar <j.j.molenaar@gmail.com>'

# Version history:
# 0.1	initial version

import time
import re
import random

import twitter

# CALCULATIONS ########################################################################################################

def from_radix(r, s, d='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    return 0 if not s else (d.find(s[-1]) + r * from_radix(r, s[:-1]))

def to_radix(r, n, d='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    return '' if not n else (to_radix(r, n/r) + d[n%r])

def convert(f, t, s):
    return to_radix(t, from_radix(f, s))

def parse_mention(s, d='01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    try:
        m = re.search(r'^@convertbot\s*\((.+)\)\s*([^\s]+)', s, re.I)
        if m:
            args, number = m.groups()
            if ',' in args:
                f, t = map(lambda a: int(a.strip()), args.split(','))  
            else:
                f, t = (10, int(args.strip()))
            if 1 <= f <= 36 and 1 <= t <= 36:
                if re.match('['+d[:f]+']+', number, re.I):
                    return f, t, number.upper()
    except:
        pass

def handle_new_mention(id, username, text):
    args = parse_mention(text)
    if not args: 
        return
    f, t, n = args
    reply = '@{0} {1}({2}) = {3}({4})'.format(username, n, f, convert(f, t, n), t)
    while True:
        try:
            twitter.post_reply_to(id, reply)
            break
        except twitter.FailWhale as fail:
            twitter.log('FAIL WHALE: {0}', fail.args)        
    
def handle_new_mentions(mentions):
    if not mentions: 
        return
    twitter.log(mentions)
    the_goodies = [ (id, user, text) for (id, (text, user, _))  in mentions.items() ]
    for args in the_goodies:
        handle_new_mention(*args)
    twitter.CONFIG['latest_mention'] = max(args[0] for args in the_goodies)

def post_time(h, m, is_dst):
    base = random.randint(2,36)
    text = 'Current {0} time in base {1} is {2}:{3}'.format(
        'UTC+2' if is_dst else 'UTC+1',
        base,
        to_radix(base, h) or 0,
        to_radix(base, m) or 0)
    while True:
        try:
            twitter.post_status(text)
            break
        except twitter.FailWhale as fail:
            twitter.log('FAIL WHALE: {0}', fail.args)        

# MAIN LOOP ###########################################################################################################

CONFIG_FILE = 'cfg/convertbot.json'

def main():
    twitter.log('convertbot.py starting at {0}', time.ctime())

    # check credentials because that's important
    try:
        twitter.get_verify()
        twitter.log("Account verification OK! We're good to go.")
    except twitter.FailWhale as fail:
	twitter.log('FAIL WHALE: {0}', fail.args)
        twitter.log('AAIIIIIIEEE! Mein Leben! Please check OAuth credentials and retry')
        return

    # repeat until heat death of universe
    beeped = False
    while True:
        # be quick to check if it's time
        time.sleep(0.5)

        # get UTC and local time
        t = time.time()
        loc = time.localtime(t)

        if (loc.tm_sec == 0):
            if (random.randint(0, 59) == 42) or not beeped:
                while True:
                    try:
                        post_time(loc.tm_hour, loc.tm_min, loc.tm_isdst == 1)
                        beeped = True
                        break
                    except twitter.FailWhale as fail:
                        twitter.log('FAIL WHALE: {0}', fail.args)
            else:
                twitter.log('No dice')

            while True:
                try:
                    new_mentions = twitter.get_new_mentions(twitter.CONFIG['latest_mention'])
                    handle_new_mentions(new_mentions)
                    break
                except twitter.FailWhale as fail:
                    twitter.log('FAIL WHALE: {0}', fail.args)

            twitter.save_config(CONFIG_FILE)

class ConvertBot(twitter.TwitterAPI):
    def post_time(self, t):
        if random.randint(0, 2000) != 42:
            return True

        base = random.randint(2,36)
        text = u'Current {0} time in base {1} is {2}:{3}'.format(
            'UTC+2' if t.tm_isdst else 'UTC+1',
            base,
            to_radix(base, t.tm_hour) or 0,
            to_radix(base, t.tm_min) or 0)

        try:
            self.info('Posting status: {0} ({1})', repr(text), len(text))
            self.post_statuses_update(status=text)
            return True
        except twitter.FailWhale as fail:
            self.log('FAIL WHALE: {0}', fail.args)        
            return False

if __name__ == '__main__':
    assert from_radix(2, '1010') == 10
    assert from_radix(36, '1Z') == 71

    assert to_radix(2, 10) == '1010'
    assert to_radix(36, 2) == '2'
    assert to_radix(36, 71) == '1Z'

    assert convert(10, 2, '10') == '1010'
    assert convert(2, 36, '1000111') == '1Z'

    assert parse_mention('@convertbot(2,30) 10011100') == (2, 30, '10011100')
    assert parse_mention('@convertbot(16) 111') == (10, 16, '111')
    assert parse_mention('@convertbot(16,10) DeadBeef') == (16, 10, 'DEADBEEF')
    assert parse_mention('@convertbot(16,10) b00b5 quux fasd') == (16, 10, 'B00B5')
    assert parse_mention('@convertbot (16,10) b00b5 quux fasd') == (16, 10, 'B00B5')
    
    twitter.load_config(CONFIG_FILE)
    main()

	
