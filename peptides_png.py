#
# Copyright © 2019 Ronald C. Beavis
# Licensed under Apache License, Version 2.0, January 2004
#

# Creates a histogram of the frequency of protein residue observation
# Information is obtained from GPMDB services and converted into a
# line plot

import sys
import requests
import re
import json
import os
import matplotlib.pyplot as plt
import matplotlib.style
import matplotlib as mpl

#obtain the frequency of peptide observation for the protein identified by _l
def get_peptides(_l):
	#create the appropriate URL
	url = 'https://gpmdb.thegpm.org/protein/model/%s&excel=1' % (_l)
	session = requests.session()
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	#clean up line end characters
	text = re.sub('\r\n','\n',r.text)
	#return information in csv lines
	return text.splitlines()

#obtain the protein sequence for the protein identified by _l
def get_protein(_l):
	#create appropriate URL
	url = 'http://rest.thegpm.org/1/protein/sequence/acc=%s' % (_l)
	session = requests.session()
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	#parse the JSON return value
	try:
		values = json.loads(r.text)
	except:
		return None
	#return protein sequence
	return values[0]

# generate a frequency histogram and plot the values
def make_peptide_png(_l,_plength,_lines,_title,_file):
	start = {}
	end = {}
	res = {}
	max = 0
	#interpret the csv info from get_peptides
	for line in _lines[1:]:
		vs = line.split('\t')
		vs[0] = int(vs[0])
		vs[1] = int(vs[1])
		vs[2] = int(vs[2])
		if vs[0] in start:
			start[vs[0]] = start[vs[0]] + vs[2]
		else:
			start[vs[0]] = vs[2]
		if vs[1] in end:
			end[vs[1]] = end[vs[1]] + vs[2]
		else:
			end[vs[1]] = vs[2]
		if vs[1] > max:
			max = vs[1]
		for a in range(vs[0],vs[1]+1):
			if a in res:
				res[a] = res[a] + vs[2]
			else:
				res[a] = vs[2]

	max = _plength
	max_res = 0
	for a in res:
		if res[a] > max_res:
			max_res = res[a]
	a = 1
	xs = []
	ys = []
	#create the x,y arrays to plot
	for a in range(1,max+1):
		xs.append(a)
		if a in res:
			ys.append(res[a])
		else:
			ys.append(0)

	mpl.style.use('seaborn-notebook')
	plt.xlim(0,int(1.02*_plength))
	ms = 10
	#load x,y information into a plot
	plt.plot(xs,ys,color=(0.25,0,.75,.8),marker='',linestyle='solid',linewidth=1)
	#set up the required graph
#	plt.yscale('log')
	plt.ylabel('observations')
	plt.xlabel('residue')
	plt.grid(True, lw = 1, ls = '--', c = '.9')
	plt.title(_title)
	fig = plt.gcf()
	fig.set_size_inches(10, 5)
	cl = re.sub('\|','_',_file)
	plt.gca().get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
	plt.gca().get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
	#store graph in png file
	fig.savefig('png/%s_peps.png' % (cl), dpi=100, bbox_inches='tight')
	#display graph on screen
	plt.show()
	return 1

#deal with command line arguments	
if len(sys.argv) < 2:
		print('peptides_png.py PROTEIN_ACC TITLE (FILENAME)')
		exit()
label = sys.argv[1]
title = ''
try:
	title = sys.argv[2]
except:
	title = label
filename = sys.argv[1]
try:
	filename = sys.argv[3]
except:
	filename = sys.argv[1]

print('Request protein sequence ...')
protein = get_protein(label)
print('Request peptide information ...')
ls = get_peptides(label)
print('Create peptide plot ...')
make_peptide_png(label,len(protein),ls,title,filename)


