import sys
import requests
import re
import json
import os
import matplotlib.pyplot as plt
import matplotlib.style
import matplotlib as mpl

def get_peptides(_l,_t):
	url = 'https://gpmdb.thegpm.org/protein/model/%s&excel=1' % (_l)
	session = requests.session()
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None

	text = re.sub('\r\n','\n',r.text)
	return text.splitlines()

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


def make_peptide_png(_l,_plength,_lines,_title):
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
		a = vs[0]
		while a <= vs[1]:
			if a in res:
				res[a] = res[a] + vs[2]
			else:
				res[a] = vs[2]
			a += 1

	max = _plength
	max_res = 0
	for a in res:
		if res[a] > max_res:
			max_res = res[a]
	a = 1
	xs = []
	ys = []
	while a <= max:
		xs.append(a)
		if a in res:
			ys.append(res[a])
		else:
			ys.append(0)
		a += 1

	mpl.style.use('seaborn-notebook')
	plt.xlim(0,int(1.02*_plength))
	ms = 10
	plt.plot(xs,ys,color=(0.25,0,.75,.8),marker='',linestyle='solid',linewidth=1)
#	plt.yscale('log')
	plt.ylabel('observations')
	plt.xlabel('residue')
	plt.grid(True, lw = 1, ls = '--', c = '.9')
#	plt.axvline(x=_plength,color=(.2,.2,.2,.5),linestyle='dotted',linewidth=1)
	plt.title(_title)
	fig = plt.gcf()
	fig.set_size_inches(10, 5)
	cl = re.sub('\|','_',_l)
	plt.gca().get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
	plt.gca().get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

	fig.savefig('png/%s_peps.png' % (cl), dpi=100, bbox_inches='tight')
	plt.show()


	return 1
	
if len(sys.argv) < 2:
		print('start_stop.py PROTEIN_ACC TITLE')
		exit()
label = sys.argv[1]
title = ''
try:
	title = sys.argv[2]
except:
	title = label
tfile = 't.csv'
print('Request protein sequence ...')
protein = get_protein(label)
print('Request peptide information ...')
ls = get_peptides(label,tfile)
print('Create peptide plot ...')
make_peptide_png(label,len(protein),ls,title)
print('Info for %s complete.' % (label))

