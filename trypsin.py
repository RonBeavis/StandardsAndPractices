# trypsin.py generates a list of the peptides expected from a complete trypstic digest
# that is a digest that cuts the peptide backbone at all eligible sites
import sys
# a test protein sequence
def trypsin(_seq):
	# a list of elegible sites
	ps = [-1]
	# residues cut by trypsin
	ss = set(['K','R'])
	# residues that block cleavage when C-terminal to site
	cbad = set(['P'])
	# length of protein
	lseq = len(_seq)
	# find all cleavage sites and store in ps (zero based coordinates)
	for s in ss:
		i = _seq.find(s)
		while i != -1:
			if i+1 == lseq or _seq[i+1] not in cbad:
				ps.append(i)
			i = _seq.find(s,i+1)
	# add last residue, if not already there
	if lseq-1 not in ps:
		ps.append(lseq-1)
	# sort ps
	ps.sort()
	# list of tryptic peptides
	peps = []
	i = 1;
	remainder = ''
	# using the sites in ps, create a list of peptides using protein coordinates (one based)
	while i < len(ps):
		# ordinary cleavage site
		if ps[i]-ps[i-1] > 1:
			if remainder and ps[i-1] > 1:
				seq = remainder + _seq[ps[i-1]+1:ps[i]+1]
				peps.append({'seq':'%s' % (seq),'f':ps[i-2]+2,'l':ps[i]+1})
				remainder = ''
			seq = _seq[ps[i-1]+1:ps[i]+1]
			peps.append({'seq':'%s' % (seq),'f':ps[i-1]+2,'l':ps[i]+1})
		# deal with cleavage of adjacent sites
		else:
			pl = ''
			f = -1
			if peps:
				pl = peps[-1]['seq']
				f = peps[-1]['f']
			# if there are more than 2 cleavage sites in a row
			if ps[i]-ps[i-2] == 2:
				seq = _seq[ps[i-2]+1:ps[i]+1]
				peps.append({'seq':'%s' % (seq),'f':ps[i-2]+2,'l':ps[i]+1})
			# if there are 2 cleavage sites in a row
			else:
				seq = pl+_seq[ps[i]]
				if len(seq) > 1:
					peps.append({'seq':'%s' % (seq),'f':f,'l':ps[i]+1})
			# residue to add on to the N-terminus of the next peptide
			remainder = _seq[ps[i]]
		if i > 3:
			if ps[i]-ps[i-1] == 1 and ps[i-1]-ps[i-2] > 1 and ps[i-2]-ps[i-3] == 1:
				seq = _seq[ps[i-2]] + peps[-1]['seq']
				peps.append({'seq':'%s' % (seq),'f':ps[i-2]+1,'l':lseq})
			
		i += 1
	# remove any peptides formed by the removal of the first or last residue in a protein
	peps = [p for p in peps if p['l'] != lseq-1 and p['f'] != 2]
	peps = [p for p in sorted(peps, key=lambda k: k['f'])]
	return peps
# show results

proseq = '''MRRGLSKRRLLSARRLALAKAWPTVLQTGTRGFHFTVDRR'''
try:
	proseq = sys.argv[1]
except:
	pass
peps = trypsin(proseq)
for p in peps:
	print(p)

