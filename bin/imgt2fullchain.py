#! /usr/bin/env python

import sys
import optparse

import vdj

parser = optparse.OptionParser()
(options, args) = parser.parse_args()

if len(args) == 2:
    inhandle = open(args[0],'r')
    outhandle = open(args[1],'w')
elif len(args) == 1:
    inhandle = open(args[0],'r')
    outhandle = sys.stdout
elif len(args) == 0:
    inhandle = sys.stdin
    outhandle = sys.stdout
else:
    raise Exception, "Wrong number of arguments."

for chain in vdj.parse_imgt(inhandle):
    try:
        full_chain = chain.full_chain
        print >>outhandle, ">%s\n%s" % (full_chain.id,full_chain.seq)
    except AttributeError:
        pass

