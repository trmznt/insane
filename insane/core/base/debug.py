

debug_level = 10

INFO = 10
ALL = 100

from inspect import *
import sys, time
from seqpy import cerr, cout

def D( level, text ):
    cf = getouterframes( currentframe() )[ 1 ]
    #print cf
    #infos = getframeinfo( cf )
    if level >= debug_level:
        cerr("[%s] %s [%s:%s]:: %s " % (time.strftime('%H:%M:%S'),
                cf[3], cf[1], cf[2],  text))

