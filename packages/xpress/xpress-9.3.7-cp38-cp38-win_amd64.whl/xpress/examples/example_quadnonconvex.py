# Test problem on a dot product between matrices of scalars and/or of
# variables. Note that the problem cannot be solved by the Optimizer
# as it is nonconvex.
#
# (C) Fair Isaac Corp., 1983-2025

from __future__ import print_function

import xpress as xp
import numpy as np

a = 0.1 + np.arange(21).reshape(3, 7)

# Create NumPy vectors of variables
y = xp.vars(3, 7, name='')
x = xp.vars(7, 5, name='')

p = xp.problem()
p.addVariable(x, y)

p.addConstraint(xp.Dot(y, x) <= 0)
p.addConstraint(xp.Dot(a, x) == 1)

p.setObjective(x[0][0])

# By default the problem is solved to global optimality.
# Setting the nlpsolver control to one ensures the problem is
# solved the local nonlinear solver.
p.controls.nlpsolver = 1

p.optimize()
