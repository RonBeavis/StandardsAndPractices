#
# Copyright © 2019 Ronald C. Beavis
# Licensed under Apache License, Version 2.0, January 2004
#

# Creates a parent ion mass autocorrelation histogram from an X! Tandem XML file
# The autocorrelation value is calculated on the difference between the measured mass of
# a PSM and the mass of the unmodifed assigned peptide sequence

import xml.sax
import sys
import re
import os
import matplotlib.pyplot as plt
import matplotlib.style
import matplotlib as mpl
import math
import numpy

# simple XML handler class
class bioMLHandler(xml.sax.ContentHandler):
	def __init__(self):
		self.cTag = ''
		self.isDomain = False
		self.isAa = False
		self.mods = {}
		self.spectra = set()
		self.current = None
		self.domSum = 0.0
	# handles aa tags inside of a single domain		
	def startElement(self, tag, attrs):
		self.cTag = tag
		if tag == 'domain':
			self.current = int(re.sub('\..+','',attrs['id']))
			self.isDomain = True
			self.domSum = 0.0
		if tag == 'aa':
			self.domSum += float(attrs['modified'])
	# stores nominal mass difference in self.mods
	def endElement(self, tag):
		if tag == 'domain':
			mod = int(self.domSum + 0.5)
			if self.current not in self.spectra:
				if mod in self.mods:
					self.mods[mod] += 1
				else:
					self.mods[mod] = 1
				self.spectra.add(self.current)

	def get_mod_map(self):
		return self.mods

# creates an autocorrelation histogram from the information in _map (copied from bioMLHandler.mods)
def render_map(_map,_title,_file):
	xs = []
	ys = []
	xs.append([])
	ys.append([])
	#create x,y values
	min_map = min(_map)-10
	max_map = max(_map)+10
	for x in range(min_map,max_map):
		xs[0].append(x)
		if x in _map:
			ys[0].append(_map[x])
		else:
			ys[0].append(0)
	xs.append([])
	ys.append([])
	ymean = numpy.mean(ys[0])
	ydiv = 0
	for x in range(min_map,max_map):
		ydiv += (ys[0][x]-ymean)**2
	for a in range(-20,301):
		xs[1].append(a)
		ac = 0
		for x in range(min_map,max_map-a):
			ac += (ys[0][x]-ymean)*(ys[0][x+a]-ymean)
		ys[1].append(ac/ydiv)

	mpl.style.use('seaborn-notebook')
	#generate the bar histogram
	plt.bar(xs[1],ys[1],color=(1,0,0,1),linewidth=5)
	#alter plot parameters to create the desired view
#	plt.yscale('log')
#	plt.yscale('linear')
	plt.ylabel('autocorrelation (δM)')
	plt.xlabel('δM (Da)')
	plt.grid(True, lw = 1, ls = '--', c = '.90')
	plt.title(_title)
	fig = plt.gcf()
	fig.set_size_inches(10, 5)
	plt.gca().set_axisbelow(True)
	plt.gca().get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
	#store image in png file (requires an existing "png" directory)
	fig.savefig('png/%s_auto.png' % (_file), dpi=100, bbox_inches='tight')
	#display plot on screen
	plt.show()

#process command line
#try to load an XML file path
try:
	fpath = sys.argv[1]
#deal with errors
except:
	print('Usage: >mod_map.py INPUT_FILE (TITLE)')
	exit()
#check for a help-like request for information
if (fpath.find('-h') == 0 or fpath.find('?') < 4) and len(fpath) < 4:
	print('Usage: >mod_map.py INPUT_FILE (TITLE)')
	exit()
#deal with malformed XML file path name
if not os.path.isfile(fpath):
	print('File path "%s" does not exist.' % (fpath))
	print('Usage: >mod_map.py INPUT_FILE (TITLE)')
	exit()
#create default title
title = 'autocorrelation %s' % fpath
#try to get path from command line
try:
	title = sys.argv[2]
except:
	'autocorrelation %s' % fpath

#create the xml parser
parser = xml.sax.make_parser()
#attach the bioMLHandler class
parser.setContentHandler(bioMLHandler())
#associated the input XML file path and parse
parser.parse(open(fpath,"r"))
#retrieve the correlation information
mod_map = parser.getContentHandler().get_mod_map()
#plot the correlation information
render_map(mod_map,title,fpath)


