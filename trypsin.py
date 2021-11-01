# trypsin.py generates a list of the peptides expected from a complete trypstic digest
# that is a digest that cuts the peptide backbone at all eligible sites
import sys

# generate tryptic cleavage by parsing through the sequence

def trypsin(_seq):
	# a list of elegible sites
	ps = [-1]
	# residues cut by trypsin
	ss = set(['K','R'])
	# residues that block cleavage when C-terminal to site
	cbad = set(['P'])
	# length of protein
	lseq = len(_seq)
	seqs = list(_seq)
	peps = []
	i = 0
	j = 0
	# iterate through the sequence
	for i,res in enumerate(seqs):
		if i == lseq - 1:
			continue
		# if you just passed a cleavage site, act
		if i == 0 or (seqs[i-1] in ss and seqs[i] not in cbad):
			j = i + 1
			# is the next residue a cleavage site too
			if j < lseq-1 and seqs[j] in ss and seqs[j+1] not in cbad:
				peps.append({'seq':'%s' % (_seq[i:j+1]),'f':i+1,'l':j+1})
				if i == 0:
					j += 1
				else:
					continue
			# find the next cleavage site
			while j < lseq-1 and not (seqs[j] in ss and seqs[j+1] not in cbad):
				j += 1
			if j < lseq -2:
				peps.append({'seq':'%s' % (_seq[i:j+1]),'f':i+1,'l':j+1})
			j += 1
			# deal with the last residue cleavage problem
			if j < lseq-1 and seqs[j] in ss and seqs[i+1] not in cbad:
				peps.append({'seq':'%s' % (_seq[i:j+1]),'f':i+1,'l':j+1})
			elif j >= lseq - 1:
				peps.append({'seq':'%s' % (_seq[i:j+1]),'f':i+1,'l':lseq})
		else:
			pass
	# make sure everything is in order
	peps = [p for p in sorted(peps, key=lambda k: k['f'])]
	return peps

proseq = '''MTLIEGVGDEVTVLFSVLACLLVLALAWVSTHTAEGGDPLPQPSGTPTPSQPSAAMAATDSMRGEAPGAETPSLRHRGQAAQPEPSTGFTATPPAPDSPQEPLVLRLKFLNDSEQVARAWPHDTIGSLKRTQFPGREQQVRLIYQGQLLGDDTQTLGSLHLPPNCVLHCHVSTRVGPPNPPCPPGSEPGPSGLEIGSLLLPLLLLLLLLLWYCQIQYRPFFPLTATLGLAGFTLLLSLLAFAMYRP'''
try:
	proseq = sys.argv[1]
except:
	pass
peps = trypsin(proseq)
# show results
for p in peps:
	print(p)



