#!/usr/bin/env python

import argparse
import random
random.seed()

def ports():
    return range(1025, 65536)

def easy_hard(hard_side_sockets=256, easy_side_probes=256):
    # On the hard side, create N sockets and send probes to the one
    # (known, correct) ip:port on the easy side. The net effect, for
    # the purposes of this simulation, is that we'll have N port
    # mappings on the hard NAT, all wanting to see traffic from the
    # easy ip:port.
    hard_side_ports = set(random.sample(ports(), k=hard_side_sockets))

    # On the easy side, create a single socket and probe M ports on
    # the hard side.
    easy_side_probes = set(random.sample(ports(), k=easy_side_probes))

    hits = easy_side_probes.intersection(hard_side_ports)
    return len(hits) > 0

def hard_hard(a_probes=256, b_probes=256):
    # On each hard side, probe N targets. Each one results in a random
    # *pair* of ports: the NAT-allocated port, and the target port
    # from which packets must return if they're to cross the firewall.
    a_ports = random.sample(ports(), k=a_probes)
    a_probes = random.sample(ports(), k=a_probes)
    a_state = set(zip(a_ports, a_probes))

    b_ports = random.sample(ports(), k=b_probes)
    b_probes = random.sample(ports(), k=b_probes)
    # Note: probes/ports is flipped compared to a_state, so that we
    # can intersect the two sets and find matches.
    b_state = set(zip(b_probes, b_ports))

    # Traversal only succeeds if the two sides independently guess the
    # same ports (albeit mirrored - A's outbound is B's inbound and
    # vice-versa).
    hits = a_state.intersection(b_state)
    return len(hits) > 0

def probability(a_side=256, b_side=256, hard=False):
    # The math is not quite the same as the classic birthday paradox,
    # because we're looking for collisions between two different sets,
    # rather than collisions within one set. The net result is that
    # the probability curve skews slightly more in our favor, e.g. we
    # get 66% likelihood of success where the straight birthday
    # paradox would get 50%.
    #
    # We do the math on this the somewhat naive way, which means we'll
    # probably accumulate rounding errors even with double precision
    # floats. Since this is just an approximate simulation, that's
    # okay. We could always use higher precision decimals if we wanted
    # to.
    num_options = len(ports())
    if hard:
        # In hard mode, the search space doubles, because we now have
        # to find collisions on _pairs_ of ports, each of which can
        # cover the entire port range.
        num_options *= num_options
    p = 1.0
    for i in range(b_side):
        p *= (num_options-a_side-i)/(num_options-i)
    return 1.0 - p

def main():
    p = argparse.ArgumentParser(description="Calculate birthday paradox probabilities for NAT traversal")
    p.add_argument("--hard", action="store_true", help="Simulate two endpoint-dependent NATs instead of one")
    p.add_argument("--a-side-probes", type=int, default=256, help="number of probe attempts from the A side")
    p.add_argument("--b-side-probes", type=int, default=256, help="number of probe attempts from the B side")
    args = p.parse_args()
    prob = probability(args.a_side_probes, args.b_side_probes, args.hard)
    num_ports = len(ports())
    if args.hard:
        pcta = args.a_side_probes/(num_ports*num_ports)*100
        pctb = args.b_side_probes/(num_ports*num_ports)*100
        print("""
Simulating the hard case:
  peer A -> endpoint-dependent NAT --- endpoint-dependent NAT <- peer B

  A probes {} combinations of (source port, target port)
    (this is {:.2g}% of the search space)
  B probes {} combinations of (source port, target port)
    (this is {:.2g}% of the search space)
""".format(args.a_side_probes, pcta, args.b_side_probes, pctb))
    else:
        pcta = args.a_side_probes/num_ports*100
        pctb = args.b_side_probes/num_ports*100
        print("""
Simulating the easy case:

  peer A -> endpoint-dependent NAT --- endpoint-independent NAT <- peer B

  A probes 1 target port on B from {} source ports
    (this is {:.2g}% of the search space)
  B probes {} target ports on A from 1 source port
    (this is {:.2g}% of the search space)
""".format(args.a_side_probes, pcta, args.b_side_probes, pctb))
    print("Probability of successful traversal: %.2f%%" % (prob*100))

if __name__ == "__main__":
    main()
