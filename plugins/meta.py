import sys
import threading
import time
import random
import pickle
import traceback


if __name__ == "__main__":
	input("You opened the wrong file. This one can not run by itself.")
	sys.exit()

"""try: conf
except: conf = {}
try: settings
except: settings = {}
try: users
except: users = {}
try: channels
except: channels = {}
try: help
except: help = [" - Jobot Help - "]
try: quit
except: quit = False
try: restart
except: restart = False
try: con
except: con = None
try: nick
except: nick = "Jobot"
try: userInfo
except: userInfo = {}
try: reload
except: reload = []

try: Author
except: Author = ()

try: muteTimers
except: muteTimers = []
try: banTimers
except: banTimers = []"""



try: unknownCmdReplys
except: unknownCmdReplys = [
	"{nick}, huh?", 
	"I don't quite follow...", 
	"{nick}: what?", 
	"{nick}: I don't get it...",
	"{nick}: ???"
	]





#try:
#	la = open('action.log', 'ta', buffering=1)
#except:
#	print('Could not open action log.')




def init(s):
	global conf, settings, users, channels, help, quit, restart, con, nick, userInfo, reload, Author, muteTimers, banTimers
	conf = {}
	settings = {}
	users = {}
	channels = {}
	help = [" - Jobot Help - "]
	quit = False
	restart = False
	con = None
	nick = "Jobot"
	userInfo = {}
	reload = []

	Author = ()

	muteTimers = []
	banTimers = []
	
	
	try:
		Fconf = open("bot.conf","r")
	except:
		input('Configuration not found. Press [enter] to exit.')
		sys.exit()
	else:
		for line in Fconf:
			nameEnd = line.find('=')
			
			if nameEnd != -1:
				property = line[: nameEnd].strip().lower()
				value = line[nameEnd+1 :].strip()
				
				if value.lower() == "true":
					conf[property] = True
				elif value.lower() == "false":
					conf[property] = False
				else:
					conf[property] = value
				

	return





try: LOUD
except: LOUD = []

def send(s, data):
	#s.write(bytes(data, "ascii"))
	s.send(bytes(data, "ascii"))
	
def sendMsg(s, to, text):
	if to in LOUD: send(s, "PRIVMSG %s :%s\r\n" % (to, text.upper()))
	else: send(s, "PRIVMSG %s :%s\r\n" % (to, text))
	
	
def sendNotice(s, to, text):
	send(s, "NOTICE %s :%s\r\n" % (to, text))

"""	
def send(s, data, delay):
	s.send(bytes(data, "ascii"))
	
def sendMsg(s, to, text, delay):
	if to in LOUD: send(s, "PRIVMSG %s :%s\r\n" % (to, text.upper()), delay)
	else: send(s, "PRIVMSG %s :%s\r\n" % (to, text), delay)
	
	
def sendNotice(s, to, text, delay):
	send(s, "NOTICE %s :%s\r\n" % (to, text), delay)"""
	
	
def close(s = None):
	#la.close()
	pass
	


	
"""def isChannel(channel):
	if channel in users: return True
	return False"""

# rewritten to be case insensitive
def isChannel(channel):
	channel = channel.lower()
	
	for key in users.keys():
		if key.lower() == channel:
			return key
		
	return False

"""def isUser(channel, nick):
	if isChannel(channel) and nick in users[channel]:
		return True
	else:
		return False"""

# rewritten to be case insensitive
def isUser(channel, nick):
	channel = isChannel(channel)
	if not channel: return (None, None)
	
	nick = nick.lower()
	
	for key in users[channel].keys():
		if key.lower() == nick:
			return (channel, key)
		
	return (channel, None)


def delUser(channel, nick):
	c, u = isUser(channel, nick)
	if c and u:
		del users[c][u]
		return True
	else:
		return False



def user(nick, channel):
	c = None
	channel = channel.lower()
	
	for key, value in users.items():
		if key.lower() == channel:
			c = value
			break
	
	if not c: return None
	
	nick = nick.lower()
	
	for key, value in c.items():
		if key.lower() == nick:
			return value
	
	return None
	

	
def isOp(channel, nick):
	if isUser(channel, nick):
		return users[channel][nick].op
	else:
		return False
		
def isHalfOp(channel, nick):
	if isUser(channel, nick):
		return users[channel][nick].halfOp
	else:
		return False

def isProtected(channel, nick):
	if isUser(channel, nick):
		return users[channel][nick].protected
	else:
		return False

def isOwner(channel, nick):
	if isUser(channel, nick):
		return users[channel][nick].owner
	else:
		return False


def isAuthor(*auth):
	return (auth == Author)

# place holder: more advanced authorization might require this function
def unsetAuthor():
	# if we dont declare Author as a global here, it will set it as if it were
	# being used as a local
	global Author
	Author = ()

# place holder: more advanced authorization might require this function
def setAuthor(*auth):
	global Author
	Author = auth

	
	
	
def hasVoice(channel, nick):
	if isUser(channel, nick):
		return users[channel][nick].voice
	else:
		return False
	
def canMute(channel, nick):
	if isOp(channel, nick) or isHalfOp(channel, nick) or isProtected(channel, nick) or isOwner(channel, nick):
		return True
	else:
		return False

canVoice = canMute
canBan = canMute


def randomUser(channel=None):
	if channel and isChannel(channel):
		return random.choice( list(users[channel].values()) )
	else:
		return random.choice( list(users[random.choice( list(users.keys()) )].values()) )




def loadMuteTimers():
	global muteTimers
	
	try:
		mf = open('muteTimers','rb')
		
		muteTimers = pickle.load(mf)
		print("Mute Timers:\n", muteTimers, "\n")
		mf.close()
	
	except:
		print('Could not load mute timers!')
		#traceback.print_exc()
	
	
def parseMuteTimers(s, channel, nick=None):
	delete = []
	for i, timer in enumerate(muteTimers):
		print(timer)
		if timer[1] != channel: continue
		if nick and timer[0] != nick: continue
		
		if timer[2] + timer[3] <= time.time():
			delete.append(i)
			print('delete:', timer)
			continue
		
		
		
		c, u = isUser(timer[1], timer[0])
		print(u, time.time() - timer[2] + timer[3])
		if c and u:
			user(u, c).mute(s, time.time() - timer[2] + timer[3], True)
			if nick: return True
	
	# the id of each item decreases by one every time an item is deleted
	deleted = 0
	for d in delete:
		del muteTimers[d-deleted]
		deleted -= 1
		
	if deleted:
		saveMuteTimers()
	
	if nick: return False
	


def saveMuteTimers(user=None, channel=None, started=None, time=None):
	if user:
		muteTimers.append([user, channel, started, time])
		
	try:
		mf = open('muteTimers','wb')
		
		pickle.dump(muteTimers, mf)
		
		mf.close()
		
	except:
		print('Could not save mute timers!')
		#traceback.print_exc()
	

def getMuteTimer(user, channel):
	for timer in muteTimers:
		if timer[0] == user and timer[1] == channel:
			return timer

def delMuteTimer(user, channel):
	for i, timer in enumerate(muteTimers):
		if timer[0] == user and timer[1] == channel:
			return muteTimers.pop(i)



def kick(s, nick, channel, reason=None):
	if reason:
		send(s, "KICK {0} {1} :{2}\r\n".format(channel, nick, reason))
	else:
		send(s, "KICK {0} {1}\r\n".format(channel, nick))




def ban(s, chan, **k):
	mask = userMask(**k)
	
	k['mode'] = 'mode' in k and k['mode'] or '+b'
	
	send(s, "MODE {chan} {mode} {mask}\r\n".format(chan=chan, mask=mask, **k))
	return mask

def unban(s, chan, **k):
	k['mode'] = '-b'
	mask = ban(s, chan, **k)
	
	popBanTimer(chan, mask)[2].cancel()
	return mask

def timedBan(s, chan, time, **k):
	mask = ban(s, chan, **k)
	
	timer = threading.Timer(int(round(time)), unban, args=[s, chan], kwargs=k)
	timer.start()
	
	addBanTimer(chan, mask, timer)
	return (timer, mask)
	
def addBanTimer(chan, mask, timer):
	print(chan)
	print(mask)
	print(timer)
	return banTimers.append((chan, mask, timer))
	
def popBanTimer(chan, mask):
	for n in range(len(banTimers)):
		if banTimers[n][0] == chan and banTimers[n][1] == mask:
			return banTimers.pop(n)
	return None
	

def userMask(**k):
	for a in ['nick', 'ident', 'host']:
		k[a] = a in k and k[a] or '*'
	return "{nick}!{ident}@{host}".format(**k)
	

	

class User():
	def __init__(self, nick, channel, ident, host):
		self.channel = channel
		self.nick = nick
		self.owner = False
		self.protected = False
		self.op = False
		self.halfOp = False
		self.voice = False
		self.muteTimer = None
		self.host = host
		self.ident = ident
		self.conf = dict()
	
	def mute(self, s, length=None, inTimer=None):
		if self.muteTimer:
			#cancel any current mute timer so it can be recreated
			self.muteTimer.cancel()
			
		if length:
			#if there is a mute length, set a mute timer
			self.muteTimer = threading.Timer(length, self.unmute, args=[s])
			self.muteTimer.start()
			
			if not inTimer: 
				saveMuteTimers(self.nick, self.channel, time.time(), length)
		# mute them
		send(s, "MODE %s -v %s\r\n" % (self.channel, self.nick))
		#print("MODE %s -v %s\r\n" % (self.channel, self.nick))
	
	
	def unmute(self, s):
		if not self.voice:
			send(s, "MODE {0} +v {1}\r\n".format(self.channel, self.nick))
			
			print("Unmuting", self.nick, "on", self.channel)
			
		
		delMuteTimer(self.nick, self.channel)
		
		if self.muteTimer:
			self.muteTimer.cancel()
			self.muteTimer = None
		
		
	def kick(self, s, reason=None):
		
		if reason:
			send(s, "KICK {0} {1} :{2}\r\n".format(self.channel, self.nick, reason))
		else:
			send(s, "KICK {0} {1}\r\n".format(self.channel, self.nick))
		
		
	def ban(self, s, time=0):
		pass
		
		
	def unban(self, s):
		pass
	
	
	def kickban(self, s, time=0, reason=None):
		self.ban(s, time)
		self.kick(s, reason)
	
	



	