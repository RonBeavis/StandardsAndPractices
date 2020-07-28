# ctweet.py takes tweet text from a command line.
# Each parameter on the line are assembled into a chain of tweets.
# For example, a command line might contain the following parameters
'''
>python3 ctweet.py "This is the first tweet" "This is the 2nd tweet" "/home/user/image.png"
'''
# The first parameter would be used to create the first tweet
# The 2nd parameter would be added as a reply to the first tweet
# The image file would be added to the second tweet as an attachment
# Any parameter that contains only a file path is interpreted as an attachment
# Any number of images can be attached to a tweet
# Any number of tweets can be assembled into a chain
# If the parameter is a number only, it is interpretted as a tweet
# id number and the first line is added as a reply to that tweet.

# redirect stdout to a file if you wish to maintain a log of the process

# the twython package must be installed for this to work
from twython import Twython
import sys
import re
import os

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

# test to see if a parameter is an image file for attachment
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
twitter = Twython(consumer_key, consumer_secret, access_token, access_token_secret,client_args=client_args)
# read parameters into an array
ls = sys.argv[1:]

# replay holds the tweet id number to the most recent tweet sent
# 0 indicates the first tweet should be the base of the chain
reply = 0
try:
	reply = int(ls[0])
	if reply > 10000:
		ls = ls[1:]
except:
	pass

# assemble the tweets into a queue
que = generate_que(ls)
s = {}

# check the reply value
if reply > 10000:
	s['id_str'] = str(reply)

# process the queue
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


