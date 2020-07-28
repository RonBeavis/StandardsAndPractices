
# ftweet.py takes a file path on the command line.
# The lines in that file are assembled into a chain of tweets.
# For example, a file might contain the following lines
'''
This is the first tweet
This is the 2nd tweet
/home/user/image.png
'''
# The first line would be used to create the first tweet
# The 2nd line would be added as a reply to the first tweet
# The image file would be added to the second tweet as an attachment
# Any line that contains only a file path is interpreted as an attachment
# Any number of images can be attached to a tweet
# Any number of tweets can be assembled into a chain
# Any line starting with '#' is ignored
# If the first line is a number only, it is interpretted as a tweet
# id number and the first line is added as a reply to that tweet.

# the twython package must be installed for this to work
from twython import Twython

import sys
import os
import re

#auth.py contains the credentials needed to make tweets
from auth import (
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

#client_args is used for the request headers
client_args = {
  "headers": {
    "accept-charset": "utf-8",
    "User-Agent": "GPM Messages"
  }
}

# test to see if a line is an image file for attachment
def is_image(_l):
	if _l.find('.png') == len(_l)-4:
		return True
	if _l.find('.gif') == len(_l)-4:
		return True
	if _l.find('.jpg') == len(_l)-4:
		return True
	return False

# takes a list of lines and assembles it into tweets
def generate_que(_ls):
	q = []
	v = {}
	for l in _ls:
		if l[0] == '#':
			print(l)
			continue
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

# initialize a Twython object
twitter = Twython(consumer_key, consumer_secret, access_token access_token_secret,client_args=client_args)

# read lines from the command line specified file
lines = [l.strip() for l in open(sys.argv[1],'r',encoding='utf-8') if len(l.strip()) > 0]

# replay holds the tweet id number to the most recent tweet sent
# 0 indicates the first tweet should be the base of the chain
reply = 0
try:
	reply = int(lines[0])
	if reply > 10000:
		lines = lines[1:]
except:
	pass

# log the process
log = open('status.log','a',encoding='utf-8')
print('Tweeting "%s"' % (sys.argv[1]))
log.write('Tweeting "%s"\n' % (sys.argv[1]))

# assemble the tweets into a queue
que = generate_que(lines)
s = {}
# check the reply value
if reply > 10000:
	s['id_str'] = str(reply)
mn = 1
# process the queue
for q in que:
	rs = []
	log.write('\tmessage (%i): %s\n' % (mn,q['message']))
	if 'photo' in q:
		for p in q['photo']:
			log.write('\tphoto (%i): %s\n' % (mn,p))
			photo = open(p, 'rb')
			r = twitter.upload_media(media=photo)
			rs.append(r['media_id'])
			photo.close()
	if 'id_str' in s:
		s = twitter.update_status(status=q['message'],media_ids=rs,in_reply_to_status_id=s['id_str'])
	else:
		s = twitter.update_status(status=q['message'],media_ids=rs)
	log.write('\t%s\n' % (s))
	mn += 1
	print('id = %s' % (s['id_str']))

# close the log and finish
log.close()

