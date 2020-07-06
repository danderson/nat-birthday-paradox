#!/usr/bin/env python
#
# This file implements the birthday paradox attack between two NATs
# with endpoint-dependent mapping and endpoint-dependent firewalling.
#
# It never successfully finds a path in most cases, expect it to run
# for ever.

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
    def __init__(self, clock, wan, remote):
        self.clock = clock
        self.wan_port = wan
        self.remote_port = remote
        self.until = 0

    def expired(self):
        return self.clock.now() > self.until

    def refresh(self, until):
        self.until = until

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
        remote_port = random.randrange(1025, 65535)
        m = self.by_remote_port.get(remote_port)
        if not m or m.expired():
            wan_port = random.randrange(1025, 65535)
            m = Mapping(self.clock, wan_port, remote_port)
            self.by_remote_port[remote_port] = m
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
    a, b = NAT(clock, 10), NAT(clock, 10)

    i=0
    while not (a.guess(b) or b.guess(a)):
        i+=1
        clock.advance(0.05)
        if i%10000 == 0:
            print("{} attempts".format(i))
    print("guessed after {} attempts", i)

attempt()
