import os
import sys
import requests
import re
import json
import random
import matplotlib.pyplot as plt
import matplotlib.style
import matplotlib as mpl

def create_pngs(_js):
	ps = _js['accessions']
	for p in ps:
		cmd = 'python3 ptm_imager.py %s %s %s %s' % (ps[p],'"%s PTMs"'%(ps[p]),p,_js['directory'])
		print('<!-- ' + cmd + ' -->')
		os.system(cmd + ' >/dev/null')

def get_description(_l):
	url = 'http://rest.thegpm.org/1/protein/description/acc=%s' % (_l)
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

def start_page(_t):
	print('''<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta charset="utf-8">
<title>%s</title>''' % (_t))
	print('''<meta name="viewport" content="width=device-width,initial-scale=1" />
<link rel="stylesheet" type="text/css" href="/ma-diagrams/css/ma-diagrams.css" />
</head>
<body>
		''')

def end_page():
	print('''<br /><p id="copyright">Copyright &copy; 2019 GPMDB&nbsp;<img style="vertical-align: middle;" src="/pics/the_gpm_db_140x105.png" height="20" />''')
	print('''</body>\n</html>\n''')

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

lines = [s for s in open(sys.argv[1],'r')]
js = json.loads(''.join(lines))
headings = js['headings']
heading_colors = js['heading_colors']
start_page(js['title'])
try:
	if sys.argv[2] == 'yes':
		if not os.path.exists(js["directory"]):
			os.makedirs(js["directory"])
		create_pngs(js)
except:
	pass
fs = os.listdir(js['directory'])
ls = []
for f in sorted(fs):
	if f.find('_ptms.png') != -1:
		ls.append(f)

ls.sort(key=natural_keys)
bar = ''
if len(headings) > 1:
	bar = '<div class="bar alt">|&nbsp;'
	for h in headings:
		bar += '<a class="bar" href="#%s">%s</a>&nbsp;|&nbsp;' % (h,h)
	bar += '</div>'
print('<div id="pic"><img class="top-pic" src="%s" /></img></div>' % js['image'])
print('''<div class="content">%s</div>''' % (js['description']))
print('''<div class="content">The following Modification-Abundance (M-A) diagrams show the number of times a residue has been observed with 
a particular PTM in a peptide-to-spectrum match in GPMDB, as a function of the residue's position in the corresponding protein sequence. 
Note that the Y-axes have log scales.</div>''') 
print(bar)
hcolor = ''
d = js['directory']
for h in headings:
	hcolor = heading_colors[h]
	print('<div id="%s" class="title" style="background-color: %s;"><b>&nbsp;%s proteins</b><div id="%s.proteins"></div></div>' % (h,hcolor,h,h))
	print('<div class="content" id="bar-%s"></div>' % (h))
	thumbs = ''
	proteins = '|'
	for f in ls:
		t = re.sub(r'(.+?)\_.+',r'\1',f)
		if t not in headings[h]:
			continue
		print('<div id="%s"><img class="pic" src="/ma-diagrams/%s/%s" title="%s:p"/></div>' % (t,d,f,t))
		try: 
			acc = js['accessions'][t]
			desc = get_description(acc)
			print('<div id="%s.desc" class="desc">%s &mdash; %s (<a href="http://gpmdb.thegpm.org/_/ptm_png/l=%s" target="_blank">details</a>)</div>' % (t,h,desc,acc))
		except:
			print('<div id="%s.desc" class="desc">%s &mdash; %s:p</div>' % (t,h,t))
		print('<hr class="pic" style="background-color: %s;color: %s" />' % (hcolor,hcolor))
		proteins += " <a class='bar' href='#%s'>%s</a> |" % (t,t)
		thumbs += "<a href='#%s'><img class='bar-pic zoom' src='/ma-diagrams/%s/%s' title='%s:p'/></a>" % (t,d,f,t)
	print('<script>document.getElementById("bar-%s").innerHTML="%s";\ndocument.getElementById("%s.proteins").innerHTML="%s"</script>' % (h,thumbs,h,proteins))
end_page()
