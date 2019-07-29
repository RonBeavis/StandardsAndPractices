#
# Copyright © 2019 Ronald C. Beavis
# Licensed under Apache License, Version 2.0, January 2004
#

# Finds peptide sequence overlaps between a list of protein accession numbers
# Information is obtained from GPMDB services

import sys
import requests
import re
import json
import os

#obtain the protein sequence for the protein identified by _l

def get_peptides(_l):
	url = 'https://gpmdb.thegpm.org/protein/model/%s&excel=1' % (_l)
	session = requests.session()
	try:
		r = session.get(url,timeout=500)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	text = re.sub('\r\n','\n',r.text)
	lines = text.split('\n')
	amap = {}
	for l in lines:
		vs = l.split('\t')
		if len(vs) != 5 or vs[0] == 'Start':
			continue
#		print(vs)
		amap[vs[4]] = vs
	return amap

#create a TSV formatted output listing the sequences, the corresponding
#start of the peptide in protein coordinates and the number of times the
#peptide has been identified

def generate_overlap(_seqs,_lbls):
	all_seq = set()
	for v in _seqs:
		for a in v:
			all_seq.add(a)
	c = 0
	title = '#\tsequence\t'
	for l in _lbls:
		title += '%s\t' % (l)
	title += 'observations'
	print(title)
	lines = []
	cmap = []
	for s in all_seq:
		line = '%s\t' % (s)
		obs = 0
		ts = 0
		a = 0
		for v in _seqs:
			if s in v:
				line += '%i\t' % (int(v[s][0]))
				ts += 1
				if int(v[s][2]) > obs:
					obs = int(v[s][2])
			else:
				line += '\t'
			if a == 0 and s in v:
				cmap.append(int(v[s][0]))
			elif a == 0 and s not in v:
				cmap.append(0)
			a += 1
		line += '%i' % obs
		lines.append(line)
		c += 1
	cs = sorted(enumerate(cmap), key=lambda x: x[1])
	c = 1
	for c,cv in enumerate(cs):
		print('%i\t%s' % (c+1,lines[cv[0]]))

def main():
	#deal with the command line
	if len(sys.argv) < 2:
		print('splice_overlap.py ACC1,ACC2, ...')
		exit()
	lbls = sys.argv[1].split(',')
	seqs = []
	#get peptide observation information for each accession number
	for l in lbls:
		smap = get_peptides(l)
		if smap is None:
			print('%s did not return a map' % l)
			exit()
		seqs.append(smap)
	#generate TSV formatted information
	generate_overlap(seqs,lbls)

if __name__== "__main__":
	main()

