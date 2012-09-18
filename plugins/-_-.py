## Copyright 2009-2012 Joey
## 
## Jobot is released under Affero GPL. Please read the license before continuing.
## 
## The latest source can be found here:
##	 https://github.com/MOSW/wallybot
##
import meta
import re
import random
from threading import Timer

random.seed()


if 'tenso' not in meta.conf:
	meta.conf['tenso'] = False

def msg(s, nick, ident, host, channel, text):
	
	
	if nick in meta.conf['ignore'] or host in meta.conf['ignorehost']:
		return False
	
	if nick == meta.conf['nick']:
		return True
		
	if channel == meta.conf['nick']:
		channel = nick
	
	if not meta.conf['tenso']: return True
	
	a = re.match(r"\s?([-><]+)(_+)([-><]+)\s?$", text)
	if a:
		k = False
		t = "TENSO"
		
		if len(text) > 12:
			meta.sendMsg(s, channel, "KICKSO")
			meta.kick(s, nick, channel, t)
		elif len(text) > 30:
			meta.sendMsg(s, channel, "DONTDOITAGAINSO")
			meta.kick(s, nick, channel, t)
			
			
		if random.randint(1, channel.lower() == "#lingubender" and 3 or 7) == 1 or len(text) > 6:
			k = True
			t = "KICKSO"
		elif nick.lower() == "tan":
			t = "TANSO"
			
			
		meta.sendMsg(s, channel, "%s%s%s"%(a.group(1)*2,a.group(2)*2,a.group(3)*2))
		Timer(1, lambda: meta.sendMsg(s, channel, "%s%s%s"%(a.group(1)*3,a.group(2)*3,a.group(3)*3))).start()
		Timer(2, lambda: meta.sendMsg(s, channel, "%s%s%s"%(a.group(1)*4,a.group(2)*4,a.group(3)*4))).start()
		if k:
			Timer(3, lambda: meta.sendMsg(s, channel, t)).start()
			Timer(4, lambda: meta.kick(s, nick, channel, t)).start()
		else:
			Timer(3, lambda: meta.sendMsg(s, channel, t)).start()
		return False
	
	return True
	