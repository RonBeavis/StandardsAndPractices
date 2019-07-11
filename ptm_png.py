import sys
import requests
import re
import json
import os
import matplotlib.pyplot as plt
import matplotlib.style
import matplotlib as mpl

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

def make_ptm_csv(_l,_plength,_title,_protein):
	session = requests.session()
	seq = list(_protein)
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
	a = 1;
	xs = {'acetyl':[],'S-phosphoryl':[],'T-phosphoryl':[],'Y-phosphoryl':[],'ubiquitinyl':[]}
	ys = {'acetyl':[],'S-phosphoryl':[],'T-phosphoryl':[],'Y-phosphoryl':[],'ubiquitinyl':[]}
	while(a <= _plength):
		b = str(a)
		if(b in values['acetyl']):
			if values['acetyl'][b] != 0:
				xs['acetyl'].append(a)
				ys['acetyl'].append(values['acetyl'][b])

		if(b in values['phosphoryl']):
			if values['phosphoryl'][b] != 0:
				if seq[a-1] == 'S':
					xs['S-phosphoryl'].append(a)
					ys['S-phosphoryl'].append(values['phosphoryl'][b])
				if seq[a-1] == 'T':
					xs['T-phosphoryl'].append(a)
					ys['T-phosphoryl'].append(values['phosphoryl'][b])
				if seq[a-1] == 'Y':
					xs['Y-phosphoryl'].append(a)
					ys['Y-phosphoryl'].append(values['phosphoryl'][b])

		if(b in values['ubiquitinyl']):
			if values['ubiquitinyl'][b] != 0:
				xs['ubiquitinyl'].append(a)
				ys['ubiquitinyl'].append(values['ubiquitinyl'][b])
		a += 1

#	plt.xkcd()
	mpl.style.use('seaborn-notebook')
	plt.xlim(0,int(1.02*_plength))
	ms = 10
	plt.plot(xs['acetyl'],ys['acetyl'],color=(0.25,0,1,.8),markersize=ms,marker='o',linestyle='None',label='acetyl')
	plt.plot(xs['S-phosphoryl'],ys['S-phosphoryl'],markersize=ms,color=(1,0,.25,.8),marker='v',linestyle='None',label='S-phos')
	plt.plot(xs['T-phosphoryl'],ys['T-phosphoryl'],markersize=ms,color=(1,0,.25,.8),marker='^',linestyle='None',label='T-phos')
	plt.plot(xs['Y-phosphoryl'],ys['Y-phosphoryl'],markersize=ms,color=(1,0,.25,.8),marker='o',linestyle='None',label='Y-phos')
	plt.plot(xs['ubiquitinyl'],ys['ubiquitinyl'],markersize=ms,color=(.1,.8,.1,.8),marker='v',linestyle='None',label='K-ubiq')
	plt.yscale('log')
	plt.ylabel('observations')
	plt.xlabel('residue')
	plt.legend(loc='best')
	plt.grid(True, lw = 1, ls = '--', c = '.8')
#	plt.axvline(x=_plength,color=(.2,.2,.2,.5),linestyle='dotted',linewidth=1)
	plt.title(_title)
	fig = plt.gcf()
	fig.set_size_inches(10, 5)
	cl = re.sub('\|','_',_l)
	plt.gca().get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
	fig.savefig('png/%s_ptms.png' % (cl), dpi=100, bbox_inches='tight')
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
	title = sys.argv[1]
print('Request protein sequence ...')
protein = get_protein(label)
print('Create PTM CSV ...')
make_ptm_csv(label,len(protein),title,protein)


