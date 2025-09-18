# Solve an instance of the TSP with Xpress using callbacks
#
# (C) Fair Isaac Corp., 1983-2025

# Retrieve an example from
#
# http://www.math.uwaterloo.ca/tsp/world/countries.html
#
# and load the TSP instance, then solve it using the Xpress Optimizer
# library with the appropriate callback. Once the optimization is over
# (i.e. the time limit is reached or we find an optimal solution) the
# optimal tour is displayed using matplotlib.

import networkx as nx
import xpress as xp
import re
import math
import sys

from matplotlib import pyplot as plt

if sys.version_info >= (3,):    # Import with Python 3
    import urllib.request as ul
else:                           # Use Python 2
    import urllib as ul

#
# Download instance from TSPLib
#
# Replace with any of the following for a different instance:
#
# ar9152.tsp   (9125 nodes)
# bm33708.tsp (33708 nodes)
# ch71009.tsp (71009 nodes)
# dj38.tsp       (38 nodes)
# eg7146.tsp   (7146 nodes)
# fi10639.tsp (10639 nodes)
# gr9882.tsp   (9882 nodes)
# ho14473.tsp (14473 nodes)
# ei8246.tsp   (8246 nodes)
# ja9847.tsp   (9847 nodes)
# kz9976.tsp   (9976 nodes)
# lu980.tsp     (980 nodes)
# mo14185.tsp (14185 nodes)
# nu3496.tsp   (3496 nodes)
# mu1979.tsp   (1979 nodes)
# pm8079.tsp   (8079 nodes)
# qa194.tsp     (194 nodes)
# rw1621.tsp   (1621 nodes)
# sw24978.tsp (24978 nodes)
# tz6117.tsp   (6117 nodes)
# uy734.tsp     (734 nodes)
# vm22775.tsp (22775 nodes)
# wi29.tsp       (29 nodes)
# ym7663.tsp   (7663 nodes)
# zi929.tsp     (929 nodes)
# ca4663.tsp   (4663 nodes)
# it16862.tsp (16862 nodes)
#

filename = 'wi29.tsp'

ul.urlretrieve('https://www.math.uwaterloo.ca/tsp/world/' + filename, filename)

# Read file consisting of lines of the form "k: x y" where k is the
# point's index while x and y are the coordinates of the point. The
# distances are assumed to be Euclidean.

instance = open(filename, 'r')
coord_section = False
points = {}

G = nx.Graph()

#
# Coordinates of the points in the graph
#

for line in instance.readlines():

    if re.match('NODE_COORD_SECTION.*', line):
        coord_section = True
        continue
    elif re.match('EOF.*', line):
        break

    if coord_section:
        coord = line.split(' ')
        index = int(coord[0])
        cx = float(coord[1])
        cy = float(coord[2])
        points[index] = (cx, cy)
        G.add_node(index, pos=(cx, cy))

instance.close()

print("Downloaded instance, created graph.")

# Callback for checking if the solution forms a tour
#
# Returns a tuple (a,b) with
#
# a: True if the solution is to be rejected, False otherwise
# b: real cutoff value


def check_tour(prob, G, isheuristic, cutoff):
    """
    Use this function to refuse a solution unless it forms a tour
    """

    # Obtain solution, then start at node 1 to see if the solutions at
    # one form a tour. The vector s is binary as this is a preintsol()
    # callback.

    s = []

    prob.getlpsol(s, None, None, None)

    orignode = 1
    nextnode = 1
    card = 0

    while nextnode != orignode or card == 0:

        # forward star
        FS = [j for j in V if j != nextnode and
              abs (s[prob.getIndex(x[nextnode, j])] - 1.0) <= prob.controls.miptol]
        card += 1

        if len(FS) < 1:
            # reject solution if we can't close the loop
            return (True, None)

        nextnode = FS[0]

    # If there are n arcs in the loop, the solution is feasible

    # To accept the cutoff, return second element of tuple as None
    return (card < n, None)


#
# Callback for adding subtour elimination constraints
#
# Return nonzero if the node is infeasible, 0 otherwise
#

def eliminate_subtour(prob, G):
    """
    Function to insert subtour elimination constraints
    """

    # Only add cuts at nodes that are integer feasible
    if prob.attributes.mipinfeas:
        return

    # Initialize s to an empty list to provide it as an output
    # parameter
    s = []

    prob.getlpsol(s, None, None, None)

    # Starting from node 1, gather all connected nodes of a loop in
    # set M. if M == V, then the solution is valid if integer,
    # otherwise add a subtour elimination constraint

    orignode = 1
    nextnode = 1

    connset = []

    while nextnode != orignode or len(connset) == 0:

        connset.append(nextnode)

        # forward star
        FS = [j for j in V if j != nextnode and
              abs(s[prob.getIndex(x[nextnode, j])] - 1.0) <= prob.controls.miptol]
        if len(FS) < 1:
            return 0

        nextnode = FS[0]

    if len(connset) < n:

        # Add a subtour elimination using the nodes in connset (or, if card
        # (connset) > n/2, its complement)

        if len(connset) <= n/2:
            columns = [x[i, j] for i in connset
                       for j in connset if i != j]
            nArcs = len(connset)
        else:
            columns = [x[i, j] for i in V for j in V
                       if i not in connset and
                       j not in connset and i != j]
            nArcs = n - len(connset)

        # Presolve cut in order to add it to the presolved problem
        colind, rowcoef = [], []
        drhsp, status = prob.presolverow(rowtype='L',
                                         origcolind=columns,
                                         origrowcoef=[1] * len(columns),
                                         origrhs=nArcs - 1,
                                         maxcoefs=prob.attributes.cols,
                                         colind=colind, rowcoef=rowcoef)
        # Since mipdualreductions=0, presolving the cut must succeed, and the cut should
        # never be relaxed as this would imply that it did not cut off a subtour.
        assert status == 0

        prob.addcuts(cuttype=[1],
                     rowtype=['L'],
                     rhs=[drhsp],
                     start=[0, len(colind)],
                     colind=colind,
                     cutcoef=rowcoef)

    return 0  # return nonzero for infeasible


#
# Formulate problem, set callback function and solve
#

n = len(points)    # number of nodes
V = range(1, n+1)  # set of nodes

# Set of arcs (i.e. all pairs since it is a complete graph)
A = [(i, j) for i in V for j in V if i != j]

x = {(i, j): xp.var(name='x_{0}_{1}'.format(i, j),
                    vartype=xp.binary) for (i, j) in A}

conservation_in = [xp.Sum(x[i, j] for j in V if j != i) == 1 for i in V]
conservation_out = [xp.Sum(x[j, i] for j in V if j != i) == 1 for i in V]

p = xp.problem()

p.addVariable(x)
p.addConstraint(conservation_in, conservation_out)

xind = {(i, j): p.getIndex(x[i, j]) for (i, j) in x.keys()}

# Objective function: total distance travelled
p.setObjective(xp.Sum(math.sqrt((points[i][0] - points[j][0])**2 +
                                (points[i][1] - points[j][1])**2) * x[i, j]
                      for (i, j) in A))

# The negative is for "stop even if no solution is found"
p.controls.timelimit = 200

p.addcboptnode(eliminate_subtour, G, 1)
p.addcbpreintsol(check_tour, G, 1)

# Disable dual reductions (in order not to cut optimal solutions)
# and nonlinear reductions, in order to be able to presolve the
# cuts.
p.controls.mipdualreductions = 0

p.optimize()

if p.attributes.solstatus not in [xp.SolStatus.OPTIMAL, xp.SolStatus.FEASIBLE]:
    print("Solve status:", p.attributes.solvestatus.name)
    print("Solution status:", p.attributes.solstatus.name)
else:
    # Read solution and store it in the graph
    sol = p.getSolution()
    try:
        for (i, j) in A:
            if sol[p.getIndex(x[i, j])] > 0.5:
                G.add_edge(i, j)

        # Display best tour found
        pos = nx.get_node_attributes(G, 'pos')

        nx.draw(G, points)  # create a graph with the tour
        plt.show()          # display it interactively
    except:
        print('Could not draw solution')
