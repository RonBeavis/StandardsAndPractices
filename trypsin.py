# trypsin.py generates a list of the peptides expected from a complete trypstic digest
# that is a digest that cuts the peptide backbone at all eligible sites

# a test protein sequence
proseq = '''MRRGLSKRRLLSARRLALAKAWPTVLQTGTRGFHFTVDRR'''

# a list of elegible sites
ps = [-1]
# residues cut by trypsin
ss = set(['K','R'])
# residues that block cleavage when C-terminal to site
cbad = set(['P'])
# length of protein
lseq = len(proseq)
# find all cleavage sites and store in ps (zero based coordinates)
for s in ss:
	i = proseq.find(s)
	while i != -1:
		if i+1 == lseq or proseq[i+1] not in cbad:
			ps.append(i)
		i = proseq.find(s,i+1)
# add last residue, if not already there
if lseq-1 not in ps:
	ps.append(lseq-1)
# sort ps
ps.sort()
# list of tryptic peptides
peps = []
i = 1;
remainder = ''
while i < len(ps):
	# ordinary cleavage site
	if ps[i]-ps[i-1] > 1:
		if remainder and ps[i-1] > 1:
			seq = remainder + proseq[ps[i-1]+1:ps[i]+1]
			peps.append({'seq':'%s' % (seq),'f':ps[i-2]+2,'l':ps[i]+1})
			remainder = ''
		seq = proseq[ps[i-1]+1:ps[i]+1]
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
			seq = proseq[ps[i-2]+1:ps[i]+1]
			peps.append({'seq':'%s' % (seq),'f':ps[i-2]+2,'l':ps[i]+1})
		# if there are 2 cleavage sites in a row
		else:
			seq = pl+proseq[ps[i]]
			if len(seq) > 1:
				peps.append({'seq':'%s' % (seq),'f':f,'l':ps[i]+1})
		# residue to add on to the N-terminus of the next peptide
		remainder = proseq[ps[i]]
	i += 1
# remove any peptides formed by the removal of the first or last residue in a protein
peps = [p for p in peps if p['l'] != lseq-1 and p['f'] != 2]

# show results
for p in sorted(peps,key=lambda k: k['f']):
	print(p)

