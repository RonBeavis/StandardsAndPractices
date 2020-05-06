# vcf_confirmer.py checks a GPM csv-formatted SAV file against a FASTA file
# of current protein sequences. Any SAV with a reference allele that does not agree with the
# FASTA file's protein sequence is rejected
# the csv-formatted SAV files are assumed to have been created by vcf_explorer.py

import re
import sys

try:
	if not os.path.isfile(sys.argv[1]):
		print('File %s does not exist' % (sys.argv[1]))
		exit()
except:
	print('''usage: >python3 vcf_confirmer.py FASTA_FILE CSV_FILE''')
#open FASTA file
f = open(sys.argv[1],'r')
acc = ''
protein = ''
pros = {}
#load protein sequences into a dictionary, indexed by the accession number
for l in f:
	line = l.strip()
	if line.find('>') == 0:
		if len(protein) > 0:
			pros[acc] = protein
		protein = ''
		acc = re.sub(r'\>(\w+)\..+',r'\1',line)
	else:
		protein += line

if len(protein) > 0:
	pros[acc] = protein
f.close()
try:
	if not os.path.isfile(sys.argv[2]):
		print('File %s does not exist' % (sys.argv[2]))
		exit()
except:
	print('''usage: >python3 vcf_confirmer.py FASTA_FILE CSV_FILE''')
#open the CSV file and an output file
v = open(sys.argv[2],'r')
o = open(sys.argv[2]+'.1.txt','w')
missed = 0
absent = 0
bad = 0
ok = 0
#run through each entry, checking the protein sequence dictionary for
#reference allele agreement
for l in v:
	vs = l.strip().split(',')
	pos = int(vs[2])-1
	if vs[0] in pros:
		if len(pros[vs[0]])-1 >= pos:
			try:
				res = pros[vs[0]][pos]
			except:
				print(len(pros[vs[0]]),pos,'?')
				missed += 1
				continue
		else:
			print(len(pros[vs[0]]),pos,'>')
			missed += 1
			continue
	else:
		print(vs[0],'absent')
		absent += 1
		continue
	if res == vs[3][0]:
		o.write(l)
		ok += 1
	else:
		print('bad',res,vs[3][0])
		bad += 1

v.close()
print('bad = %i, absent = %i, missed = %i, ok = %i' % (bad,absent,missed,ok))


