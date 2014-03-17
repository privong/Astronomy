#!/usr/bin/env python
#
# abs_err cont cont_err abs abs_err
#
# Takes inputs of fluxes in the same units and computes the error in the measured opacity

import math
import sys

cont=float(sys.argv[1])
cerr=float(sys.argv[2])
abs=float(sys.argv[3])
aerr=float(sys.argv[4])

tau=-1*math.log(1.-abs/cont)
#terrsq=(1/(1-abs/cont))**2*(aerr**2/cont+(cerr**2*abs)/cont**2)
terrsq=(1/(1-abs/cont))**2*((aerr/cont)**2+abs**2*cerr**2/cont**4)

print "tau: {0:.4f}".format(tau)
print "delta tau: {0:.4f}".format(math.sqrt(terrsq))


