#!/usr/bin/env python
#
# abs_err cont cont_err abso abs_err
#
# Compute optical depth and its error, using an input absorption measurement
# and continuum measurement. All (integrated) fluxes must be in the same units.

import math
import sys


cont = float(sys.argv[1])
cerr = float(sys.argv[2])
abso = float(sys.argv[3])
aerr = float(sys.argv[4])

tau = -1*math.log(1.-abso/cont)
# terrsq = (1/(1-abso/cont))**2*(aerr**2/cont+(cerr**2*abso)/cont**2)
terrsq = (1/(1-abso/cont))**2*((aerr/cont)**2+abso**2*cerr**2/cont**4)

print("tau: {0:.4f}".format(tau))
print("delta tau: {0:.4f}".format(math.sqrt(terrsq)))
