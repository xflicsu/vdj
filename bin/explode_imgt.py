#! /usr/bin/env python

import os
import argparse

import vdj
from pyutils import cleanup_id

argparser = argparse.ArgumentParser(description=None)
argparser.add_argument('input_file')
argparser.add_argument('output_dir',default=os.getcwd())
args = argparser.parse_args()

for chain in vdj.parse_imgt(args.input_file):
    output_file = os.path.join(args.output_dir,'%s.imgt' % cleanup_id(chain.id))
    with open(output_file,'w') as op:
        print >>op, chain
