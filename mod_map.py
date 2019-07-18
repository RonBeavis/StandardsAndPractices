import xml.sax
import sys
import re
import matplotlib.pyplot as plt
import matplotlib.style
import matplotlib as mpl

class bioMLHandler(xml.sax.ContentHandler):
	def __init__(self):
		self.cTag = ''
		self.isDomain = False
		self.isAa = False
		self.mods = {}
		self.spectra = set()
		self.current = None
		self.domSum = 0.0
			
	def startElement(self, tag, attrs):
		self.cTag = tag
		if tag == 'domain':
			self.current = int(re.sub('\..+','',attrs['id']))
			self.isDomain = True
			self.domSum = 0.0
		if tag == 'aa':
			self.domSum += float(attrs['modified'])

	def endElement(self, tag):
		if tag == 'domain':
			mod = int(self.domSum + 0.5)
			if self.current not in self.spectra:
				if mod in self.mods:
					self.mods[mod] += 1
				else:
					self.mods[mod] = 1
				self.spectra.add(self.current)

	def get_mod_map(self):
		return self.mods

def render_map(_map,_title,_file):
	xs = []
	ys = []
	for x in range(min(_map)-10,max(_map)+10):
		if x not in _map:
			continue
		xs.append(x)
		if x in _map:
			ys.append(_map[x])
		else:
			ys.append(0)
	mpl.style.use('seaborn-notebook')
	plt.bar(xs,ys,color=(1,0,0,1),linewidth=10)
	plt.yscale('log')
#	plt.yscale('linear')
	plt.ylabel('PSMs')
	plt.xlabel('ΔM (measured-sequence, Da)')
	plt.grid(True, lw = 1, ls = '--', c = '.90')
#	plt.axvline(x=_plength,color=(.2,.2,.2,.5),linestyle='dotted',linewidth=1)
	plt.title(_title)
	fig = plt.gcf()
	fig.set_size_inches(10, 5)
	plt.gca().set_axisbelow(True)
	plt.gca().get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
	plt.gca().get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
	fig.savefig('png/%s.png' % (_file), dpi=100, bbox_inches='tight')
	plt.show()
	plt.show()

try:
	fpath = sys.argv[1]
except:
	print('Error opening file specified on command line:\ne.g. ">mod_map.py INPUT_FILE"')
	exit()
title = fpath
try:
	title = sys.argv[2]
except:
	title = fpath
parser = xml.sax.make_parser()
parser.setContentHandler(bioMLHandler())
parser.parse(open(fpath,"r"))
mod_map = parser.getContentHandler().get_mod_map()
render_map(mod_map,title,fpath)


