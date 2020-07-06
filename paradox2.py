#!/usr/bin/env python
#
# This file implements the birthday paradox attack between two NATs
# with endpoint-dependent mapping and endpoint-dependent firewalling.
#
# It never successfully finds a path in most cases, expect it to run
# for ever.
from __future__ import division
import random
random.seed()

class Clock(object):
    def __init__(self):
        self.time = 0.0

    def advance(self, delta):
        self.time+=delta

    def now(self):
        return self.time

class Mapping(object):
    __slots__ = ['clock', 'lan_port', 'wan_port', 'remote_port', 'until']

    def __init__(self, clock, lan, wan, remote):
        self.clock = clock
        self.lan_port = lan
        self.wan_port = wan
        self.remote_port = remote
        self.until = 0

    def expired(self):
        return self.clock.now() > self.until

    def refresh(self, until):
        self.until = until

NAT_SIZE = 10000
PPS = 20
MAX_PORT = 65535

class NAT(object):
    def __init__(self, clock, mapping_valid_window):
        self.clock = clock
        self.by_remote_port = {} # remote port -> Mapping
        self.by_all = {} # (WAN port, remote port) -> Mapping
        self.valid_win = mapping_valid_window

    def guess(self, other):
        now = self.clock.now()

        # Pick a random remote port, and create/update the
        # corresponding NAT mapping to figure out what the
        # corresponding WAN port is.
        src_port = random.randrange(1025, MAX_PORT)
        remote_port = random.randrange(1025, MAX_PORT)
        m = self.by_remote_port.get((src_port, remote_port))
        if not m or m.expired():
            wan_port = random.randrange(1025, MAX_PORT)
            m = Mapping(self.clock, src_port, wan_port, remote_port)
            self.by_remote_port[src_port, remote_port] = m
            self.by_all[(wan_port, remote_port)] = m
        m.refresh(self.clock.now()+self.valid_win)

        # Now we have both the WAN port and remote port, see if
        # there's a matching unexpired mapping in other.
        return other.has_mapping(remote_port, m.wan_port)

    def has_mapping(self, wan_port, remote_port):
        m = self.by_all.get((wan_port, remote_port))
        return not (m is None or m.expired())

def attempt():
    clock = Clock()
    a, b = NAT(clock, NAT_SIZE/PPS), NAT(clock, NAT_SIZE/PPS)

    i=0
    while not (a.guess(b) or b.guess(a)):
        i+=1
        clock.advance(1/PPS)
        if i%10000 == 0:
            print("{} attempts".format(i))
    print("guessed after {} attempts", i)

attempt()
