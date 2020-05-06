# vcf_explorer.py takes a VCF file from https://gnomad.broadinstitute.org/downloads and
# converts it into an SAV format compat.ble with the GPM.
# The GPM compatible information is sent to stdout, so to capture it in a file
# use a command like:
# >python3 vcf_explorer.py VCF_FILE 1>human_sites.csv 2>human_sites.err

import re
import sys
import os

# translate 3 letter abbreviations used by gnomad into 1 letter abbreviations

trans = {'Ala': 'A',
	'Cys':'C',
	'Asp':'D',
	'Glu':'E',
	'Phe':'F',
	'Gly':'G',
	'His':'H',
	'Ile':'I',
	'Lys':'K',
	'Leu':'L',
	'Met':'M',
	'Asn':'N',
	'Pro':'P',
	'Gln':'Q',
	'Arg':'R',
	'Sec':'U',
	'Ser':'S',
	'Thr':'T',
	'Val':'V',
	'Trp':'W',
	'Tyr':'Y'}

# convert the HGVS annotation into GPM csv format
def get_values(_m,_r):
	#extract the ENSEMBL accession
	acc = re.sub(r'(ENSP\d+).+',r'\1',_m)
	#extract the coordinates and residues
	v = re.sub(r'.+\:p\.(\w+)',r'\1',_m)
	#extract the reference residue
	r1 = re.sub(r'^(\w\w\w).+',r'\1',v)
	#extract the protein coordinate
	pos = re.sub(r'^\w\w\w(\d+).+',r'\1',v)
	#extract the variant residue
	r2 = re.sub(r'^\w\w\w\d+(\w\w\w).+',r'\1',v)
	#test for non-SAAV variants
	if r1 not in trans:
		sys.stderr.write('r1 = %s\n' % (r1))
		return None
	if r2 not in trans:
		sys.stderr.write('r2 = %s\n' % (r2))
		return None

	ms = '%s,%s,%s,%s/%s' % (acc,_r,pos,trans[r1],trans[r2])
	return ms

try:
	if not os.path.isfile(sys.argv[1]):
		print('File %s does not exist' % (sys.argv[1]))
		exit()
except:
	print('''usage: >python3 vcf_explorer.py VCF_FILE
To store to file, use somthing like:
>python3 vcf_explorer.py VCF_FILE 1>human_sites.csv 2>human_sites.err
''')
	exit()

#open gnomad VCF file
f = open(sys.argv[1],'r')
#go through the file and find SAVs
for l in f:
	#skip comment lines
	if l.find('#') == 0:
		continue
	#parse TSV values
	vs = l.split('\t')
	#bail if no rs number
	if vs[2].find('rs') != 0:
		continue
	#deal with HGVS formatted SAVs
	if vs[7].find('ENSP0') != -1:
		matches = re.findall(r'ENSP0[\d\.]+\:p.+?\|',vs[7])
		for m in matches:
			if m.find('?') == -1:
				ms = get_values(m,vs[2])
				if ms:
					#filter with and include frequency information
					if vs[7].find('non_topmed_AF_popmax') != -1:
						pop = re.sub(r'.+non\_topmed\_AF\_popmax\=(.+?)\;.+',r'\1',vs[7])
						if float(pop) > 0.0001:
							print('%s,%.1e'% (ms,float(pop)))
f.close()

