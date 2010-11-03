#! /usr/bin/env python

import optparse

import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.collections

import vdj
import vdj.analysis

option_parser = optparse.OptionParser()
option_parser.add_option('-t','--times')
option_parser.add_option('-q','--quantify',choices=['clone','junction','v','j'])
option_parser.add_option('-r','--threshold',type='float')
(options,args) = option_parser.parse_args()

if len(args) == 1:
    inhandle = open(args[0],'r')
else:
    raise ValueError, "Must give a single argument to vdjxml file"

# determine mapping between barcodes and times
timedict = {}
ip = open(options.times,'r')
for line in ip:
    timedict[line.split()[0]] = float(line.split()[1])
ip.close()

features = [options.quantify,'barcode']
(uniq_feature_values,countdict) = vdj.analysis.vdjxml2countdict(inhandle,features)
times = np.array([timedict[bc] for bc in uniq_feature_values['barcode']])
timesort = np.argsort(times)
times = times[timesort]
countmatrix = vdj.analysis.countdict2matrix(features,uniq_feature_values,countdict)
countmatrix = countmatrix[:,timesort]  # sort in increasing times
freqmatrix = np.float_(countmatrix) / countmatrix.sum(axis=0)

# define which idxs to plot
if options.threshold:
    idxs = np.sum(freqmatrix>=options.threshold,axis=1)>0 # breaks threshold at least once
else:
    idxs = [True]*freqmatrix.shape[0]
# idxs = np.sum(time_series_freqs>0,axis=1)>2 # seen at least twice
# idxs_bool = np.logical_and(idxs_bool_1,idxs_bool_2)
# idxs_bool = np.array([False]*len(reference_clones))
print "Number of lines plotted: %i" % np.sum(idxs)

# make the plots
outbasename = '.'.join(args[0].split('.')[:-1])

random_color = lambda: '#%02x%02x%02x' % tuple(np.random.randint(0,256,3))

segments = [zip(times,freqs) for freqs in freqmatrix[idxs]]
colors = [random_color() for i in xrange(len(segments))]
lines = mpl.collections.LineCollection(segments,colors=colors,linewidths=0.5)
lines.set_alpha(0.75)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.add_collection(lines)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_position(('outward',5))
ax.spines['left'].set_position(('outward',5))
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(times))
ax.set_xlim([times.min(),times.max()])
ax.autoscale_view(scalex=False,scaley=True)
# ax.set_yscale('log')
ax.set_xlabel('time')
ax.set_ylabel(options.quantify+' frequency')
# fig.show()
fig.savefig(outbasename+'.%stimeseries.png' % options.quantify)
fig.savefig(outbasename+'.%stimeseries.pdf' % options.quantify)

# # only stuff that's positive everywhere
segments = [np.asarray(zip(times,freqs)) for freqs in freqmatrix[idxs]]
segments = [segment[segment[:,1]>0] for segment in segments if segment[:,1].sum()>0]
lines = mpl.collections.LineCollection(segments,colors=colors,linewidths=0.5)
lines.set_alpha(0.75)

figlog = plt.figure()
ax = figlog.add_subplot(111)
ax.add_collection(lines)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_position(('outward',5))
ax.spines['left'].set_position(('outward',5))
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(times))
ax.set_yscale('log')
ax.set_xlim([times.min(),times.max()])
ax.set_xlabel('time')
ax.set_ylabel(options.quantify+' frequency')
# fig.show()
figlog.savefig(outbasename+'.%stimeseries.log.png' % options.quantify)
figlog.savefig(outbasename+'.%stimeseries.log.pdf' % options.quantify)