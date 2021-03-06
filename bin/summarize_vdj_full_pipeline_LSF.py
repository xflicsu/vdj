#! /usr/bin/env python

import os
import sys
import glob
import optparse

import seqtools
import subprocess

join = os.path.join

option_parser = optparse.OptionParser()
# option_parser.add_option('-x','--xxx',dest='xxxx',type='int')
(options,args) = option_parser.parse_args()

if len(args) != 1:
    raise ValueError, "Require a single input jobfile"

jobfile = args[0]

# PARAMETER DEFINITION

# process jobfile for input parameters
# defines the following variables:
    # basename               # unique base identifier for data
    # vdj_package_dir        # directory to find scripts.  will be added to shell PATH
    # input_fasta            # the initial fasta data
    # barcode_fasta          # barcode identifiers
    # isotype_fasta          # isotype identifiers
    # analysis_dir           # full path; base directory for final products
    # work_dir               # full path; base directory for intermediate parts and logs
    # min_size               # min size selection
    # max_size               # max size selection
    # packet_size            # packet size for alignment jobs
    # loci                   # the loci to use for VDJ aln
    # raw_vdjxml             # derived file stored in analysis_dir
    # aligned_file           # derived file stored in analysis_dir
    # vj_filtered_file       # derived file stored in analysis_dir
    # size_selected_file     # derived file stored in analysis_dir
    # clustered_file         # derived file stored in analysis_dir
    # parts_dir              # derived intermediate work directories (rel. to work_dir)
    # log_dir                # derived intermediate work directories (rel. to work_dir)
    # partition_dir          # derived intermediate work directories (rel. to work_dir)

execfile(jobfile)

print '%s\n' % basename

num_fasta = 0
ip = open(input_fasta,'r')
for seq in seqtools.FastaIterator(ip):
    num_fasta += 1
ip.close()
print 'Number of raw reads:\n\t%s\n' % num_fasta

num_size_selected = 0
ip = open(join(analysis_dir,size_selected_file),'r')
for line in ip:
    if "<ImmuneChain>" in line:
        num_size_selected += 1
ip.close()
print 'Number of reads in size range(%d-%d):\n\t%s\n' % (min_size,max_size,num_size_selected)

print 'Barcoding, coding strand, isotype ID, VDJ alignment split into packets of %d reads.\n' % packet_size
p = subprocess.Popen('cat %s | grep CPU' % join(work_dir,log_dir,'alignment*log*'),shell=True,stdout=subprocess.PIPE)
cpu_times = []
for line in p.stdout:
    cpu_times.append(float(line.split()[3]))
print '\tAverage CPU time:\n\t\t%f s' % (sum(cpu_times)/len(cpu_times))
cpu_times.sort()
print '\tShortest CPU times:\n\t\t%f s\n\t\t%f s\n\t\t%f s' % tuple(cpu_times[:3])
print '\tLongest CPU times:\n\t\t%f s\n\t\t%f s\n\t\t%f s\n' % tuple(cpu_times[-3:])

num_revcomp = 0
num_barcode = 0
barcode_counts = {}
ip = open(join(analysis_dir,aligned_file),'r')
for line in ip:
    if 'revcomp' in line:
        num_revcomp += 1
    elif '<barcode>' in line:
        num_barcode += 1
        bc = line.strip().lstrip('<barcode>').rstrip('</barcode>')
        barcode_counts[bc] = barcode_counts.get(bc,0) + 1
ip.close()
print 'Number of chains that were reverse-complemented:\n\t%d\n' % num_revcomp
print 'Number of chains with barcode:\n\t%d\n' % num_barcode
print 'Barcode breakdown:'
for (bc,count) in barcode_counts.iteritems():
    print '\t%-10s %10d %10.1f%%' % (bc,count,float(count)/num_barcode*100.)

num_vj_filtered = 0
ip = open(join(analysis_dir,vj_filtered_file),'r')
for line in ip:
    if '<ImmuneChain>' in line:
        num_vj_filtered += 1
ip.close()
print '\nNumber of chains after filtering for VJ alignment:\n\t%d\n' % num_vj_filtered

num_barcode = 0
barcode_counts = {}
ip = open(join(analysis_dir,vj_filtered_file),'r')
for line in ip:
    if '<barcode>' in line:
        num_barcode += 1
        bc = line.strip().lstrip('<barcode>').rstrip('</barcode>')
        barcode_counts[bc] = barcode_counts.get(bc,0) + 1
ip.close()
print 'Barcode breakdown in VJ filtered set:'
for (bc,count) in barcode_counts.iteritems():
    print '\t%-10s %10d %10.1f%%' % (bc,count,float(count)/num_barcode*100.)

partitions = glob.glob(join(work_dir,partition_dir,'*.clustered.vdjxml'))
num_partitions = len(partitions)
print "\nClustering split into %d partitions.\n" % num_partitions

p = subprocess.Popen('cat %s | grep CPU' % join(work_dir,log_dir,'clustering*log*'),shell=True,stdout=subprocess.PIPE)
cpu_times = []
for line in p.stdout:
    cpu_times.append(float(line.split()[3]))
print '\tAverage CPU time:\n\t\t%f s' % (sum(cpu_times)/len(cpu_times))
cpu_times.sort()
print '\tShortest CPU times:\n\t\t%f s\n\t\t%f s\n\t\t%f s' % tuple(cpu_times[:3])
print '\tLongest CPU times:\n\t\t%f s\n\t\t%f s\n\t\t%f s\n' % tuple(cpu_times[-3:])

partition_sizes = []
for partition in partitions:
    num_chains_partition = 0
    ip = open(partition,'r')
    for line in ip:
        if '<ImmuneChain>' in line:
            num_chains_partition += 1
    ip.close()
    partition_sizes.append(num_chains_partition)
partition_sizes.sort()
print 'Largest partition sizes:\n\t%d\n\t%d\n\t%d\n' % tuple(partition_sizes[-3:])

uniq_clones = set()
uniq_junctions = set()
ip = open(join(analysis_dir,clustered_file),'r')
for line in ip:
    if '<clone>' in line:
        uniq_clones.add( line.strip().lstrip('<clone>').rstrip('</clone>') )
    elif '<junction>' in line:
        uniq_junctions.add( line.strip().lstrip('<junction>').rstrip('</junction>') )
ip.close()
print 'Number of unique clones:\n\t%d\n' % len(uniq_clones)
print 'Number of unique junctions:\n\t%d' % len(uniq_junctions)
