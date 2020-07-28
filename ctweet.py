from twython import Twython
import sys
import re
import os

from auth import (
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

client_args = {
  "headers": {
    "accept-charset": "utf-8",
    "User-Agent": "GPM Messages"
  }
}

def is_image(_l):
	if _l.find('.png') == len(_l)-4:
		return True
	if _l.find('.gif') == len(_l)-4:
		return True
	if _l.find('.jpg') == len(_l)-4:
		return True
	return False

def generate_que(_ls):
	q = []
	v = {}
	for l in _ls:
		if is_image(l):
			if os.path.isfile(l):
				if 'photo' in v:
					v['photo'].append(l)
				else:
					v['photo'] = [l]
			else:
				print('Error: file "%s" does not exist' % (l))
				exit()
		else:
			if len(v) > 0:
				q.append(v)
			v = {}
			v['message'] = re.sub(r'\<br\>',r'\n',l)
	if len(v) > 0:
		q.append(v)
	return q
		
twitter = Twython(consumer_key, consumer_secret, access_token, access_token_secret,client_args=client_args)
ls = sys.argv[1:]
reply = 0
try:
	reply = int(ls[0])
	if reply > 10000:
		ls = ls[1:]
except:
	pass

que = generate_que(ls)
s = {}

if reply > 10000:
	s['id_str'] = str(reply)

for q in que:
	rs = []
	if 'photo' in q:
		for p in q['photo']:
			photo = open(p, 'rb')
			r = twitter.upload_media(media=photo)
			rs.append(r['media_id'])
			photo.close()
	if 'id_str' in s:
		s = twitter.update_status(status=q['message'],media_ids=rs,in_reply_to_status_id=s['id_str'])
	else:
		s = twitter.update_status(status=q['message'],media_ids=rs)
	print('id = %s' % (s['id_str']))

