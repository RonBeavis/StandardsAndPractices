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
    "accept-charset": "utf-8"
  }
}

def generate_que(_ls):
	q = []
	v = {}
	for l in _ls:
		if os.path.isfile(l):
			if 'photo' in v:
				v['photo'].append(l)
			else:
				v['photo'] = [l]
		else:
			if len(v) > 0:
				q.append(v)
			v = {}
			v['message'] = re.sub(r'\<br\>',r'\n',l)
	if len(v) > 0:
		q.append(v)
	return q
		
twitter = Twython(consumer_key, consumer_secret, access_token, access_token_secret)

que = generate_que(sys.argv[1:])
s = {}
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


