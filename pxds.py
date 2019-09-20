import re
import requests
from operator import itemgetter

lines = []
#for l in open('pxdids.html','r', encoding='latin-1'):
#	lines.append(l.rstrip())

url = 'http://proteomecentral.proteomexchange.org/cgi/GetDataset?action=search'
session = requests.session()
try:
	r = session.get(url,timeout=20)
	r.encoding = 'cp1252'
except requests.exceptions.RequestException as e:
	print(e)
	exit()

lines = r.text.split('\n')
values = []
mx = 0
for l1 in lines:
	if l1.find('PXD0') == -1:
		continue
	if l1.find('RPXD0') != -1:
		continue
	l = re.sub(r'\s+',' ',l1.rstrip())
	l = re.sub(r'[\"\']',' ',l)
	ls = l.split('</td> <td>')
	vs = []
	for i,s in enumerate(ls):
		if i != 5:
			z = re.sub(r'\<.*?\>','',s)
			if len(z) > mx:
				mx = len(z)
#			if len(z) > 100:
#				z = z[0:100] + ' ...'
			vs.append(z)
		else:
			z = re.sub(r'\<.*?\>','',s)
			if len(z) > mx:
				mx = len(z)
			vs.append(z)
			if s.find('www.ncbi') != -1:
				z = re.sub(r'.+?pubmed\/(\d+).+$',r'\1',s)
				vs.append(z)
			else:
				vs.append('')
	if len(vs) != 10:
		print(len(vs))
	values.append(vs)
print(mx)	
f = open('pxdids.tsv','w')

for v in sorted(values,key=itemgetter(0)):
	f.write('\t'.join(v)+'\n')
f.close()


