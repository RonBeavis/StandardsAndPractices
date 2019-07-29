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
	#create URL for request to GPMDB
	url = 'https://gpmdb.thegpm.org/protein/model/%s&excel=1' % (_l)
	session = requests.session()
	try:
		r = session.get(url,timeout=500)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	#process the TSV output from GPMDB
	text = re.sub('\r\n','\n',r.text)
	lines = text.split('\n')
	#store the information in a dict with the peptide sequence as the key
	amap = {}
	for l in lines:
		vs = l.split('\t')
		#skip blank lines and the heading line
		if len(vs) != 5 or vs[0] == 'Start':
			continue
		amap[vs[4]] = vs
	return amap

#create a TSV formatted output listing the sequences, the corresponding
#start of the peptide in protein coordinates and the number of times the
#peptide has been identified

def generate_overlap(_seqs,_lbls):
	all_seq = set()
	#create a set of all peptide sequences in all proteins
	for v in _seqs:
		for a in v:
			all_seq.add(a)
	c = 0
	#create top line for output
	title = '#\tsequence\t'
	for l in _lbls:
		title += '%s\t' % (l)
	title += 'observations'
	print(title)
	lines = []
	cmap = []
	#organize information for each of the peptide sequences
	for s in all_seq:
		#get peptide sequence
		line = [s]
		obs = 0
		ts = 0
		a = 0
		ccs = []
		#iterate through each protein result
		for v in _seqs:
			#store start positions for the peptide sequence
			if s in v:
				line.append(int(v[s][0]))
				ts += 1
				#get observations from the sequence
				if int(v[s][2]) > obs:
					obs = int(v[s][2])
			#if peptide not in protein, record a null string
			else:
				line.append('')
			#store start values for sorting
			if s in v:
				ccs.append(int(v[s][0]))
			#if peptide not in protein, record start as 0 for sorting
			elif s not in v:
				ccs.append(0)
			a += 1
		#add observations information for the sequence
		line.append(obs)
		#store array elements for a line in output
		lines.append(line)
		#store start values for sorting lines
		cmap.append(ccs)
		c += 1
	#generate indexes for sorted lines
	cs = sorted(enumerate(cmap), key=lambda x: x[1][0])
	c = 1
	#produce output
	for c,cs1 in enumerate(cs):
		ls = [str(a) for a in lines[cs1[0]]]
		print('%i\t%s' % (c+1,'\t'.join(ls)))

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

