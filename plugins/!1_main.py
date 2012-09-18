## Copyright 2009-2011 Joey
##
## This file is part of Jobot.
##
##    Jobot is free software: you can redistribute it and/or modify
##    it under the terms of the GNU Affero General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    Jobot is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU Affero General Public License for more details.
##
##    You should have received a copy of the GNU Affero General Public License
##    along with Jobot.  If not, see <http://www.gnu.org/licenses/>.
##

import meta
import re
import sys
import os
import PorterStemmer #http://tartarus.org/~martin/PorterStemmer/python.txt
import traceback
import pickle
import decimal
import threading




if __name__ == "__main__":
	input("You opened the wrong file. This one can not run by itself.")
	sys.exit()


if 'nick' not in meta.conf:
	meta.conf['nick'] = "Jobot"
if 'pass' not in meta.conf:
	meta.conf['pass'] = False
if 'ident' not in meta.conf:
	meta.conf['ident'] = "Jobot_bot"
if 'realname' not in meta.conf:
	meta.conf['realname'] = "Joey"
if 'channel' not in meta.conf:
	meta.conf['channel'] = "#"+meta.conf['nick']
if 'debug' not in meta.conf:
	meta.conf['debug'] = False

if 'source' not in meta.conf:
	meta.conf['source'] = "https://github.com/jvq2/Jobot"
	
if 'autovoice' not in meta.conf:
	meta.conf['autovoice'] = False
if 'auth' not in meta.conf:
	meta.conf['auth'] = "p48a_qui956~"


try: stemmer
except: stemmer = None

try: flyingPigs
except: flyingPigs = []
try: replaceables
except: replaceables = []


def init(s):
	global stemmer, replaceables, flyingPigs
	
	stemmer = PorterStemmer.PorterStemmer()
	
	loadReplaceables()
	
	meta.loadMuteTimers()
	
	return
	
	
def shutdown():
	print('!1_main.py def shutdown')
	
	if meta.restart:
		# there is no return from this...
		print('starting new process...')
		os.execvp('python3', ['python3', './jobot.py'])
	return


def handle(s, nick, ident, host, cmd, data):


	if cmd == "PING":
		meta.send(s, "PONG %s\r\n" % data)
		return True
	
	
	
	elif cmd == "001":
		if meta.conf['pass']:
			print("Sending NickServ Password\n")
			meta.sendMsg(s, "NickServ", "IDENTIFY %s" % meta.conf['pass'])
		
		print("Joining Channel %s\n" % meta.conf['channel'])
		meta.send(s, "MODE %s +B\r\nJOIN %s\r\nUSERHOST %s\r\n" % (meta.conf['nick'], meta.conf['channel'], meta.conf['ident']))
		
		return True
		
		
		
		
	elif cmd == "353":
		# Create our user list on channel join (353: user list)
		#print(data)
		
		listStart = data.find(':')
		
		cfind = data.find('=')
		if cfind == -1:
			#secret
			cfind = data.find('*')
			if cfind == -1:
				#private
				cfind = data.find('@')
		
		channel = data[cfind+2 : listStart-1]
		userlist = data[listStart+1 :].split()
		
		
		#print("userlist:",userlist)
		
		for u in userlist:
			#print(u)
			if u[0] == '&':
				user = u[1 :]
				meta.users[channel][user] = meta.User(user, channel, ident, host)
				meta.users[channel][user].protected = True
				
			elif u[0] == '~':
				user = u[1 :]
				meta.users[channel][user] = meta.User(user, channel, ident, host)
				meta.users[channel][user].owner = True
				
			elif u[0] == '@':
				user = u[1 :]
				meta.users[channel][user] = meta.User(user, channel, ident, host)
				meta.users[channel][user].op = True
				
			elif u[0] == '%':
				user = u[1 :]
				meta.users[channel][user] = meta.User(user, channel, ident, host)
				meta.users[channel][user].halfOp = True
				
			elif u[0] == '+':
				user = u[1 :]
				meta.users[channel][user] = meta.User(user, channel, ident, host)
				meta.users[channel][user].voice = True
				
			else:
				#print("channel:", channel)
				#print("U:", u)
				meta.users[channel][u] = meta.User(u, channel, ident, host)
				
			
		meta.parseMuteTimers(s, channel)
		
	
	
	elif cmd == "MODE":
		#return True
		mode = data.split()
		
		if len(mode) < 3:
			return True
		
		print(nick, ident, mode)
		channel = mode[0]
		user = mode[2]
		mode = mode[1]
		
		if not meta.isUser(channel, user):
			return True
		
		add = True
		for char in mode:
			if char == "+": add = True
			elif char == "-": add = False
			elif char == "v":
				if add: 
					meta.users[channel][user].voice = True
					#clears mute timers
					meta.users[channel][user].unmute(s)
					#take them off the pig watch list (mute until list)
					removePig(user, channel)
				else:
					meta.users[channel][user].voice = False
			elif char == "o":
				if add: meta.users[channel][user].op = True
				else: meta.users[channel][user].op = False
			elif char == "a":
				if add: meta.users[channel][user].protected = True
				else: meta.users[channel][user].protected = False
			elif char == "h":
				if add: meta.users[channel][user].halfOp = True
				else: meta.users[channel][user].halfOp = False
			elif char == "q":
				if add: meta.users[channel][user].owner = True
				else: meta.users[channel][user].owner = False
		
		
		
		
		return True
	
	
	elif cmd == "KICK":
		# remove the user from our list when they are kicked
		kick = data.split()
		
		if meta.isUser(kick[0], kick[1]):
			del meta.users[kick[0]][kick[1]]
		
		removePig(kick[1], kick[0])
		return True
	
	
	
	elif cmd == "JOIN":
		channel = data[1 :]
		if nick == meta.conf['nick']:
			#:Jobot!Jobot_bot@hide-54ECEB19.tampabay.res.rr.com JOIN :#joey
			#when jobot joins a channel, add that channel to its list
			meta.users[ channel ] = dict()
			meta.send(s, "WHO {0}\r\n".format(channel))
		else:
			#:Azaghal!foo@20D0CA34.378255A6.27CBF2F8.IP JOIN :#xkcd
			meta.users[channel][nick] = meta.User(nick, channel, ident, host)
			
			# mute the person if wally has a timer ready and waiting for them
			muted = meta.parseMuteTimers(s, channel, nick)
			
			# dont autovoice if they are on a mute timer
			if not muted and meta.conf['autovoice']:# and meta.canMute(channel, meta.conf['nick']) and meta.conf['autovoice']:
				meta.users[channel][nick].unmute(s)
			
			
			if nick not in meta.userInfo:
				meta.userInfo[nick] = {}
			meta.userInfo[nick]["ident"] = ident
			meta.userInfo[nick]["host"] = host
		return True
	
	
	elif cmd == "PART":
		
		meta.delUser(data, nick)
		
		removePig(nick, data)
		return True
	
	
	# WHO #channel reply
	#:colobus.foonetic.net 352 Joey #xkcd-robotics ~Jobot hide-54ECEB19.tampabay.res.rr.com colobus.foonetic.net wally HrB% :0 Joey
	#:colobus.foonetic.net 352 Joey #xkcd-robotics ~Joey hide-54ECEB19.tampabay.res.rr.com colobus.foonetic.net Joey Hr& :0 Joey
	elif cmd == "352":
		x = data.split()
		if x[5] not in meta.userInfo:
			meta.userInfo[x[5]] = {}
		meta.userInfo[x[5]]["ident"] = x[2]
		meta.userInfo[x[5]]["host"] = x[3]
		meta.userInfo[x[5]]["server"] = x[4]
		meta.userInfo[x[5]]["realname"] = x[8]
		return True
	
	
	# Handle nick changes. No channel is given because nicks are unique for that server.
	elif cmd == "NICK":
		for channel in meta.users.keys():
			if nick in meta.users[channel]:
				meta.users[channel][data[1:]] = meta.users[channel][nick]
				del meta.users[channel][nick]
				
				piggy = findPig(nick, channel)
				if piggy:
					removePig(nick, channel)
					groundPig(data[1:], channel, piggy[2], piggy[3])
				
				m = meta.delMuteTimer(nick, channel)
				if m:
					meta.saveMuteTimers(*m)
		return True
	
	
	elif cmd == "QUIT":
		#:Kokuma!~foo@20D0CA34.378255A6.27CBF2F8.IP QUIT :Ping timeout
		for channel in meta.users.keys():
			if nick in meta.users[channel]:
				del meta.users[channel][nick]
		
		removePig(nick, channel)
		
		return True
	
	


	
#def notice(s, nick, ident, host, sender, text):
#	textUpper = text.upper()
#	
#	if textUpper[: 4] == 'DIE':
#		if meta.isProtected(sender, nick) or text[5 :].lstrip() == meta.conf['pass']:
#			meta.quit = True
#		
#	#elif text.find('HELP') == 0 :
#	#	for line in meta.help:
#	#		meta.sendNotice(s, nick, line)
#	
#	elif textUpper[: 7] == "RELOAD ":
#		moduleName = text[7 :]
#		print(moduleName)
#		



def msg(s, nick, ident, host, channel, text):
	
	
	
	#print(channel)
	#no channel specific commands in private chat
	if channel == meta.conf['nick']:
		inChannel = False
		channel = nick
	else:
		inChannel = True
		
	
	if nick in meta.conf['ignore'] or host in meta.conf['ignorehost']:
		return False
	
	
	checkPigs(s, nick, channel, text)
	
	
	print(channel+":", nick,"|",text)
	
	
	
	if not re.match(r"wally[,:] ", text, re.I):
		return True
	
	if channel in meta.LOUD and not re.match(r"bitch[,:] ", text, re.I):
		return True
	
	
	text = text[7 :]
	textLower = text.lower()
	
	#print("In !1_main msg func", meta.canMute(channel, nick), inChannel)
	
	if textLower == "you there?":
		meta.sendMsg(s, channel, "yes")
		return True
	
	elif textLower[: 5] == "mute " and meta.canMute(channel, nick) and inChannel:
		#mute Joey until pigs fly
		#mute Joey until hell freezes over
		#mute Joey until ...your mom
		
		
		
		userEnd = text.find(' ', 5)
		
		#print("In mute", userEnd)
		
		if userEnd > 0:
			user = text[5 : userEnd]
			params = textLower[userEnd+1 :]
			
			# mute me 1m
			# mute me until pigs fly
			if user.lower() == 'me':
				user = nick
			
			if params[:6] == 'until ' or params[:4] == 'til ':
				if params[:4] == 'til ':
					params = params[4:]
				else:
					params = params[6:]
				
				# improper syntax
				if not params:
					meta.sendMsg(s, channel, "Until when? Finish your statements...")
					return False
				
				try:
					# add the user to the 'muted until' list
					stemmed = groundPigs(user, channel, params, nick)
				except:
					traceback.print_exc()
					input()
				
				print("Muting", user, "until", stemmed)
				
				c, u = meta.isUser(channel, user)
				if c and u:
					meta.users[c][u].mute( s )
				else:
					print(user, 'is not a user')
					meta.sendMsg(s, channel, "Mute who?")
					
				return False
			
			if not re.match(r"\d+[smhdwyc]?", params):
				return True
			
			if params[-1:] == 's':#seconds
				muteTime = float(params[ :-1])
			elif params[-1:] == 'm':#minutes
				muteTime = float(params[ :-1]) * 60
			elif params[-1:] == 'h':#hours
				muteTime = float(params[ :-1]) * 3600
			elif params[-1:] == 'd':#days
				muteTime = float(params[ :-1]) * 86400
			elif params[-1:] == 'w':#weeks
				muteTime = float(params[ :-1]) * 604800
			elif params[-1:] == 'y':#years
				muteTime = float(params[ :-1]) * 31556926
			elif params[-1:] == 'c':#Centuries
				muteTime = float(params[ :-1]) * 3155692600
			else:
				muteTime = float(params) #seconds
			
		else:
			user = text[5 :]
			
			if user.lower() == 'me':
				user = nick
			
			muteTime = 0
			
		c, u = meta.isUser(channel, user)
		if c and u:
			print("Muting", u, muteTime)
			meta.users[c][u].mute( s, muteTime )
		else:
			print(user, 'is not a user')
			meta.sendMsg(s, channel, "Mute who?")
			
		return False
		
		
	elif textLower.find('unmute ') == 0 and meta.canMute(channel, nick) and inChannel:
		user = text[7 :]
		
		if user.lower() == 'me':
			user = nick
			
		c, u = meta.isUser(channel, user)
		if c and u:
			meta.users[c][u].unmute(s)
			removePig(u, channel)
			#print("Unmuting", u)
		else:
			meta.sendMsg(s, channel, "Unmute who?")
		return False
		
	elif textLower.find('ban ') == 0:
		if not inChannel: return False
		
		if not meta.canBan(channel, nick):
			meta.sendMsg(s, channel, "%s: You do not have the power!" % nick)
			return False
			
		if not meta.canBan(channel, meta.conf['nick']):
			#meta.sendMsg(s, channel, "%s: I do not have the power!" % nick)
			return True
			
		
		r = re.match(r"ban\s+([^\s]+)\s*(?:(?:for\s+)?(.*?))?[!.?]*$", textLower)
		
		if not r:
			meta.sendMsg(s, channel, "%s: Invalid syntax." % nick)
			return False
		
		user, timeStr = r.groups()
		
		c, user = meta.isUser(channel, user)
		
		if not user:
			meta.sendMsg(s, channel, "%s: ban who?" % nick)
			return False
		
		x = meta.userInfo[user]
		
		length = timeOffset(timeStr)
		
		if not timeStr or (length and length < 0):
			meta.ban(s, channel, host=x['host'])
			return False
		
		elif not length:
			meta.sendMsg(s, channel, "%s: Invalid time." % nick)
			return False
		
		
		meta.timedBan(s, channel, length, host=x['host'])
		
		#meta.sendMsg(s, channel, "%s, You are awarded one tricky-dick-fun-bill for finding an undocumented unfinished feature!"%nick)
		return False
	
	elif textLower.find('unban ') == 0:
		if not inChannel: return False
		
		if not meta.canBan(channel, nick):
			meta.sendMsg(s, channel, "%s: You do not have the power!" % nick)
			return False
			
		if not meta.canBan(channel, meta.conf['nick']):
			#meta.sendMsg(s, channel, "%s: I do not have the power!" % nick)
			return True
		
		r = re.match(r"unban\s+([^\s]+?)[!.?\s]*$", textLower)
		
		if not r:
			meta.sendMsg(s, channel, "%s: Invalid syntax." % nick)
			return False
		
		(user,) = r.groups()
		
		c, user = meta.isUser(channel, user)
		
		if not user:
			meta.sendMsg(s, channel, "%s: unban who?" % nick)
			return False
		
		x = meta.userInfo[user]
		
		banmask = meta.unban(s, channel, host=x['host'])
		
		return False
	elif False and textLower == 'be loud' and ((inChannel and meta.canMute(channel, nick)) or not inChannel):
		while channel in meta.LOUD:
			meta.LOUD.remove(channel)
		meta.LOUD.append(channel)
		
		meta.sendMsg(s, channel, "%s: Ok."%nick)
		return False
		
	elif False and (textLower == 'not so loud' or textLower == 'be cool') and \
		((inChannel and meta.canMute(channel, nick)) or not inChannel):
		if channel in meta.LOUD:
			meta.LOUD.remove(channel)
			meta.sendMsg(s, channel, "%s: Ok."%nick)
			return False
			
		
	elif (textLower == 'restart' or textLower == 'reboot') and meta.isAuthor(nick, ident, host):
		meta.quit = True
		meta.restart = True
		return False
		
	elif (textLower == 'quit' or textLower == 'exit') and meta.isAuthor(nick, ident, host):
		meta.quit = True
		return False







def groundPigs(user, channel, until, muter=None):
	global flyingPigs
	says = None
	
	until = until.strip().lower().split()
	
	len_until = len(until)
	
	if len_until > 2 and until[1] == 'says':
		c, u = isUser(channel, until[0])
		
		if u:
			says = u
			until = until[2:]
		
		
	elif len_until > 2 and until[0] == 'i' and until[1] == 'say':
		says = muter
		until = until[2:]
	
	
	until = stemList(stripPunctList(until))
	
	
	# find words that are in the replaceable list and insert that list instead
	for i, word in enumerate(until):
		x = getReplaceables(word)
		if x:
			until[i] = x
	
	
	#remove the user from the list if they are already in it
	removePig(user, channel)
	
	flyingPigs.append((user, channel, says, until))
	
	return until


def findPig(user, channel):
	for pig in flyingPigs:
		if pig[0] != user or pig[1] != channel:
			return pig



def removePig(user, channel):
	for n, pig in enumerate(flyingPigs):
		if pig[0] == user and pig[1] == channel:
			del flyingPigs[n]
			break

def checkPigs(s, nick, channel, text):
	words = stemPhrase(text)
	#print("Words:", words)
	
	##:: Pig Format ::
	##
	## [0]   [1]      [2]   [3]
	## nick, channel, says, words
	## |     |        |     ^ (find all theses items; if that item is a list,
	## |     |        |     ^  then we only need to find one of the items in
	## |     |        |     ^  that list)
	## |     |        ^ (who needs to say all those words)
	## |     ^ (must act only on phrases in the channel it was created)
	## ^ (this is who we unmute when we find the phrase)
	
	
	# for each user muted that is in the channel in question
	for pig in flyingPigs:
		if pig[1] != channel: continue
		if pig[2] and nick != pig[2]: continue
		
		Unmute = True
		
		# check to see if all the keywords are in the sentance
		for word in pig[3]:
			
			if type(word) == list:
				win = False
				for w in word:
					if w in words:
						win = True
						break
				if not win:
					Unmute = False
				
			elif word not in words:
				Unmute = False
				#print(word, "not in words")
				break
			
		
		if Unmute:
			#print("unmute")
			#print(meta.users[channel])
			channel, nick = meta.isUser(channel, pig[0])
			if channel and nick:
				#print("Unmuting:", nick, "on", channel)
				meta.users[channel][nick].unmute(s)
				removePig(nick, channel)
			
		
	

def stemList(list):
	stemmed = []
	
	# stem all the words to find the root word
	for word in list:
		stemmed.append(stemmer.stem(word, 0, len(word)-1))
		
	return stemmed
	

def stemPhrase(phrase):
	return stemList(stripPunctList(phrase.strip().lower().split()))
	
	
	

def stripPunctList(pList):
	newList = []
	for item in pList:
		stripped = item.strip(",./<>?;:'\"[]{}\\|`~!@#$%^&*()-_=+")
		if stripped:
			newList.append(stripped)
	return newList
	
	
def loadReplaceables():
	global replaceables
	
	try:
		rf = open('replaceable.list','rb')
		
		replaceables = pickle.load(rf)
		
		rf.close()
	except:
		print('Unable to load replaceable lists!')
		traceback.print_exc()


def getReplaceables(word):
	for wordlist in replaceables:
		if word in wordlist: return wordlist
	
	return None
	
	
	
	
	
def notice(s, sender, ident, host, channel, text):
	
	# Don't parse anything from nick or chan server. They wont be telling us
	# to do things.
	senderLower = sender.lower()
	if senderLower == 'chanserv' or senderLower == 'nickserv':
		return True
	
	authd = meta.isAuthor(sender, ident, host)
	
	textLower = text.lower()
	
	if textLower.find('join ') == 0 and authd:
		meta.send(s, "JOIN %s\r\n" % textLower[5:].strip())
		return False
	
	elif textLower.find('part ') == 0 and authd:
		meta.send(s, "PART %s\r\n" % textLower[5:].strip())
		return False
	
	elif textLower.find('nick ') == 0 and authd:
		meta.send(s, "NICK %s\r\n" % text[5:].strip())
		meta.conf['nick'] = text[5:].strip()
		return False
	
	elif textLower.find('nickpass ') == 0 and authd:
		meta.sendMsg(s, "NickServ", "IDENTIFY %s" % textLower[9:].strip())
		return False
	
	elif textLower.find('reload ') == 0 and authd:
		print("Reloading Module:", textLower[7:].strip())
		meta.reload.append(textLower[7:].strip())
		return False
		
	elif textLower.find('test ') == 0 and authd:
		meta.sendMsg(s, "Joey", "asdf1456")
		return False
		
	elif textLower.find('raw ') == 0 and authd:
		meta.send(s, "%s\r\n" % textLower[4:])
		return False
	
	elif textLower.find('msg ') == 0 and authd:
		rest = text[4:].strip()
		x = rest.find(' ')
		if not x: return False
		meta.sendMsg(s, rest[:x].rstrip(), rest[x+1:].lstrip())
		return False
		params = text[4:].strip().split()
		if len(params) < 2: return False
		meta.sendMsg(s, params[0], text[4+strlen(params[0]):].strip())
		return False
		
	
	elif textLower.find('notice ') == 0 and authd:
		rest = text[4:].strip()
		x = rest.find(' ')
		if not x: return False
		meta.sendMsg(s, rest[:x].rstrip(), rest[x+1:].lstrip())
		return False
		params = text[7:].strip().split()
		if len(params) < 2: return False
		meta.sendMsg(s, params[0], text[4+strlen(params[0]):].strip())
		return False
		
	elif textLower == 'mode?':
		if meta.conf['autovoice']:
			meta.sendNotice(s, sender, "Mode: AutoVoice is On.")
		else:
			meta.sendNotice(s, sender, "Mode: AutoVoice is Off.")
		# continue through to the other modules.
		# This command should return all the modules state to the requesting
		# user.
		return True
	
	noBlock = True
	
	# break down our text into commands to be processed by 
	cmds = text.split()
	while(cmds):
		#print(cmds[0])
		
		if cmds[0] == '-autovoice' and authd:
			if not meta.conf['autovoice']:
				meta.sendNotice(s, sender, "Confirm - AutoVoice is already Off.")
			else:
				meta.sendNotice(s, sender, "Confirm - AutoVoice is now Off.")
				meta.conf['autovoice'] = False
			noBlock = False
			
		elif cmds[0] == '+autovoice' and authd:
			if meta.conf['autovoice']:
				meta.sendNotice(s, sender, "Confirm - AutoVoice is already On.")
			else:
				meta.sendNotice(s, sender, "Confirm - AutoVoice is now On.")
				meta.conf['autovoice'] = True
			noBlock = False
			
		elif cmds[0] == '+auth':
			# This command takes 1 parameter that should immediatly follow it.
			# pop off the current command (+auth) so that we can grab the pass
			cmds.pop(0)
			
			# grab the pass
			upass = cmds[0]
			
			if upass == meta.conf['auth']:
				# save the authors exact identity
				meta.setAuthor(sender, ident, host)
				
				meta.sendNotice(s, sender, "Confirm - You are now Authorized.")
				print(sender, "is now authorized.")
				
				# set the local authorized variable so that the user is
				# authorized for the rest of the commands.
				authd = True
				
				# no other modules should ever get their hands on the password
				noBlock = False
			else:
				print("FAILED AUTHORIZATION BY", sender, ident, host)
			
		elif cmds[0] == '-auth':
			if authd:
				# un auth the sender
				meta.unsetAuthor()
				
				meta.sendNotice(s, sender, "Confirm - Authorization Removed.")
				print(sender, "has been deauthorized.")
				
				noBlock = False
			else:
				print("FAILED DEAUTH BY", sender, ident, host)
				
		elif cmds[0] == '+loud' and authd:
			if meta.conf['loud']:
				meta.sendNotice(s, sender, "CONFIRM - I WAS ALREADY REALLY REALLY ANNOYING.")
			else:
				meta.conf['loud'] = True
				meta.sendNotice(s, sender, "CONFIRM - I AM NOW REALLY REALLY ANNOYING.")
		elif cmds[0] == '-loud' and authd:
			if not meta.conf['loud']:
				meta.sendNotice(s, sender, "Confirm - Loud was already Off.")
			else:
				meta.conf['loud'] = False;
				meta.sendNotice(s, sender, "Confirm - Loud is now Off.")
				
		elif cmds[0] == '+tenso' and authd:
			if meta.conf['tenso']:
				meta.sendNotice(s, sender, "CONFIRM - TENSO was already On.")
			else:
				meta.conf['tenso'] = True
				meta.sendNotice(s, sender, "CONFIRM - TENSO")
		elif cmds[0] == '-tenso' and authd:
			if not meta.conf['tenso']:
				meta.sendNotice(s, sender, "Confirm - TENSO was already Off.")
			else:
				meta.conf['tenso'] = False;
				meta.sendNotice(s, sender, "Confirm - TENSO is now Off.")
			
		#elif cmds[0] == '+reload' and authd:
		#	cmds.pop(0)
		#	print("trying to reload:", cmds[0])
		#	print(__main__.__dict__)
		#	for plugin in __main__.plugins:
		#		print(" plugin:", plugin.__name__)
		#		if plugin.__name__ == cmds[0]:
		#			plugin = imp.reload(plugin)
		#			break
			
		elif cmds[0] == '-quit' and authd:
			meta.quit = True
			noBlock = False
			
		elif cmds[0] == '-restart' and authd:
			meta.quit = True
			meta.restart = True
			noBlock = False
		
		
		# if the first command fails dont continue trying to process commands
		# This is useful in situations where the notice is something like a 
		# talk command and this module shouldn't process anything in that
		# message.
		if noBlock: return True
		
		# pop the old command that we just worked on, off the queue
		cmds.pop(0)
		
	return noBlock
	
	
	
	
	
tOffRepTable = (
	(r"s(?:ec(?:onds?)?)?$", "second"),
	(r"m(?:in(?:utes?)?)?$", "minute"),
	(r"h(?:ours?)?$", "hour"),
	(r"d(?:ays?)?$", "day"),
	(r"w(?:eeks?)?$", "week"),
	(r"f(?:ortnights?)?$", "fortnight"),
	(r"m(?:onths?)?$", "month"),
	(r"y(?:ears?)?$", "year"),
	(r"dec(?:ades?)?$", "decade"),
	(r"scores?$", "score"),
	(r"cen(?:tur(?:y|ie)s?)?$", "century"),
	(r"mil(?:lennium)?$", "millennium"),
	(r"(?:a|a?eons?)$", "aeon")
			)
	
tOffUnitSecs = (
	("second", 1),
	("minute", 60),
	("hour", 3600),
	("day", 86400),
	("week", 604800),
	("fortnight", 1209600),
	("month", 2592000),
	("year", 31536000),
	("decade", 315360000),
	("score", 630720000),
	("century", 3153600000),
	("millennium", 31536000000),
	("aeon", 31536000000000000)
			)
	
tOffUnitPlurals = (
	("second", "seconds"),
	("minute", "minutes"),
	("hour", "hours"),
	("day", "days"),
	("week", "weeks"),
	("fortnight", "fortnights"),
	("month", "months"),
	("year", "years"),
	("decade", "decades"),
	("score", "score"),
	("century", "centuries"),
	("millennium", "millennium"),
	("aeon", "aeons")
			)

def timeOffset(str):
	timeList = getTimeList(str)
	print(timeList)
	if not timeList: return None
	
	secs = calcSeconds(timeList)
	print(secs)
	return secs
	
	
def calcSeconds(timeList):
	secs = decimal.Decimal(0)
	
	for (val, unit) in timeList:
		secs = secs + (getUnitSecs(unit) * val)
	
	return secs
	
	
def getUnitSecs(unit):
	for (x, secs) in tOffUnitSecs:
		if x == unit: return secs
	
	
def getTimeList(str):
	str = str.lower().strip()
	#re.findall(r"([0-9]+)\s?([a-z ]*)(?:\sand)?", str)
	#a = re.findall(r"\s?([0-9.]+)\s?([a-z]*)(?:\sand)?\s?", "0 days and 5 hours")
	
	defaultUnit = "minute"
	defaultVal = 3
	timeList = []
	
	#tList = re.split(r"(\d+|\w+)",)
	
	for x in re.split(r"(\d+|\w+)", str):
		x = x.strip(' .,?!')
		if not x: continue
		
		# catch the numbers (can be decimals)
		if re.match(r"^-?(?:\d+(?:\.\d+|\.)?|\.\d+)$", x):
			timeList.append( [decimal.Decimal(x), None] )
			continue
		
		# Ignore me..
		elif x == "and": 
			continue
		
		
		# Gimme my time unit!
		unit = getUnitRep(x)
		print(x, unit)
		# getUnitRep returns None when the unit does not exist
		if not unit: return None
		
		# create an empty item if the list is empty or the last unit is set
		if not timeList or timeList[-1][1] is not None:
			timeList.append( [None, None] )
		
		timeList[-1][1] = unit
	
	
	# set default values
	for i in range(len(timeList)):
		if timeList[i][0] == None:
			timeList[i][0] = defaultVal
		
		if timeList[i][1] == None:
			timeList[i][1] = defaultUnit
	
	
	return timeList
	

def getUnitRep(str):
	for (pattern, unit) in tOffRepTable:
		if re.match(pattern, str):
			return unit
	return None

