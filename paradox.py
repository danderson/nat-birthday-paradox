#!/usr/bin/env python
#
# This file implements the birthday paradox attack between two NATs
# with endpoint-dependent mapping and endpoint-independent
# firewalling.

import random
random.seed()

# Each round, both sides generate a random secret of their own (the
# mapped port on their NAT), and try to guess the other side's secret
# (the mapped port on the remote NAT). Success is when either one
# guesses any of the other side's N previous secrets.

class Clock(object):
    def __init__(self):
        self.time = 0

    def advance(self, delta):
        self.time += delta

    def now(self):
        return self.time

class Device(object):
    def __init__(self, clock, valid_window):
        self.clock = clock
        self.valid_window = valid_window
        self.mapped = {}

    def guess(self, other):
        """Try to guess a working port on other.

        Returns True if we guessed correctly (meaning a packet was
        delivered), False otherwise.

        As a side-effect, this also opens a new port on self, which
        others could use to reach self.
        """
        myPort = random.randrange(1025, 65535)
        self.mapped[myPort] = self.clock.now()

        theirPort = random.randrange(1025, 65535)
        hit = other.mapped.get(theirPort)
        if not hit or self.clock.now()-hit > other.valid_window:
            return False
        return True

def attempt(valid_window_secs=10, xmit_delta=0.1):
    clock = Clock()
    a, b = Device(clock, valid_window_secs), Device(clock, valid_window_secs)

    i=1
    while not (a.guess(b) or b.guess(a)):
        i+=1
        clock.advance(xmit_delta)
    return i, clock.now()

def main():
    p = argparse.ArgumentParser(description="Simulate the NAT birthday paradox")
    p.add_argument("-i", "--iterations", type=int, default=100)
    p.add_argument("-x", "--probe-interval", type=float, default=0.1)
    p.add_argument("-v", "--mapping-valid-time", type=float, fefault=10)
    
attempts = 1000
window_secs = 10
delta = 0.1

results = [attempt() for _ in range(attempts)]
times = [x[1] for x in results]
min_time, max_time = int(min(times)), int(max(times))
avg_time = sum(times)/len(times)
median_time = sorted(times)[len(times)//2]

buckets = [0 for _ in range((max_time//5)+1)]
for t in times:
    buckets[int(t)//5] += 1
cum = [sum(buckets[:i+1]) for i in range(len(buckets))]

for i in range(len(buckets)):
    print("{},{},{},{}".format(i*5, buckets[i], cum[i], cum[i]/attempts))
#print("min={}s max={}s avg={}s median={}s".format(min_time, max_time, avg_time, median_time))
