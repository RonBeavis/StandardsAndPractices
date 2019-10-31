# a simple protein FASTA sequence shuffler
# that preserves tryptic peptide amino acid
# composition and location
# version 1.0

from random import shuffle
import sys

# shuffles any peptide
def s_p(_p):
	if len(_p) == 0:
		return _p
	kr = _p[len(_p)-1]
	l = list(_p[:-1])
	shuffle(l)
	return ''.join(l)+kr

# shuffles a protein
def scramble(_s):
	n = ''
	p = ''
	for i,a in enumerate(list(_s)):
		if a == 'K' or a == 'R':
			n += s_p(p + a)
			p = ''
		else:
			p += a
	n += s_p(p)
	return n

if len(sys.argv) < 3 or sys.argv[1] == '-h':
	print('usage: >python3 psuffle.py IN_FASTA OUT_FASTA')
	exit()
# reads a FASTA file specified on the command line
fasta = [l.strip() for l in open(sys.argv[1],'r')]
# opens an output FASTA file specified on the command line
o = open(sys.argv[2],'w')
s = ''
l = ''
for f in fasta:
	if f.find('>') != -1:
		if len(s) != 0:
			o.write(l+' (shuffled)\n')
			d = scramble(s)
			v = '\n'.join(d[i:i+50] for i in range(0, len(d), 50))
			if v[:-1] != '\n':
				v += '\n'
			o.write(v)
		l = f
		s = ''
		continue
	s += f
if len(s) != 0:
	o.write(l+'\n')
	d = scramble(s)
	v = '\n'.join(d[i:i+50] for i in range(0, len(d), 50))
	if v[:-1] != '\n':
		v += '\n'
	o.write(v)
o.close()

