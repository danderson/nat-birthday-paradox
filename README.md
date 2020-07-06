A small calculator that computes the probability of successfully
traversing endpoint-dependent NATs by exploiting (a variant of) the
birthday paradox. Run `paradox.py --help` for quick instructions.

## Easy birthday attack

In the easy case, one peer is behind an NAT with Endpoint-Depdendent
Mapping (EDM, which varies its WAN source port for each destination),
while the other is behind an NAT with Endpoint-Independent Mapping
(EIM, which uses a single WAN source port for all traffic to a
particular LAN socket).

To traverse this, the EDM peer creates N sockets, and probes the one
ip:port of the EIM peer. The EIM peer creates a single socket, and
uses it to probe M random ports on the EDM NAT.

`./paradox.py --a-side-probes=256 --b-side-probes=256` shows that with
256 sockets on the EDM side and 256 random probes from the EIM side,
there's a 64% probability of a collision (meaning the peers can
communicate). This is slightly better than the 50% the straight
birthday paradox predicts, because we're looking for collisions
between two sets, rather than collisions within a single set.

## Hard birthday attack

In the hard case, both peers are behind an EDM NAT. The peers create N
and M sockets each, and probe NP, MP random ports on the other
NAT. Each probe results in a new mapping on their NAT, and in firewall
state that requires an exact match of both source and destination port
in order to pass traffic.

In other words, the peers probe `N*NP` and `M*MP` combinations of
`(wan_src_port, wan_remote_port)` each, which doubles the number of
bits in the search space from `2^16` in the easy case to `2^(16+16)`
in the hard case.

`./paradox.py --hard --a-side-probes=256 --b-side-probes=256` shows
that the same amount of packets results in a ~0% chance of
connectivity. You have to crank both sides to 65536 probes each
(e.g. 256 probes from each of 256 sockets, on both sides) to get back
to a 64% probability of communication.

## Algorithms

The formulas to compute the probability of traversal aren't
documented, because doing so would require writing a small explanatory
proof, and I can't be bothered to do the requisite TeX shuffling. It's
a small variant on the birthday paradox, so if you follow the proof of
that, and make the necessary tweaks to account for the fact that we're
hunting for a collision between two sets, rather than collisions
within one set, you'll arrive at the logic.

I've also left in the code that runs one iteration of the birthday
attack, as an attempt to illustrate what would happen in real network
code that runs it, and specifically what we're trying to find
collisions on in the easy and hard cases - which is also where the
huge escalation in difficulty comes from for the "hard" case.
