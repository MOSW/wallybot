## Copyright 2009-2012 Joey
## 
## Jobot is released under Affero GPL. Please read the license before continuing.
## 
## The latest source can be found here:
##	 https://github.com/MOSW/wallybot
##
import meta
import time
import random
import re
import threading

random.seed()

if 'awkward' not in meta.conf:
	meta.conf['awkward'] = False

if 'awkward_channel' not in meta.conf:
	meta.conf['awkward_channel'] = []
else:
	meta.conf['awkward_channel'] = meta.conf['awkward_channel'].split()


channels = {}
awkward_pause = (
	("action",	"whistles innocently.."),
	("msg",		"brb, gonna go get some coffee"),
	("msg",		"*cough*"),
	("action",	"sighs..")
	)
awkward_question = (
	("msg",		"[Awkward Silence]"),
	("msg", 	"[...]"),
	("action",	"whistles innocently.."),
	("msg",		"*cough*"),
	("msg",		"umm...")
	)
	
def msg(s, nick, ident, host, channel, text):
	
	
	
	if not meta.conf['awkward']:
		return True
	
	if nick == meta.conf['nick']:
		return True
	
	
	if nick in meta.conf['ignore'] or host in meta.conf['ignorehost']:
		return False
	
	
	if channel == meta.conf['nick']:
		channel = nick
	
	if channel not in meta.conf['awkward_channel']:
		return True
	
	
	if channel not in channels:
		channels[channel] = {"last": {"who":"", "time": 0, "timer": None},
							 "lastQuestion": {"who":"", "time": 0, "timer": None}}
	
	channels[channel]["last"] = {"who": nick, "time": time.time(), "timer": None}
	
		
	# reset the time if the questioner continues something
	if channels[channel]["lastQuestion"]["who"] and nick == channels[channel]["lastQuestion"]["who"]:
		#print("Resetting awkward question timer")
		
		channels[channel]["lastQuestion"]["time"] = time.time()
		
		if channels[channel]["lastQuestion"]["timer"]:
			channels[channel]["lastQuestion"]["timer"].cancel()
			
		channels[channel]["lastQuestion"]["timer"] = threading.Timer(random.randint(60,100), sendAwkwardQ, (s, channel, channels[channel]["lastQuestion"]["who"]))
		channels[channel]["lastQuestion"]["timer"].start()
		channels[channel]["lastQuestion"]["who"] = ""
		
	# if someone responds, reset the whole thing
	elif channels[channel]["lastQuestion"]["timer"]:
		#print("Clearing awkward question timer")
		
		if channels[channel]["lastQuestion"]["timer"]:
			channels[channel]["lastQuestion"]["timer"].cancel()
			
		channels[channel]["lastQuestion"] = {"who":"", "time": 0, "timer": None}
	
	# not always an awkward question.. 
	if not random.randint(0,5):
		if re.search(r"[?!]$", text):
			print("Starting awkward question timer")
			if channels[channel]["lastQuestion"]["timer"]:
				channels[channel]["lastQuestion"]["timer"].cancel()
			channels[channel]["lastQuestion"] = {"who": nick, "time": time.time(), "timer": None}
			channels[channel]["lastQuestion"]["timer"] = threading.Timer(random.randint(60,100), sendAwkwardQ, (s, channel, channels[channel]["lastQuestion"]["who"]))
			channels[channel]["lastQuestion"]["timer"].start()
	
	#if channels[channel]["lastQuestion"]["time"] > 0:
	#	if channels[channel]["lastQuestion"]["time"] < time.time() - random.randint(60,100):
	#		sendAwkwardQ(s, channel, channels[channel]["lastQuestion"]["who"])
	
	
	
	return True
	
def sendAwkwardQ(s, chan, nick):
	agit = random.choice(awkward_question)
	print(agit)
	if agit[0] == "msg":
		meta.sendMsg(s, chan, agit[1].format(nick=nick, chan=chan))
	elif agit[0] == "action":
		meta.sendMsg(s, chan, "\001ACTION "+agit[1].format(nick=nick, chan=chan)+"\001")