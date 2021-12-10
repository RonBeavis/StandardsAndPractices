import cgi,cgitb
import os
#os.environ has to be set so that matplotlib will function
os.environ[ 'HOME' ] = 'c:/temp'

import sys
import requests
import re
import json
import random
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style
import matplotlib as mpl

cgitb.enable()

def error(_x,_y):
	dx = np.sqrt(_x)
	dy = np.sqrt(_y)
	return np.sqrt((dx/_x)**2 + (dy/_y)**2 - 2*(dx/_x)*(dy/_y))
#
# get peptide PSMs for protein _l
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
# get protein _l sequence
#

def get_protein(_l):
	url = 'http://gpmdb.thegpm.org/1/protein/sequence/acc=%s' % (_l)
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
# get protein _l description
#
def get_description(_l):
	url = 'http://gpmdb.thegpm.org/1/protein/description/acc=%s' % (_l)
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
# test deamidated residue for sequence motifs
#
def test_pos(_res,_protein):
	if _protein[_res+1] == 'G':
		return 50
	if _protein[_res+1] == 'A':
		return 25
	if _protein[_res-1] == 'K' or _protein[_res-1] == 'R':
		return 20
	if _protein[_res-1] == 'N' or _protein[_res+1] == 'N':
		return 20
	if _protein[_res-1] == 'Q' or _protein[_res+1] == 'Q':
		return 20
	return 15

def make_ptm_csv(_l,_plength,_title,_protein,_xs,_ys,_legend,_cl):
	use_ylim = False
	notes_min = 5
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
	xs = {'N-deamidation':[],'N':[]}
	ys = {'N-deamidation':[],'N':[]}
	min_obs = 2
	#create x,y arrays for plot
	for a in range(1,_plength+1):
		b = str(a)
		if(b in values['deamidation']):
			if values['deamidation'][b] >= min_obs and a < len(seq) - 2:
				if seq[a-1] == 'N' and (seq[a+1] == 'S' or seq[a+1] == 'T') and seq[a] != 'P':
					xs['N-deamidation'].append(a)
					ys['N-deamidation'].append(values['deamidation'][b]) 
			elif seq[a-1] == 'N' and _ys[a-1] > 0:
				xs['N'].append(a)
				ys['N'].append(0)
	notes = []
	tsv = {}
	isv = {}
	for i,y in enumerate(ys['N-deamidation']):
		yst = ys['N-deamidation'][i]
		ystm = _ys[xs['N-deamidation'][i]-1]
		try:
			ys['N-deamidation'][i] /= _ys[xs['N-deamidation'][i]-1]/100.0
		except:
			notes.append('exception')
			continue
		if ys['N-deamidation'][i] >= 100.0:
			ys['N-deamidation'][i] = 99.0
		s = xs['N-deamidation'][i]
		if s - 2 < 0:
			p = '[' + _protein[s-1] + _protein[s].lower()
		elif s > len(_protein) - 1:
			p = _protein[s-2].lower() + _protein[s-1] + ']'
		else:
			p = _protein[s-2].lower() + _protein[s-1] + _protein[s].lower() + _protein[s+1].lower()
		tsv[xs['N-deamidation'][i]] = '%i\t%s\t%.2f\t%i\t%i\t%.2f' % (xs['N-deamidation'][i],p,ys['N-deamidation'][i],yst,ystm,error(yst,ystm))
		isv[xs['N-deamidation'][i]] = ys['N-deamidation'][i]
		if s - 2 < 0:
			notes.append(('%sN%i%s'%('[',xs['N-deamidation'][i],_protein[s].lower()+_protein[s+1].lower()),xs['N-deamidation'][i],ys['N-deamidation'][i]))
		elif s > len(_protein) - 1:
			notes.append(('%sN%i%s'%(_protein[s-2].lower(),xs['N-deamidation'][i],']'),xs['N-deamidation'][i],ys['N-deamidation'][i]))
		else:
			notes.append(('%sN%i%s'%(_protein[s-2].lower(),xs['N-deamidation'][i],_protein[s].lower()+_protein[s+1].lower()),xs['N-deamidation'][i],ys['N-deamidation'][i]))
#	mpl.style.use('seaborn-notebook')
	plt.xkcd()
	plt.rcParams.update({'font.size': 10})
	plt.xlim(0,int(1.02*_plength))
	max_occ = 0
	if len(ys['N-deamidation']) > 0:
		max_occ = max(ys['N-deamidation'])
		

	ms = 10
	tlist = ys['N-deamidation'] + ys['N']
	ave = 0.0
	if len(tlist) > 0:
		thelist = []
		for t in tlist:
			if t > 2.0:
				continue
			thelist.append(t)
		if len(thelist):
			ave = sum(thelist)/len(thelist)
	#load all x,y information into a plot
	xsf = []
	ysf = []
	ns = []
	nlim = 40
	for i,f in enumerate(xs['N-deamidation']):
		lim = test_pos(f-1,protein)
		try:
			print(i,f,notes[i],ys['N-deamidation'][i],_ys[f-1],_ys[f-1] > nlim)
		except:
			print(i)
		if ys['N-deamidation'][i] >= lim and _ys[f-1] > nlim:
			ysf.append(ys['N-deamidation'][i])
			xsf.append(f)
			ns.append(notes[i])
	notes = ns
	plt.plot(xsf,ysf,markersize=ms,color=(0.05,.05,.9,.8),marker='s',linestyle='None',label='N-linked')
	#set up the required graph
	plt.legend(loc=_legend)
	plt.yscale('linear')
	plt.ylabel('AI-ND score')
	plt.xlabel('residue')
	plt.grid(True, lw = 1, ls = '--', c = '.8')
	plt.title(_title)
	ax = plt.gca()
	xoff = 0.015 * len(protein)
	for n in notes:
		ax.annotate(n[0], (n[1]+xoff, n[2]))
	box = ax.get_position()
	ax.set_ylim([0,100])
	ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])

	ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

	if len(xsf) == 0:
		plt.ylim(0,105.0)
	elif use_ylim and max_occ < 9.5:
		plt.ylim(0,10.1)
	else:
		plt.ylim(0,105.0)

	fig = plt.gcf()
	fig.set_size_inches(10, 5)
	plt.gca().get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
	#store graph in png file
	desc = re.sub(r' \[',r'<br />[&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;',get_description(_l))
	desc = re.sub(r'[\[\]]',r'',desc)
	if len(xsf) == 0:
		print('No N-linked glycosylation sites detected for "%s".' % (_l))
		return
	fig.savefig('png/%s_nlink.png' % (_cl), dpi=100, bbox_inches='tight')
	plt.show()
	return
	
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
		print('deamidation_png.py PROTEIN_ACC TITLE FILE')
		print('LEGEND: "upper right"|"upper left"|"best"')
		exit()
label = sys.argv[1]
try:
	cl = sys.argv[3]
except:
	cl = None
title = ''
try:
	title = sys.argv[2]
except:
	title = sys.argv[1]

y_axis = None

legend = 'upper left'

protein = get_protein(label)

ls = get_peptides(label)
(xs,ys) = get_residues(len(protein),ls)

make_ptm_csv(label,len(protein),title,protein,xs,ys,legend,cl)

