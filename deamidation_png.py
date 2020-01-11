#
# Copyright © 2019 Ronald C. Beavis
# Licensed under Apache License, Version 2.0, January 2004
#
#
# Creates a histogram of the occupancy of Q/N deamidation observation
#
# Information is obtained from GPMDB services and converted into a
# scatter plot
#

import sys
import requests
import re
import json
import os
import matplotlib.pyplot as plt
import matplotlib.style
import matplotlib as mpl

#
# obtain a TSV formatted list of peptides
#

def get_peptides(_l):
	url = 'https://gpmdb.thegpm.org/protein/model/%s&excel=1' % (_l)
	session = requests.session()
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None

	text = re.sub('\r\n','\n',r.text)
	return text.splitlines()

#
#obtain the protein sequence for the protein identified by _l
#

def get_protein(_l):
	url = 'http://rest.thegpm.org/1/protein/sequence/acc=%s' % (_l)
	session = requests.session()
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	try:
		values = json.loads(r.text)
	except:
		return None
	return values[0]

#
# generate a frequency histogram and plot the values
#

def make_ptm_csv(_l,_plength,_title,_protein,_xs,_ys):
	session = requests.session()
	seq = list(_protein)
	values = {'deamidation':None}
	#formulate a URL to request information about NQ-deamidation for the protein identified by _l
	url = 'http://gpmdb.thegpm.org/1/peptide/nq/acc=%s&pos=1-%i&w=n' % (_l,_plength)
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	try:
		values['deamidation'] = json.loads(r.text)
	except:
		return None
	a = 1;
	#xs and ys contain the x,y arrays for the scatter plots
	xs = {'N-deamidation':[],'Q-deamidation':[],'N':[],'Q':[]}
	ys = {'N-deamidation':[],'Q-deamidation':[],'N':[],'Q':[]}
	min_obs = 5
	#create x,y arrays for plot
	for a in range(1,_plength+1):
		b = str(a)
		if(b in values['deamidation']):
			if values['deamidation'][b] >= min_obs:
				if seq[a-1] == 'Q':
					xs['Q-deamidation'].append(a)
					ys['Q-deamidation'].append(values['deamidation'][b])
				if seq[a-1] == 'N':
					xs['N-deamidation'].append(a)
					ys['N-deamidation'].append(values['deamidation'][b]) 
			elif seq[a-1] == 'Q' and _ys[a-1] > 0:
				xs['Q'].append(a)
				ys['Q'].append(0)
			elif seq[a-1] == 'N' and _ys[a-1] > 0:
				xs['N'].append(a)
				ys['N'].append(0)
	notes = []
	tsv = {}
	for i,y in enumerate(ys['N-deamidation']):
		ys['N-deamidation'][i] /= _ys[xs['N-deamidation'][i]]/100.0
		tsv[xs['N-deamidation'][i]] = '%i\t%s\t%.1f' % (xs['N-deamidation'][i],'N',ys['N-deamidation'][i])
		if ys['N-deamidation'][i] >= 2:
			notes.append(('N%i'%(xs['N-deamidation'][i]),xs['N-deamidation'][i],ys['N-deamidation'][i]))
	for i,y in enumerate(ys['Q-deamidation']):
		ys['Q-deamidation'][i] /= _ys[xs['Q-deamidation'][i]]/100.0
		tsv[xs['Q-deamidation'][i]] = '%i\t%s\t%.1f' % (xs['Q-deamidation'][i],'Q',ys['Q-deamidation'][i])
		if ys['Q-deamidation'][i] >= 2:
			notes.append(('Q%i'%(xs['Q-deamidation'][i]),xs['Q-deamidation'][i],ys['Q-deamidation'][i]))
	print('Residue\tAA\tOccupancy (%)')
	for i in sorted(tsv):
		print('%s' % (tsv[i]))
	mpl.style.use('seaborn-notebook')
	plt.xlim(0,int(1.02*_plength))
	ms = 10
	#load all x,y information into a plot
	plt.plot(xs['N-deamidation'],ys['N-deamidation'],markersize=ms,color=(1,.0,.0,.8),marker='o',linestyle='None',label='N-deam')
	plt.plot(xs['Q-deamidation'],ys['Q-deamidation'],markersize=ms,color=(.0,.0,1,.8),marker='o',linestyle='None',label='Q-deam')
	plt.plot(xs['N'],ys['N'],markersize=ms,color=(1,.0,.0,.8),marker='.',linestyle='None',label='N')
	plt.plot(xs['Q'],ys['Q'],markersize=ms,color=(.0,.0,1,.8),marker='.',linestyle='None',label='Q')
	#set up the required graph
	plt.yscale('linear')
	plt.ylabel('% of observations')
	plt.xlabel('residue')
	plt.legend(loc='best')
	plt.grid(True, lw = 1, ls = '--', c = '.8')
	plt.title(_title)
	ax = plt.gca()
	xoff = 0.01 * len(protein)
	for n in notes:
		ax.annotate(n[0], (n[1]+xoff, n[2]))
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])
#	ax.set_ylim([0,400])
	ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
	fig = plt.gcf()
	fig.set_size_inches(10, 5)
	plt.gca().get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
	#store graph in png file
#	fig.savefig('png/%s_ptms.png' % (cl), dpi=100, bbox_inches='tight')
	#display graph on screen
	plt.show()
	return 1
#
# retrieve the number of times each residue has been observed
#

def get_residues(_plength,_lines):
	start = {}
	end = {}
	res = {}
	max = 0
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
	for a in range(1,max+1):
		xs.append(a)
		if a in res:
			ys.append(res[a])
		else:
			ys.append(0)
	return (xs,ys)

#deal with command line arguments	
if len(sys.argv) < 2:
		print('deamidation_png.py PROTEIN_ACC TITLE')
		exit()
label = sys.argv[1]
title = ''
try:
	title = sys.argv[2]
except:
	title = sys.argv[1]

y_axis = None

protein = get_protein(label)

ls = get_peptides(label)
(xs,ys) = get_residues(len(protein),ls)

make_ptm_csv(label,len(protein),title,protein,xs,ys)

