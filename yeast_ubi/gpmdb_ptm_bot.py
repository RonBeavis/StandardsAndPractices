#
# Copyright © 2021 Ronald C. Beavis
# Licensed under Apache License, Version 2.0, January 2004
#

# Takes a list of protein accession numbers in a file and generates
# a list of lysine residues that have been observed with ubiquitination
# and the number of times the ubiquitination has been observed.

import sys
import requests
import re
import json
import os

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

# generate a frequency histogram and returns the values
def get_list(_l):
	#get the protein sequence to sanity check the results
	seq = list(get_protein(_l))
	#create a session for a REST request
	session = requests.session()
	values = {}	#will hold the information retrieved by the REST request
	#formulate a URL to request information about ubiquitinylation for the protein identified by _l
	url = 'http://gpmdb.thegpm.org/1/peptide/uf/acc=%s&pos=1-%i&w=n' % (_l,len(seq))
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	try:
		values = json.loads(r.text)
	except:
		return None
	rvalues = {}	#cleaned up results
	#run through the results of the REST request and clean them up
	for v in values:
		try:
			if values[v] > 0 and seq[int(v)-1] == 'K':
				rvalues[int(v)] = values[v]
		except:
			continue
	return rvalues;
				
	

#deal with command line arguments	
if len(sys.argv) < 2:
		print('gpmdb_ptm_bot.py FILENAME')
		exit()
#file contains a list of accession numbers
filename = sys.argv[1]
accs = [l.strip() for l in open(filename,'r')]
for acc in accs:
	ls = get_list(acc)
	print(acc)
	for v in sorted(ls):
		print('%i\t%i' % (v,ls[v]))


