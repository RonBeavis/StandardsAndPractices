#
# Copyright © 2019 Ronald C. Beavis
# Licensed under Apache License, Version 2.0, January 2004
#

# A test-of-concept prototype for making histograms of protein-specific information
# peptides_png.py, ptm_png.py and ptm_normalized_png.py were created using
# the results of this prototype

import sys
import requests
import re
import json
import os

def get_peptides(_l,_t):
	url = 'https://gpmdb.thegpm.org/protein/model/%s&excel=1' % (_l)
	session = requests.session()
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	out = open('csv/%s'%_t,'w')
	text = re.sub('\r\n','\n',r.text)
	out.write(text)
	out.close()
	return 1

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

def make_ptm_csv(_l,_plength):
	session = requests.session()
	url = 'http://gpmdb.thegpm.org/1/peptide/pf/acc=%s&pos=1-%i&w=n' % (_l,_plength)
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	try:
		pvalues = json.loads(r.text)
	except:
		return None
	url = 'http://gpmdb.thegpm.org/1/peptide/af/acc=%s&pos=1-%i&w=n' % (_l,_plength)
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	try:
		avalues = json.loads(r.text)
	except:
		return None
	url = 'http://gpmdb.thegpm.org/1/peptide/uf/acc=%s&pos=1-%i&w=n' % (_l,_plength)
	try:
		r = session.get(url,timeout=20)
	except requests.exceptions.RequestException as e:
		print(e)
		return None
	try:
		uvalues = json.loads(r.text)
	except:
		return None
	output = open('csv/%s_ptms.csv' % (_l),'w')
	a = 1;
	output.write('residue,acetyl,phosphoryl,ubiquitnyl\n')
	while(a <= _plength):
		l = '%i,' % (a)
		b = str(a)
		if(b in avalues):
			if avalues[b] == 0:
				l += ','
			else:
				l += '%i,' % (avalues[b])
		else:
			l += ','
		if(b in pvalues):
			if pvalues[b] == 0:
				l += ','
			else:
				l += '%i,' % (pvalues[b])
		else:
			l += ','
		if(b in uvalues):
			if uvalues[b] == 0:
				l += '\n'
			else:
				l += '%i\n' % (uvalues[b])
		else:
			l += '\n'
		output.write(l)
		a += 1
	output.close()
	return 1

def make_peptide_csv(_l,_t,_plength)	:
	input = open('csv/%s'%_t,'r')
	output = open('csv/%s_peptides.tsv' % (_l),'w')
	lines = input.read().splitlines()
	input.close()
	os.remove('csv/%s'%_t)
	start = {}
	end = {}
	res = {}
	max = 0
	for line in lines[1:]:
		vs = line.split('\t')
		vs[0] = int(vs[0])
		vs[1] = int(vs[1])
		vs[2] = int(vs[2])
		if vs[0] in start:
			start[vs[0]] = start[vs[0]] + vs[2]
		else:
			start[vs[0]] = vs[2]
		if vs[1] in end:
			end[vs[1]] = end[vs[1]] + vs[2]
		else:
			end[vs[1]] = vs[2]
		if vs[1] > max:
			max = vs[1]
		a = vs[0]
		while a <= vs[1]:
			if a in res:
				res[a] = res[a] + vs[2]
			else:
				res[a] = vs[2]
			a += 1

	max = _plength
	max_res = 0
	for a in res:
		if res[a] > max_res:
			max_res = res[a]
	a = 1
	vals = {}
	while a <= max:
		l = '%i\t' % a
		if a in start:
			l += '%i\t' % start[a]
		else:
			l += '%i\t' % 0
		if a in end:
			l += '%i\t' % end[a]
		else:
			l += '%i\t' % 0
		if a in res:
			l += '%i\t' % res[a]
		else:
			l += '%i\t' % 0
		if a in res:
			l += '%f\n' % (float(res[a])/float(max_res))
			vals[a] = float(res[a])/float(max_res)
		else:
			l += '%f\n' % 0
			vals[a] = 0
		output.write(l)
		a += 1
	vals['scale'] = max_res
	output.close()
	return vals
	
def get_xtics(_len):
	if(_len <= 100):
		return 10;
	elif(_len <= 500):
		return 50;
	elif(_len <= 1000):
		return 100;
	elif(_len <= 5000):
		return 500;
	elif(_len <= 10000):
		return 1000;
	elif(_len <= 50000):
		return 5000;
	return 10000;

def make_rof_svg(_l,p_length,_vs,_title):
	output = open('csv/%s_svg.html' % (_l),'w')
	output.write('<!DOCTYPE html lang="en">\n<html><head>')
	output.write('''<title>%s</title>
<meta charset="utf-8" />
<meta http-equiv="x-ua-compatible" content="ie=edge">
<meta http-equiv="Cache-control: no-cache" content="public">
<meta http-equiv="Pragma: no-cache" content="public">
<meta name="viewport" content="width=device-width, initial-scale=1" />\n''' % (_title))
	output.write('</head>\n<body>\n')
	width = 900
	height = 500
	bly = 450
	blx = 50
	xscale = 800/p_length
	yscale = 400
	output.write('<svg width="%i" height="%i">\n' % (width,height))
	v = 0.0
	a = 0
	while(v <= 1.0):
		y1 = bly - v*yscale
		output.write('<line x1="50" y1="%i" x2="45" y2="%i" style="stroke:rgb(0,0,0);stroke-width:2" />\n' % (y1,y1))
		output.write('<line x1="52" y1="%i" x2="859" y2="%i" style="stroke:rgb(200,200,200);stroke-width:1" />\n' % (y1,y1))
		if(a % 2 == 0):
			output.write('<text x="20" y="%i" fill="black" style="font-family: Calibri, Arial, Helvetica, sans-serif;">%.1f</text>\n' % (y1+6,v))
		a += 1
		v += 0.1
	output.write('<text x="20" y="265" fill="black" transform="rotate(270,20,265)" style="font-family: Calibri, Arial, Helvetica, sans-serif;">o(r)</text>\n')
	xtic = get_xtics(p_length)
	a = 0
	while(a < p_length):
		x1 = a*xscale + 50
		output.write('<line x1="%i" y1="450" x2="%i" y2="455" style="stroke:rgb(0,0,0);stroke-width:2" />\n' % (x1,x1))
		output.write('<line x1="%i" y1="449" x2="%i" y2="41" style="stroke:rgb(200,200,200);stroke-width:1"  />\n' % (x1,x1))
		if(a == 0):
			output.write('<text x="%i" y="470" fill="black" text-anchor="middle" style="font-family: Calibri, Arial, Helvetica, sans-serif;">%i</text>\n' % (x1,1))
		else:
			output.write('<text x="%i" y="470" fill="black" text-anchor="middle" style="font-family: Calibri, Arial, Helvetica, sans-serif;">%i</text>\n' % (x1,a))
		a += xtic
	a = 1
	while(a < p_length):
		x1 = a*xscale + 50
		x2 = (a+1)*xscale + 50
		y1 = bly - _vs[a]*yscale
		y2 = bly - _vs[a+1]*yscale
		output.write('<line x1="%i" y1="%i" x2="%i" y2="%i" style="stroke:rgb(255,0,0);stroke-width:2" />\n' % (x1,y1,x2,y2))
		a += 1
	output.write('<text x="450" y="490" fill="black" text-anchor="middle" style="font-family: Calibri, Arial, Helvetica, sans-serif;">residues (r)</text>\n')
	output.write('<text x="450" y="20" fill="black" text-anchor="middle" style="font-family: Calibri, Arial, Helvetica, sans-serif; font-size: 14pt">%s</text>\n' % (_title))
	sc = f"{_vs['scale']:,d}"
	output.write('<text x="50" y="35" fill="black" text-anchor="left" style="font-family: Calibri, Arial, Helvetica, sans-serif; font-size: 12pt">scale 1 : %s</text>\n' % (sc))
	output.write('<rect x="50" y="40" width="810" height="410" style="fill-opacity: 0;fill:rgb(255,255,255);stroke-width:2;stroke:rgb(0,0,0)" />\n')
	output.write('</svg>\n')
	output.write('</body>\n</html>\n')
	
	output.close()

if len(sys.argv) < 2:
		print('start_stop.py PROTEIN_ACC TITLE')
		exit()
label = sys.argv[1]
title = ''
try:
	title = sys.argv[2]
except:
	title = ''
tfile = 't.csv'
print('Request protein sequence ...')
protein = get_protein(label)
print('Request peptide information ...')
get_peptides(label,tfile)
print('Create peptide CSV ...')
vals = make_peptide_csv(label,tfile,len(protein))
print('Create PTM CSV ...')
make_ptm_csv(label,len(protein))
print('Create ROF SVG ...')
make_rof_svg(label,len(protein),vals,title)
print('Info for %s complete.' % (label))

