#! /usr/bin/env python

import sys
import optparse

import vdj

parser = optparse.OptionParser()
parser.add_option('-b','--barcodes',dest='barcodes_fasta')
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

vdj.barcode_id(options.barcodes_fasta,inhandle,outhandle)
