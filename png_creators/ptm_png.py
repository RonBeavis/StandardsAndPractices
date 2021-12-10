#
# Copyright © 2019 Ronald C. Beavis
# Licensed under Apache License, Version 2.0, January 2004
#

# Creates a histogram of the frequency of PTM observation
# Information is obtained from GPMDB services and converted into a
# scatter plot

import sys
import requests
import re
import json
import os
import matplotlib.pyplot as plt
import matplotlib.style
import matplotlib as mpl

#obtain the protein sequence for the protein identified by _l
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

# generate a frequency histogram and plot the values
def make_ptm_csv(_l,_plength,_title,_protein,_file,_y):
	session = requests.session()
	seq = list(_protein)
	#formulate a URL to request information about phosphorylation for the protein identified by _l
	url = 'http://gpmdb.thegpm.org/1/peptide/pf/acc=%s&pos=1-%i&w=n' % (_l,_plength)
	values = {'acetyl':None,'phosphoryl':None,'ubiquitinyl':None}
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	try:
		values['phosphoryl'] = json.loads(r.text)
	except:
		return None

	#formulate a URL to request information about acetylation for the protein identified by _l
	url = 'http://gpmdb.thegpm.org/1/peptide/af/acc=%s&pos=1-%i&w=n' % (_l,_plength)
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	try:
		values['acetyl'] = json.loads(r.text)
	except:
		return None

	#formulate a URL to request information about ubiquitinylation for the protein identified by _l
	url = 'http://gpmdb.thegpm.org/1/peptide/uf/acc=%s&pos=1-%i&w=n' % (_l,_plength)
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	try:
		values['ubiquitinyl'] = json.loads(r.text)
	except:
		return None

	#formulate a URL to request information about ubiquitinylation for the protein identified by _l
	url = 'http://gpmdb.thegpm.org/1/peptide/sc/acc=%s&pos=1-%i&w=n' % (_l,_plength)
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	try:
		values['succinyl'] = json.loads(r.text)
	except:
		return None

	#formulate a URL to request information about sumoylation for the protein identified by _l
	url = 'http://gpmdb.thegpm.org/1/peptide/su/acc=%s&pos=1-%i&w=n' % (_l,_plength)
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	try:
		values['K-sumoyl'] = json.loads(r.text)
	except:
		return None

	#formulate a URL to request information about sumoylation for the protein identified by _l
	url = 'http://gpmdb.thegpm.org/1/peptide/ol/acc=%s&pos=1-%i&w=n' % (_l,_plength)
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	try:
		values['ST-glyco'] = json.loads(r.text)
	except:
		return None

	#formulate a URL to request information about R-dimethylation for the protein identified by _l
	url = 'http://gpmdb.thegpm.org/1/peptide/di/acc=%s&pos=1-%i&w=n' % (_l,_plength)
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	try:
		values['dimethyl'] = json.loads(r.text)
	except:
		return None
	#formulate a URL to request information about R-citrullination for the protein identified by _l
	url = 'http://gpmdb.thegpm.org/1/peptide/ct/acc=%s&pos=1-%i&w=n' % (_l,_plength)
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	try:
		values['citrulline'] = json.loads(r.text)
	except:
		return None

	#formulate a URL to request information about KP-oxidation for the protein identified by _l
	url = 'http://gpmdb.thegpm.org/1/peptide/ox/acc=%s&pos=1-%i&w=n' % (_l,_plength)
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	try:
		values['oxidation'] = json.loads(r.text)
	except:
		return None
	a = 1;
	#xs and ys contain the x,y arrays for the scatter plots
	xs = {'citrulline':[],'acetyl':[],'succinyl':[],'N-acetyl':[],'S-phosphoryl':[],'SP-phosphoryl':[],'T-phosphoryl':[],'TP-phosphoryl':[],'Y-phosphoryl':[],'ubiquitinyl':[],'K-sumoyl':[],'R-dimethyl':[],'P-oxidation':[],'K-oxidation':[],'ST-glyco':[]}
	ys = {'citrulline':[],'acetyl':[],'succinyl':[],'N-acetyl':[],'S-phosphoryl':[],'SP-phosphoryl':[],'T-phosphoryl':[],'TP-phosphoryl':[],'Y-phosphoryl':[],'ubiquitinyl':[],'K-sumoyl':[],'R-dimethyl':[],'P-oxidation':[],'K-oxidation':[],'ST-glyco':[]}
	min_obs = 5
	kms = [_protein.find('M',1)]
	if kms[0] != -1:
		kms[0] = kms[0] + 1
		kms.append(kms[0]+1)
	#create x,y arrays for plot
	for a in range(1,_plength+1):
		b = str(a)
		if(b in values['acetyl']) and (seq[a-1] == 'K' or a < 4):
			if values['acetyl'][b] >= min_obs:
				if seq[a-1] == 'K':
					xs['acetyl'].append(a)
					ys['acetyl'].append(values['acetyl'][b])
				else:
					xs['N-acetyl'].append(a)
					ys['N-acetyl'].append(values['acetyl'][b])
		elif(b in values['acetyl']) and a > 3 and a in kms:
			if values['acetyl'][b] >= min_obs:
				xs['N-acetyl'].append(a)
				ys['N-acetyl'].append(values['acetyl'][b])
		if(b in values['phosphoryl']):
			if values['phosphoryl'][b] >= min_obs:
				if seq[a-1] == 'S':
					if a < _plength and seq[a] == 'P':
						xs['SP-phosphoryl'].append(a)
						ys['SP-phosphoryl'].append(values['phosphoryl'][b])
					else:
						xs['S-phosphoryl'].append(a)
						ys['S-phosphoryl'].append(values['phosphoryl'][b])
				if seq[a-1] == 'T':
					if a < _plength and seq[a] == 'P':
						xs['TP-phosphoryl'].append(a)
						ys['TP-phosphoryl'].append(values['phosphoryl'][b])
					else:
						xs['T-phosphoryl'].append(a)
						ys['T-phosphoryl'].append(values['phosphoryl'][b])
				if seq[a-1] == 'Y':
					xs['Y-phosphoryl'].append(a)
					ys['Y-phosphoryl'].append(values['phosphoryl'][b])

		if(b in values['ubiquitinyl']) and seq[a-1] == 'K':
			if values['ubiquitinyl'][b] >= min_obs:
				xs['ubiquitinyl'].append(a)
				ys['ubiquitinyl'].append(values['ubiquitinyl'][b])
				
		if(b in values['succinyl']) and seq[a-1] == 'K':
			if values['succinyl'][b] >= 2:
				xs['succinyl'].append(a)
				ys['succinyl'].append(values['succinyl'][b])

		if(b in values['K-sumoyl']) and seq[a-1] == 'K':
			if values['K-sumoyl'][b] >= 2:
				xs['K-sumoyl'].append(a)
				ys['K-sumoyl'].append(values['K-sumoyl'][b])

		if(b in values['dimethyl']) and seq[a-1] == 'R':
			if seq[a-1] == 'R':
				if values['dimethyl'][b] >= min_obs:
					xs['R-dimethyl'].append(a)
					ys['R-dimethyl'].append(values['dimethyl'][b])
					
					
		if(b in values['citrulline']):
			if seq[a-1] == 'R':
				if values['citrulline'][b] >= min_obs and seq[a-1] == 'R':
					xs['citrulline'].append(a)
					ys['citrulline'].append(values['citrulline'][b])

		if(b in values['oxidation']):
			if values['oxidation'][b] >= min_obs:
				if seq[a-1] == 'K':
					xs['K-oxidation'].append(a)
					ys['K-oxidation'].append(values['oxidation'][b])
				if seq[a-1] == 'P':
					xs['P-oxidation'].append(a)
					ys['P-oxidation'].append(values['oxidation'][b])
		if(b in values['ST-glyco']):
			if seq[a-1] == 'S' or seq[a-1] == 'T':
				if values['ST-glyco'][b] >= min_obs:
					xs['ST-glyco'].append(a)
					ys['ST-glyco'].append(values['ST-glyco'][b])

#	mpl.style.use('seaborn-notebook')
	plt.xkcd()
	plt.rcParams.update({'font.size': 10})
	plt.xlim(0,int(1.02*_plength))
	mx = 0
	for p in ys:
		if len(ys[p]) == 0:
			continue
		m = max(ys[p])
		if m > mx:
			mx = m
	if mx == 0:
		plt.ylim(0,1000)
	ms = 10
	#load all x,y information into a plot
	clrs = {}
	clrs['Azure blue'] = '#0007FFAA'
	clrs['British racing green'] = '#004225AA'
	clrs['Honey'] = '#EC9702AA'
	clrs['India green'] = '#138808AA'
	clrs['Lime green'] = '#32CD32AA'
	clrs['Purple'] = '#6C0BA9AA'
	clrs['Red'] = '#FF0000AA'
	clrs['Turquoise'] = '#00FFEFAA'
	clrs['Violet'] = '#710193AA'
	clrs['White'] = '#EEEEEEAA'
	clrs['Dark grey'] = '#060606AA'
	plt.plot(xs['N-acetyl'],ys['N-acetyl'],color=clrs['Purple'],markersize=ms,marker='o',linestyle='None',label='n-acetyl')
	plt.plot(xs['acetyl'],ys['acetyl'],color=clrs['Azure blue'],markersize=ms,marker='o',linestyle='None',label='K-acetyl')
	plt.plot(xs['succinyl'],ys['succinyl'],color=clrs['India green'],markersize=ms,marker='o',linestyle='None',label='K-succyl')
	plt.plot(xs['S-phosphoryl'],ys['S-phosphoryl'],markersize=ms,color=clrs['Red'],marker='v',linestyle='None',label='S-phos')
	plt.plot(xs['SP-phosphoryl'],ys['SP-phosphoryl'],markersize=ms,color=clrs['Honey'],marker='v',linestyle='None',label='SP-phos')
	plt.plot(xs['T-phosphoryl'],ys['T-phosphoryl'],markersize=ms,color=clrs['Red'],marker='^',linestyle='None',label='T-phos')
	plt.plot(xs['TP-phosphoryl'],ys['TP-phosphoryl'],markersize=ms,color=clrs['Honey'],marker='^',linestyle='None',label='TP-phos')
	plt.plot(xs['Y-phosphoryl'],ys['Y-phosphoryl'],markersize=ms,color=clrs['Red'],marker='o',linestyle='None',label='Y-phos')
	plt.plot(xs['ubiquitinyl'],ys['ubiquitinyl'],markersize=ms,color=clrs['Lime green'],marker='v',linestyle='None',label='K-GG')
	plt.plot(xs['K-sumoyl'],ys['K-sumoyl'],markersize=ms,color=clrs['Lime green'],marker='X',linestyle='None',label='K-sumo')
	plt.plot(xs['R-dimethyl'],ys['R-dimethyl'],markersize=ms,color=clrs['British racing green'],marker='d',linestyle='None',label='R-dimet')
	plt.plot(xs['K-oxidation'],ys['K-oxidation'],markersize=ms,color=clrs['Turquoise'],marker='*',linestyle='None',label='K-oxy')
	plt.plot(xs['P-oxidation'],ys['P-oxidation'],markersize=ms,color=clrs['Violet'],marker='*',linestyle='None',label='P-oxy')
	plt.plot(xs['citrulline'],ys['citrulline'],markersize=ms,color=clrs['British racing green'],marker='.',linestyle='None',label='R-citr')
	plt.plot(xs['ST-glyco'],ys['ST-glyco'],markersize=ms,markerfacecolor=clrs['White'],markeredgewidth=1,markeredgecolor=clrs['Dark grey'] ,marker='s',linestyle='None',label='O-gly')
	#set up the required graph
	plt.yscale('log')
	plt.ylabel('PSMs (tabbs)')
	plt.xlabel('residue')
	plt.legend(loc='best')
	plt.grid(True, lw = 1, ls = '--', c = '.8')
	plt.title(_title)
	ax = plt.gca()
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])
	ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
	ps = ax.get_ylim()
	if ps[1] < 2000:
		ax.set_ylim([1,2000])
	fig = plt.gcf()
	fig.set_size_inches(10, 5)
	cl = re.sub('\|','_',_file)
	plt.gca().get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
	if _y is not None:
		print(_y)
		plt.ylim(1,_y)
	else:
		plt.ylim(1,None)
	#store graph in png file
	fig.savefig('png/%s_ptms.png' % (cl), dpi=100, bbox_inches='tight')
	#display graph on screen
	plt.show()
	return 1

#deal with command line arguments	
if len(sys.argv) < 2:
		print('ptm_png.py PROTEIN_ACC TITLE FILENAME (Y-LIMIT)')
		exit()
label = sys.argv[1]
title = ''
try:
	title = sys.argv[2]
except:
	title = sys.argv[1]

filename = sys.argv[1]
try:
	filename = sys.argv[3]
except:
	filename = sys.argv[1]
y_axis = None
try:
	y_axis = int(float(sys.argv[4]))
except:
	y_axis = None
print('Request protein sequence ...')
protein = get_protein(label)
print('Create PTM plot ...')
make_ptm_csv(label,len(protein),title,protein,filename,y_axis)

