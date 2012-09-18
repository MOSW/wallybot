## Copyright 2009-2012 Joey
## 
## Jobot is released under Affero GPL. Please read the license before continuing.
## 
## The latest source can be found here:
##	 https://github.com/MOSW/wallybot
##
import meta
import random
import sqlite3
import re
import time
import sys
import hashlib

if __name__ == "__main__":
	input("You opened the wrong file. This one can not run by itself.")
	sys.exit()
	
	
#pickle is not meant for unsecure data.... DO NOT USE IT HERE
#http://127.0.0.1/docs/python-3.0.1/library/re.html
#http://127.0.0.1/docs/python-3.0.1/library/sqlite3.html
#id, inkling, find, verb, reply, nick (creator)

#meta.help.append('[+|-]bucket - Turn bucket on or off. (Op)')


#wally, wally <action> sets mode +oa wally for #ministryofsillywalks


# -- - - - - - - - -     Wally Manual     - - - - - - - - - - --
# -
# - New Factoid:
# -    wally[,:] inkling (is|are|<reply>|<action>|<[verb_here]>) tidbit
# -
# -    :::WARNING::: Always keep in mind that wally will split the phrase at
# -                   'is' and 'are' before standard bracketed verbs!!
# -
# -       Example: wally, purple is a color
# -        :: &Joey: Who in their right mind would paint their car 
# -        ::    flourescent purple?
# -        :: %wally: purple is a color
# -        :: &Joey: Thank you wally, I did not know that.....
# -
# -       <reply>
# -          - Special Verb: When the inkling is found, wally, repeats the
# -            tidbit and only the tidbit.
# -
# -            Example: wally, takes the bucket <reply> GIVE ME THE BUCKET!!
# -
# -       <action>
# -          - Special Verb: Acts like reply, except sending it as 
# -            "\me [tidbit]".
# -
# -            Example: wally, kick something <action> kicks the bucket.
# -
# -       <[verb_here]>
# -          - Can be any verb surrounded by <>.
# -
# -            Example: wally, I think someone <stole> mah bucket!
# -
# -       Notes:
# -          - Do NOT make wally reply to things that are:
# -                |- too common - Ex: "lol"
# -                |- nicks - Ex: Kris
# -          - Try not to use vulgarity/cussing in replies unless he would be
# -            replying to vulgarity/cussing said by someone else.
# -          - Putting /me in the beginning of the inkling makes wally only
# -            match actions.
# -          - Commands and verbs can be escaped by placing a backslash ('\')
# -            in front of them.
# -          - All instances of who* in the tidbit will be replaced with the
# -            nick of the user that triggered it.
# -          - All instances of someone* in the tidbit will be replaced with
# -            a random nick of someone in the channel.
# -          - All instances of chan* in the tidbit will be replaced with the
# -            name of the channel in which it was triggered.
# -          - You can use sentence beginning ('^') and end ('$') identifiers
# -            to make wally check for the inkling at the beginning and/or end
# -            of messages.  Ex: wally, ^yay <reply> I'm so happy for you.
# -                          Ex: wally, omg$ <reply> you say that too often..
# -                          Ex: wally, ^no way$ <reply> I don't believe it either
# -
# -
# - Search:
# -    Syntax:
# -       wally[,:] search [phrase]
# -       wally[,:] search [offset] [phrase]
# -       wally[,:] search[[offset]] [phrase]
# -       wally[,:] search([offset]) [phrase]
# -       wally[,:] search{[offset]} [phrase]
# -
# -    Examples:
# -      :: &Joey: wally, search bucket
# -      :: &Joey: wally, search 5 bucket
# -      :: &Joey: wally, search[12] bucket
# -      :: &Joey: wally, search(42) bucket
# -      :: &Joey: wally, search{8} bucket
# - 
# - 
# - Factoid Lookup:
# -    Syntax:
# -       wally[,:] factoid 123
# -       wally[,:] factoid #123
# - 
# - 
# - Recent Factoid Info:
# -    Syntax:
# -       wally[,:] what was that
# -         - Returns the ID of the most recent factoid.
# -       wally[,:] who made that
# -         - Returns the ID and creator of the most recent factoid.
# - 
# - 
# - Removing Factoids:
# -    Syntax:
# -       wally[,:] forget that
# -       wally[,:] undo that
# -       wally[,:] forget #123
# -       wally[,:] forget 123
# - 
# -    Notes:
# -       - "undo that" deletes the last CREATED factoid where as 
# -         "forget that" deletes the last SAID factoid
# - 
# - 
# - Making him shut up
# -    Syntax:
# -       wally[,:] shut up
# -
# -    Example:
# -       :: &Joey: wally, shut up
# -       :: %wally: Ok, Joey, be back in 2 minutes.
# - 
# - 
# - Protecting Factoids (Op only):
# -    Syntax:
# -       wally[,:] protect that
# -       wally[,:] protect 123
# -       wally[,:] protect #123
# -       wally[,:] unprotect that
# -       wally[,:] unprotect 123
# -       wally[,:] unprotect #123
# - 
# -    Notes:
# -       - This command makes the factoid untouchable by non ops.
# -       - This command only works for operators.
# -
# - Statistics:
# -    Syntax:
# -       wally[,:] count
# -
# -    Notes:
# -       - Returns how many actual factoids he holds
# -       - Factoid IDs do not represent the number of factoids he holds
# -
# - 



try: conn
except: conn = None
try: cur
except: cur = None
try: channels
except: channels = {}
try: chattichans
except: chattichans = {}

random.seed()


"""if 'bucket' not in meta.conf:
	meta.conf['bucket'] = False
	
if 'reusetimeout' not in meta.conf:
	meta.conf['reusetimeout'] = 600
else:
	meta.conf['reusetimeout'] = int(meta.conf['reusetimeout'])
	
if 'ignore' not in meta.conf:
	meta.conf['ignore'] = []
else:
	meta.conf['ignore'] = meta.conf['ignore'].split()
	
if 'censor_channel' not in meta.conf:
	meta.conf['censor_channel'] = []
else:
	meta.conf['censor_channel'] = meta.conf['censor_channel'].split()"""

	

#conn = sqlite3.connect('bucket.sql')
#cur = conn.cursor()


#cur.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='factoids' LIMIT 1""")
#if not cur.fetchone():
#	cur.execute("""CREATE TABLE factoids(id, inkling, find, verb, reply, nick)""")

#ROWID
#cur.execute("""CREATE TABLE IF NOT EXISTS `factoids`(
#					`id` INTEGER PRIMARY KEY, 
#					`inkling` TEXT NOT NULL, 
#					`find` TEXT NOT NULL, 
#					`verb` VARCHAR(32) NOT NULL, 
#					`tidbit` TEXT NOT NULL, 
#					`nick` VARCHAR(32) NOT NULL, 
#					`editable` INTEGER(1) NOT NULL DEFAULT 1)""")
#				
#cur.execute("""CREATE TABLE IF NOT EXISTS `factoids`( 
#				`id` INTEGER PRIMARY KEY, 
#				`inkling` text NOT NULL, 
#				`find` text NOT NULL, 
#				`verb` varchar(32) NOT NULL, 
#				`tidbit` text NOT NULL, 
#				`nick` varchar(32) NOT NULL, 
#				`editable` tinyint(1) NOT NULL DEFAULT 1 
#				) ENGINE=MyISAM DEFAULT CHARSET=latin1;""")

#cur.execute("""INSERT INTO 
#				`factoids`	(`inkling`, `find`, `verb`, `tidbit`, `nick`) 
#				VALUES	('fobia', 
#						'my fobia', 
#						'<reply>', 
#						'who*, I''m scared of the boogieman...', 'Joey' 
#						)
#					""")
#cur.execute("""SELECT * FROM `factoids` WHERE `nick`='Joey'""")
#print(cur.fetchone())




def init(s):
	global conn, cur
	

	if 'bucket' not in meta.conf:
		meta.conf['bucket'] = False
		
	if 'reusetimeout' not in meta.conf:
		meta.conf['reusetimeout'] = 600
	else:
		meta.conf['reusetimeout'] = int(meta.conf['reusetimeout'])
		
	if 'chattiness' not in meta.conf:
		meta.conf['chattiness'] = 3
	else:
		meta.conf['chattiness'] = int(meta.conf['chattiness'])
		
	if 'ignore' not in meta.conf:
		meta.conf['ignore'] = []
	else:
		meta.conf['ignore'] = meta.conf['ignore'].split()
		
	if 'censor_channel' not in meta.conf:
		meta.conf['censor_channel'] = []
	else:
		meta.conf['censor_channel'] = meta.conf['censor_channel'].split()

	
	conn = sqlite3.connect('bucket.sql', timeout=20)
	cur = conn.cursor()
	
	cur.execute("""CREATE TABLE IF NOT EXISTS `factoids`(
					`id` INTEGER PRIMARY KEY, 
					`inkling` TEXT NOT NULL, 
					`find` TEXT NOT NULL, 
					`verb` VARCHAR(32) NOT NULL, 
					`tidbit` TEXT NOT NULL, 
					`nick` VARCHAR(32) NOT NULL, 
					`editable` INTEGER(1) NOT NULL DEFAULT 1,
					`last_said` INTEGER NOT NULL DEFAULT 0,
					`explicit` INTEGER(1) NOT NULL DEFAULT 0)""")
	
	cur.execute("""CREATE TABLE IF NOT EXISTS `del_factoids`(
					`id` INTEGER PRIMARY KEY, 
					`inkling` TEXT NOT NULL, 
					`find` TEXT NOT NULL, 
					`verb` VARCHAR(32) NOT NULL, 
					`tidbit` TEXT NOT NULL, 
					`nick` VARCHAR(32) NOT NULL, 
					`editable` INTEGER(1) NOT NULL DEFAULT 1,
					`last_said` INTEGER NOT NULL DEFAULT 0,
					`explicit` INTEGER(1) NOT NULL DEFAULT 0,
					`del_id` INTEGER NOT NULL DEFAULT 0,
					`del_time` INTEGER NOT NULL DEFAULT 0,
					`del_nick` VARCHAR(32) NULL, 
					`del_ident` VARCHAR(32) NULL, 
					`del_host` VARCHAR(128) NULL, 
					`del_channel` VARCHAR(64) NULL)""")
	
	cur.execute("""CREATE TABLE IF NOT EXISTS `users`(
					`id` INTEGER PRIMARY KEY, 
					`user` VARCHAR(32) NOT NULL, 
					`pass` VARCHAR(32) NOT NULL, 
					`nick` VARCHAR(32) NOT NULL DEFAULT '', 
					`ident` VARCHAR(32) NOT NULL DEFAULT '', 
					`host` VARCHAR(128) NOT NULL DEFAULT '', 
					`level` INTEGER NOT NULL DEFAULT 0)""")
	
	conn.commit()
	
	
	cur.execute("""SELECT * FROM `users` WHERE `user`=? LIMIT 1""",('admin',))
	
	res = cur.fetchone()
	
	if not res:
		cur.execute("""INSERT INTO `users` (`user`,`pass`,`level`) VALUES (?, ?, ?)""",('admin', hashlib.md5(bytes(meta.conf['auth']+'94--s9g', 'utf8')).hexdigest(), '99'))
	conn.commit()
	
	#cur.execute("""ALTER TABLE `factoids` ADD COLUMN `last_said` INTEGER NOT NULL DEFAULT 0""")
	
	cur.execute("""SELECT sql FROM sqlite_master WHERE `name` = 'del_factoids'""")
	(a,) = cur.fetchone();
	
	if a.find("`del_id`") == -1:
		cur.execute("""ALTER TABLE `del_factoids` ADD COLUMN `del_id` INTEGER NOT NULL DEFAULT 0""")
	
	if a.find("`del_time`") == -1:
		cur.execute("""ALTER TABLE `del_factoids` ADD COLUMN `del_time` INTEGER NOT NULL DEFAULT 0""")
	
	if a.find("`del_nick`") == -1:
		cur.execute("""ALTER TABLE `del_factoids` ADD COLUMN `del_nick` VARCHAR(32) NULL""")
	
	if a.find("`del_ident`") == -1:
		cur.execute("""ALTER TABLE `del_factoids` ADD COLUMN `del_ident` VARCHAR(32) NULL""")
	
	if a.find("`del_host`") == -1:
		cur.execute("""ALTER TABLE `del_factoids` ADD COLUMN `del_host` VARCHAR(128) NULL""")
	
	if a.find("`del_channel`") == -1:
		cur.execute("""ALTER TABLE `del_factoids` ADD COLUMN `del_channel` VARCHAR(64) NULL""")
	
	
	conn.commit()




def log(*a):
	pass

	
	"""CREATE TABLE IF NOT EXISTS `factoids`(
		`id` INTEGER PRIMARY KEY, 
		`inkling` TEXT NOT NULL, 
		`match` TEXT NOT NULL, 
		`action` VARCHAR(32) NOT NULL, 
		`text` TEXT NOT NULL, 
		`nick` VARCHAR(32) NOT NULL,
		`ident` VARCHAR(32) NOT NULL,
		`host` VARCHAR(128) NOT NULL,
		`channel` VARCHAR(128) NOT NULL,
		`last_said` INTEGER NOT NULL DEFAULT 0
		)"""

	
def factoid_exists_UNUSED(id):
	cur.execute("""SELECT 1 FROM `factoids` WHERE `id`=? LIMIT 1""", (id,))
	conn.commit()
	return not not cur.fetchone()

	
def factoid_get_UNUSED(id):
	cur.execute("""SELECT * FROM `factoids` WHERE `id`=? LIMIT 1""", (id,))
	conn.commit()
	return cur.fetchone()

	
def factoid_inkling_UNUSED(inkling, limit=None):
	sql = "SELECT * FROM `factoids` WHERE `inkling`=:inkling"
	if limit: 
		sql += "LIMIT :limit"
	cur.execute(sql, 
				{"inkling":inkling, "limit":limit}
				)
	conn.commit()
	return cur.fetchone()


	
def factoid_forget_UNUSED(id):
	f = factoid_get(id)
	
	if not f: return None
	
	cur.execute("""INSERT INTO 
				`del_factoids`	(`inkling`, `find`, `verb`, `tidbit`, `nick`, `editable`, `last_said`) 
				VALUES		(:inkling,  :find,  :verb,  :tidbit,  :nick,  :editable,  :last_said )
				""",  f)
	
	conn.commit()
	return factoid_delete(id)
	
	
def factoid_delete_UNUSED(id):
	cur.execute("""DELETE FROM `factoids` WHERE `id`=? LIMIT 1""", (id,))
	conn.commit()
	return cur.rowcount
	
	
	
def factoid_add_UNUSED(text, channel, nick, ident, host):
	response = "Ok {nick}"
	""" 
	wally is cool
	robots are cool
	wally is <reply> sure am
	wally is <action> sure am
	something <kick> [reason] (chan op)
	something <mute> time (chan op)
	something <notice> notice text (chan op)
	something <ban> [(nick|ident|host)+ | full] (chan op)
	[:nick!ident@host] mibbit <onquit> ribbit (chan hop)
	[nick] <onjoin [notice|action|msg]> text
	"""
	return response.format({'channel':channel, 'nick':nick, 'ident':ident, 'host':host})
	
	
	
def factoid_insert_UNUSED(**kwargs):
	unify_kwargs(kwargs, {'table':'factoids', 'protected': 1, 'last_said':0})
	cur.execute("""INSERT INTO 
				:table	(`inkling`, `find`, `verb`, `tidbit`, `nick`, `protected`, `said`) 
				VALUES	(:inkling,  :find,  :verb,  :tidbit,  :nick,  :protected,  :said )
				""",  kwargs)
	conn.commit()
	return cur.rowcount
	
def unify_kwargs(args, default):
	for name, value in default.items():
		args[name] = name in args and args[name] or value
	return args
	
def factoid_search_UNUSED(text):
	pass

	
def factoid_lookup_OLD(text, factoidList, aliass, depth):
	if depth > 10: return []
	
	#factoidList = []
	text = text.lower()
	
	#for inkling in re.split("[^a-z]", text):
	for inkling in text.split():
		if not inkling: continue
		
		print("Inkling:", inkling)
		cur.execute("""SELECT * FROM `factoids` WHERE `inkling`=? AND `last_said`<?
						ORDER BY `last_said`, RANDOM() ASC
						LIMIT 1""", (inkling, time.time()-meta.conf['reusetimeout']))
		conn.commit()
		tempFactoid = cur.fetchone()
		
		if tempFactoid:
			print(tempFactoid)
			#check for and handle beginning and end identifiers
			if tempFactoid[2][0] == "^":
				#If this wasnt here (using find instead of rfind) then 
				#it could match identical phrases at the beginning and end: 
				#["phrase asdf phrase" instead of "phrase"]
				if tempFactoid[2][-1] == "$":
					if text.find(tempFactoid[2][:-1].lower()) != len(text)-len(tempFactoid[2][:-1]):
						print("Not a match at the end. (beg search)")
						continue
					else:
						tempFactoid = list(tempFactoid)
						tempFactoid[2] = tempFactoid[2][1: -1]
						tempFactoid = tuple(tempFactoid)
						print("Match at the beginning and end")
						if tempFactoid not in factoidList:
							factoidList.append( tempFactoid )
				
				# if there is no ending identifier $
				else:
					if text.find(tempFactoid[2][1:].lower()) != 0:
						print("Not a match at the beginning.")
						continue
					else:
						print("Match at the beginning.")
						tempFactoid = list(tempFactoid)
						tempFactoid[2] = tempFactoid[2][1 :]
						tempFactoid = tuple(tempFactoid)
						if tempFactoid not in factoidList:
							factoidList.append( tempFactoid )
			
			elif tempFactoid[2][-1] == "$":
				if text.rfind(tempFactoid[2][:-1].lower()) != len(text)-len(tempFactoid[2][:-1]):
					print("Match at the end. (end search)", text.rfind(tempFactoid[2][:-1].lower()), len(text)-len(tempFactoid[2][:-1]))
					continue
				else:
					print("Match at the end")
					tempFactoid = list(tempFactoid)
					tempFactoid[2] = tempFactoid[2][: 1]
					tempFactoid = tuple(tempFactoid)
					if tempFactoid not in factoidList:
						factoidList.append( tempFactoid )
				
				
			#normal text search
			elif text.find(tempFactoid[2].lower()) != -1:
				print("normal text match")
				if False and tempFactoid[3] == "<alias>" and (tempFactoid[2] not in aliass):
					aliass.append(tempFactoid[2])
					aliasedFactoid = factoid_lookup(
											text.replace(tempFactoid[2], tempFactoid[4]), 
											factoidList,
											aliass,
											depth+1)
					if aliasedFactoid:
						#print("+++Alias:", aliasedFactoid)
						factoidList.extend( aliasedFactoid )
					#else:
						#print("--no alias matched")
					
				else:
					if tempFactoid not in factoidList:
						factoidList.append( tempFactoid )
						
		# factoid not found for inkling
		else:
			inkling = inkling.strip(",.:;\"'?!()")
			
			if not inkling: continue
				
			cur.execute("""SELECT * FROM `factoids` WHERE `inkling`=?  AND `last_said`<?
							ORDER BY `last_said`, RANDOM() DESC
							LIMIT 1""", (inkling, time.time()-meta.conf['reusetimeout']))
			conn.commit()
			tempFactoid = cur.fetchone()
			
			if tempFactoid:
				
				if text.find(tempFactoid[2].lower()) != -1:
					if False and tempFactoid[3] == "<alias>" and (tempFactoid[2] not in aliass):
						aliass.append(tempFactoid[2])
						aliasedFactoid = factoid_lookup(
												text.replace(tempFactoid[2], tempFactoid[4]), 
												factoidList,
												aliass,
												depth+1)
						if aliasedFactoid:
							factoidList.extend( aliasedFactoid )
						
					else:
						if tempFactoid not in factoidList:
							factoidList.append( tempFactoid )
							
					
	return factoidList



def new_factoid_lookup(text, factoidList=None, hide_explicit=None):

	if factoidList is None:
		factoidList = []
		
	
	if hide_explicit:
		sql = """SELECT * FROM `factoids` WHERE `inkling`=? AND `last_said`<?
					AND `explicit`=0
					ORDER BY `last_said`, RANDOM() DESC
					LIMIT 256"""
	else:
		sql = """SELECT * FROM `factoids` WHERE `inkling`=? AND `last_said`<?
					ORDER BY `last_said`, RANDOM() DESC
					LIMIT 256"""
	
	
	for inkling in text.split():
		cur.execute(sql, (inkling, time.time()-meta.conf['reusetimeout']))
		
		factoidList.extend(validFactoids(text))
	conn.commit()
	
	if factoidList:
		return factoidList
	
	
	for inkling in text.split():
		
		inklink = inkling.strip(",.:;\"'?!()")
		
		cur.execute(sql, (inkling, time.time()-meta.conf['reusetimeout']))
		
		factoidList.extend(validFactoids(text))
	conn.commit()
	
	return factoidList

def validFactoids(text):
	factoidList = []
	
	while True:
		factoid = cur.fetchone()
		
		if not factoid: break
		
		findLower = factoid[2].lower()
		
		if factoid[2][0] == '^':
			if factoid[2][-1] == '$':
				if text != findLower[1:-1]:
					continue
			elif text[:len(factoid[2][1:])] != findLower[1:]:
				continue
		elif factoid[2][-1] == '$':
			if text[-len(factoid[2][:1]):] != findLower[:1]:
				continue
		elif text.find(findLower) == -1:
			continue
		
		factoid = list(factoid)
		
		if factoid[2][0] == '^': 
			factoid[2] = factoid[2][1:]
		
		if factoid[2][-1] == '$': 
			factoid[2] = factoid[2][:-1]
		
		factoidList.append(tuple(factoid))
		
		print("MATCH |",factoid)
	
	return factoidList


	
	
	
	
	
	
	
	
def canDelete(user, ident, host, channel=None):
	
	return True
	
	
	
	
	
	
	
	
	
# range -> 1:30
foil_forget_range = 90
foil_forgets = []
def foilCheckForgets(nick, ident, host, channel):
	global foil_forgets
	
	t = time.time() - foil_forget_range
	
	last_forgets = list(filter(lambda x: x[0] > t, foil_forgets))
	
	# user check
	if len(list(filter(lambda x: x[1] == nick or x[2] == ident or x[3] == host, last_forgets))) > 4:
		return "My spam senses are tingling."
	
	# channel check
	if len(list(filter(lambda x: x[4] == channel, last_forgets))) > 5:
		return "My spam senses are tingling."
		
	return
	
	
	
	
	
	
def foilAddForget(nick, ident, host, channel, id):
	global foil_forgets
	foil_forgets.insert(0, [int(time.time()), nick, ident, host, channel, id])
	
	# clean up
	t = time.time() - foil_forget_range
	foil_forgets = list(filter(lambda x: x[0] > t, foil_forgets))
	
	return
	
	
	
	
	
	
	

def msg(s, nick, ident, host, channel, text):
	global conn, cur, channels
	
	if not meta.conf['bucket']:
		return True
	
	## Dont talk to yourself
	if nick == meta.conf['nick']:
		return True
	
	
	## dont talk to strange people 
	if nick in meta.conf['ignore'] or host in meta.conf['ignorehost']:
		return False
	
	
	inchannel = True
	
	if channel == meta.conf['nick']:
		channel = nick
		inchannel = False
	
	
	
	if channel not in channels:
		channels[channel] = {"lastFactoidId": 0,
							 "lastCreatedId": 0, 
							 "shutup": 0}
		
	elif channels[channel]["shutup"] > time.time():
		return True
	
	
	
	
	#/me did stuff - "\001ACTION did stuff\001"
	text = text.rstrip("\001")
	textLower = text.lower()
	factoidList = []
	
	
	
	
	if re.match(r"wally[,:] ", textLower) or \
		(channel in meta.LOUD and re.match(r"bio?t?ch[,:] ", text, re.I)):
		textLower = textLower[7 :].strip()
		unknownCommand = True
		
		
		
		###
		### chattiness
		###  - Set Chattiness level
		###
		if re.match(r"chatt?[iy]ness \d+[?!.]*$", textLower):
			
			clevel = int(re.match(r"chatt?[iy]ness (\d+)[?!.]*$", textLower).group(1))
			meta.conf['chattiness'] = (clevel>20) and 20 or clevel
			
			print("Setting chattiness level to", meta.conf['chattiness'])
			
			meta.sendMsg(s, channel, "%s, chattiness set to %s" % (nick, meta.conf['chattiness']))
			return True
		
		
		###
		### chattiness
		###  - Return chattiness level
		###
		elif re.match(r"chatt?[iy]ness[?!.]*$", textLower):
			meta.sendMsg(s, channel, "%s, chattiness is %s" % (nick, meta.conf['chattiness']))
			return True
		
		###
		### forget that
		###  - forget the last said factoid
		###
		elif re.match(r"(f[eiou]r?g[ei]t|undo) ((th|d)at|[#]?[0-9]+)[?!.]*$", textLower):
		
			# prevent forget spamming
			foiled = foilCheckForgets(nick, ident, host, channel)
			
			if foiled:
				meta.sendMsg(s, channel, foiled)
				return False
			
			
			#undo the last factoid
			word, reference = re.match(r"(f[eiou]r?g[ei]t|undo) ((th|d)at|[#]?[0-9]+)", textLower).group(1,2)
			
			#if not canDelete(nick, ident, host):
			#	meta.sendMsg(s, channel, "I can't let you do that %s." % nick)
			#	return False
			
			
			if reference == "that" or reference == "dat":
				if word == "undo":
					id = channels[channel]['lastCreatedId']
					channels[channel]['lastCreatedId'] = 0
					
					if id == channels[channel]['lastFactoidId']:
						channels[channel]['lastFactoidId'] = 0
						
				else: #forget
					id = channels[channel]['lastFactoidId']
					channels[channel]['lastFactoidId'] = 0
					
				if not id:
					meta.sendMsg(s, channel, "%s, %s what?" % (nick, word))
					return False
			else:
				#they used a factoid id
				reference = int(reference.lstrip('#'))
				id = reference
				
				if channels[channel]['lastFactoidId'] == id:
					channels[channel]['lastFactoidId'] = 0
				if channels[channel]['lastCreatedId'] == id:
					channels[channel]['lastCreatedId'] = 0
				
			
			
			
			cur.execute("""SELECT * FROM `factoids` WHERE `id`=? LIMIT 1""", (id,))
			conn.commit()
			
			res = cur.fetchone()
			
			if not res:
				meta.sendMsg(s, channel, "%s, that factoid doesn't exist." % nick)
				return False
			
			#if cur.fetchone()[0] == "0" and not (meta.isOp(channel, nick) or meta.isProtected(channel, nick)):
			if res[6] == "0":# and not (meta.isOp(channel, nick) or meta.isProtected(channel, nick)):
				
				meta.sendMsg(s, channel, "I can't let you do that %s." % nick)
				return False
			
			print("<<<", nick, "erased", id)
			
			
			cur.execute("""INSERT INTO 
				`del_factoids`	(`inkling`, `find`, `verb`, `tidbit`, `nick`, `editable`, `last_said`, `del_id`, `del_time`, `del_nick`, `del_ident`, `del_host`, `del_channel`) 
				VALUES		( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
				( res[1], res[2], res[3], res[4], res[5], res[6], res[7], id, time.time(), nick, ident, host, channel ))
			cur.execute("""DELETE FROM `factoids` WHERE `id`=?""", (id,))
			conn.commit()
			
			# add spam protection entry
			foilAddForget(nick, ident, host, channel, id)
			
			meta.sendMsg(s, channel, "Ok %s" % nick)
			return False
			
		###
		### ls
		###  - list (deleted) factoids
		###
		## TODO: add check for -v
		## TODO: add check for -d or -del
		elif re.match(r"ls.*$", textLower):
			
			## only authorized people can list factoids
			if not meta.isAuthor(nick, ident, host):
				meta.sendMsg(s, channel, "I'm afraid I can't let you do that %s" % (nick,))
				return False
				
			verbose = False
			deleted = False
			
			args = textLower[2:].split()
			
			if "-h" in args or "-help" in args or "--help" in args:
				meta.sendMsg(s, channel, "ls [-d] [-v] [-h]")
				meta.sendMsg(s, channel, "::   -d   Show deleted factoids (-del | --deleted)")
				meta.sendMsg(s, channel, "::   -v   Show every bit of info on each factoid (--verbose)")
				meta.sendMsg(s, channel, "::   -h   Display this help page (--help)")
				
				return False
				
			if "-v" in args or "--verbose" in args:
				verbose = True
				
			if "-d" in args or "-del" in args or "--deleted" in args:
				deleted = True
			
			if deleted:
				cur.execute("""SELECT * FROM `del_factoids` ORDER BY `id` DESC LIMIT 10""")
			else:
				cur.execute("""SELECT * FROM `factoids` ORDER BY `id` DESC LIMIT 10""")
			
			
			factoids = cur.fetchall()
			
			if deleted and not verbose:
				oShit = "{id}: {find} {verb} {reply} (Del: {deltime} {deleter})"
			elif deleted: # and verbose
				oShit = "{id}: {find} ({inkling}) {verb} {reply} :{creator} (Del:{delid} {deltime}:{delchan} {deleter}!{delident}@{delhost})"
			elif not deleted and not verbose: # normal
				oShit = "{id}: {find} {verb} {reply} :{creator}"
			else: # verbose normal factoids
				oShit = "{id}: {find} ({inkling}) {verb} {reply} :{creator} {lastsaid}"
				
			for res in factoids:
				meta.sendMsg(s, channel, oShit.format( \
					id = res[0], \
					inkling = res[1], \
					find = res[2], \
					verb = res[3], \
					reply = res[4], \
					creator = res[5], \
					editable = res[6], \
					lastsaid = res[7], \
					explicit = res[8], \
					delid = deleted and res[9] or "", \
					deltime = deleted and res[10] or "", \
					deleter = deleted and res[11] or "", \
					delident = deleted and res[12] or "", \
					delhost = deleted and res[13] or "", \
					delchan = deleted and res[14] or ""))
			return False
		
		
		###
		### un delete factoid
		###    unforget [id]|[deleter] [after]
		###
		elif re.match(r"unforget (?:(\d+)|(\S+)\s+(\d\d-\d\d-\d\d\d\d))[?!.]*$", textLower):
			
			r = re.match(r"unforget (?:(\d+)|(\S+)\s+(\d\d-\d\d-\d\d\d\d))[?!.]*$", text[7 :], re.I)
			(id, deleter, since) = r.groups()
			
			
			### Specific ID given. Recover one factoid from deletion.
			if id:
				cur.execute("""SELECT * FROM `del_factoids` WHERE `del_id`=? LIMIT 1""", (id,))
				conn.commit()
				res = cur.fetchone()
				if not res:
					meta.sendMsg(s, channel, "%s, I can not find any deleted factoid with that ID" % nick)
					return False
					
				"""
				0	`id` INTEGER PRIMARY KEY, 
				1	`inkling` TEXT NOT NULL, 
				2	`find` TEXT NOT NULL, 
				3	`verb` VARCHAR(32) NOT NULL, 
				4	`tidbit` TEXT NOT NULL, 
				5	`nick` VARCHAR(32) NOT NULL, 
				6	`editable` INTEGER(1) NOT NULL DEFAULT 1,
				7	`last_said` INTEGER NOT NULL DEFAULT 0,
				8	`explicit` INTEGER(1) NOT NULL DEFAULT 0,
				9	`del_id` INTEGER NOT NULL DEFAULT 0,
				10	`del_time` INTEGER NOT NULL DEFAULT 0
				11	`del_nick` VARCHAR(32) NOT NULL, 
				12	`del_ident` VARCHAR(32) NOT NULL, 
				13	`del_host` VARCHAR(128) NOT NULL, 
				14	`del_channel` VARCHAR(64) NOT NULL)"""
				
				cur.execute("""INSERT INTO 
							`factoids`	(`inkling`, `find`, `verb`, `tidbit`, `nick`, `editable`, `last_said`, `explicit`) 
							VALUES		(    ?,       ?,      ?,       ?,       ?,       ?,           ?,          ?)
						""",            ( res[1],   res[2],   res[3],   res[4],   res[5],  res[6],   time.time(),    res[8]))
						
				channels[channel]['lastCreatedId'] = cur.lastrowid
				channels[channel]['lastFactoidId'] = cur.lastrowid
				
				meta.sendMsg(s, channel, "Factoid Recovered - %s: %s %s %s :: by:%s del:%s" % (cur.lastrowid, res[2], res[3], res[4], res[5], res[11]))
				
				conn.commit()
				
				cur.execute("""DELETE FROM `del_factoids` WHERE `id`=?""", (id,))
				conn.commit()
				
				return False
			
			
			if not meta.isAuthor(nick, ident, host):
				meta.sendMsg(s, channel, "I'm afraid I can't let you do that, %s" % (nick,))
				return False
			
			### No specific id given. Go by deleter and date to recover multiple
			
			since = time.mktime(time.strptime(since,"%m-%d-%Y"))
			
			cur.execute("""SELECT * FROM `del_factoids` WHERE `del_nick` = ? AND `del_time` >= ?""", (deleter, since))
			conn.commit()
			
			dels = cur.fetchall()
			
			for res in dels:
				cur.execute("""INSERT INTO 
							`factoids`	(`inkling`, `find`, `verb`, `tidbit`, `nick`, `editable`, `last_said`, `explicit`) 
							VALUES		(    ?,       ?,      ?,       ?,       ?,       ?,           ?,          ?)
						""",            ( res[1],   res[2],   res[3],   res[4],   res[5],  res[6],   time.time(),  res[8]))
						
				#channels[channel]['lastCreatedId'] = cur.lastrowid
				#channels[channel]['lastFactoidId'] = cur.lastrowid
				
				#meta.sendMsg(s, channel, "Factoid Recovered - %s: %s %s %s :: by:%s del:%s" % (cur.lastrowid, res[2], res[3], res[4], res[5], res[11]))
				
				conn.commit()
				
				cur.execute("""DELETE FROM `del_factoids` WHERE `id`=?""", (res[0],))
				conn.commit()
				
				#res = cur.fetchone()
			
			meta.sendMsg(s, channel, "%d Factoids Recovered" % (len(dels),))
			return False
			
			
			
		###
		### what was that
		###  - get information about last said factoid
		###
		elif re.match(r"wh?at (was|were) (th|d)at[?!.]*$", textLower):
			#spout info about the last factoid
			if not channels[channel]['lastFactoidId']:
				meta.sendMsg(s, channel, "%s: What was what?" % nick)
				return False
				
			#meta.sendMsg(s, channel, "%s, That was factoid %d " % (nick, channels[channel]['lastFactoidId']))
			#return False
			
			id = channels[channel]['lastFactoidId']
			cur.execute("""SELECT * FROM `factoids` WHERE `id`=? LIMIT 1""", (id,))
			conn.commit()
			data = cur.fetchone()
			
			if not data:
				meta.sendMsg(s, channel, "%s, idk..." % nick)
				return False
			
			channels[channel]['lastFactoidId'] = int(data[0])
			
			#if data[6] == 1: editable = ""
			#else: editable = "!Not Editable!"
			
			meta.sendMsg(s, channel, "That was %s: %s %s %s :%s"
				% (data[0], data[2], data[3], data[4], data[5]))
				
			return False
			
		###
		### who made that
		###  - get information about the last factoid
		###
		elif re.match(r"who made ((th|d)at|[#]?[0-9]+)[?!.]*$", textLower):
			#spout info about the last factoid
			if not channels[channel]['lastFactoidId']:
				meta.sendMsg(s, channel, "%s: Who made what?" % nick)
				return False
			
			cur.execute("""SELECT `nick` FROM `factoids` WHERE `id`=? LIMIT 1""", (channels[channel]['lastFactoidId'],))
			conn.commit()
			who = cur.fetchone()
			if who:
				who = who[0]
				if who == nick:
					who = "you"
				meta.sendMsg(s, channel, "%s, %s made factoid %d " % (nick, who, channels[channel]['lastFactoidId']))
			else:
				meta.sendMsg(s, channel, "%s, idk..." % nick)
				
			return False
			
			
			
			
			
		###
		### mark that explicit
		###  - dont say a specific factoid in mixed company
		###
		elif re.match(r"(un)?mark (that|#?(\d+))( as)? explicit[?!.]*$", textLower):
			#only ops and above can do that
			if not (meta.isOp(channel, nick) or meta.isProtected(channel, nick)):
				meta.sendMsg(s, channel, "I can't let you do that %s." % nick)
				return False
			
			un, what, id = re.match(r"(un)?mark (that|#?(\d+))( as)? explicit[?!.]*$", textLower).group(1,2,3)
			
			if what == "that":
				id = channels[channel]['lastFactoidId']
			else:
				id = int(id)
			
			if not id:
				meta.sendMsg(s, channel, "%s: mark what?" % nick)
				return False
			
			
			res = cur.execute("""UPDATE `factoids` SET `explicit`=? WHERE `id`=?""",
					(int(not bool(un)), id))
			conn.commit()
			
			if res:
				meta.sendMsg(s, channel, "%s, done.." % nick)
			else:
				meta.sendMsg(s, channel, "%s, tried, couldn't do it." % nick)
			
			return False
			
			
			
			
		###
		### shut up
		###  - silence wally for a while (10 minutes) [see below for more]
		###
		elif re.match(r"shut (up|it) f[ouei]r a[ ]wh+ile[?!.]*$", textLower):
			channels[channel]['shutup'] = time.time() + 600
			meta.sendMsg(s, channel, "Ok %s, be back in 10 minutes." % nick)
			return False
		
		###
		### shut up
		###  - silence wally for a set amount of time [see below for more]
		###
		#elif re.match(r"shut (up|it) f[ouei]r (0-9)(m[in]|s[ec]|h|hour[s]|y|year[s])[?!.]*$", textLower):
		#	#channels[channel]['shutup'] = time.time() + 600
		#	#meta.sendMsg(s, channel, "Ok %s, be back in 10 minutes." % nick)
		#	return False
			
		###
		### shut up
		###  - silence wally for 2 minutes
		###
		elif re.match(r"shut (up|it)[?!.]*$", textLower):
			channels[channel]['shutup'] = time.time() + 120
			meta.sendMsg(s, channel, "Ok %s, be back in 2 minutes." % nick)
			return False
		
		###
		### count
		###  - count and return the factiods in his arsenal
		###
		elif re.match(r"count$", textLower):
			cur.execute("""SELECT COUNT(*) FROM `factoids`""")
			conn.commit()
			count = cur.fetchone()[0]
			
			meta.sendMsg(s, channel, "I have %s factoids." % count)
			#print("wally has", count, "factoids")
			return False
		
		###
		### factoid 666
		###  - recall and vomit a specific factoid
		###
		elif re.match(r"factoid [#]?[0-9]+$", textLower):
			id = int(re.match(r"factoid [#]?([0-9]+)", textLower).group(1))
			
			cur.execute("""SELECT * FROM `factoids` WHERE `id`=? LIMIT 1""", (id,))
			conn.commit()
			data = cur.fetchone()
			
			if not data:
				meta.sendMsg(s, channel, "%s, that factoid doesn't exist." % nick)
				return False
			
			channels[channel]['lastFactoidId'] = int(data[0])
			
			if data[6] == 1: editable = ""
			else: editable = "!Not Editable!"
			
			meta.sendMsg(s, channel, "Factoid %s: %s \003| %s \003| %s \003:%s \003%s"
				% (data[0], data[2], data[3], data[4], data[5], editable))
			
			
			return False
		
		###
		### search
		###  - search factoids via keywords
		###
		## TODO: add -del option for deleted factoids
		## TODO: add clause to search in 'replies' as well as 'finds'
		elif re.match(r"search([\s]?[\(\[\{]?[0-9]+[\)\}\]]?)? (.+)", textLower):
			#return False
			page, search = re.match(r"search([\s]?[\(\[\{]?[0-9]+[\)\}\]]?)? (.+)", textLower).group(1,2)
			
			if len(search) < 4:
				meta.sendMsg(s, channel, "query too short.")
				return False
			
			if not page:
				page = 0
			else:
				page = int(page.strip(" \t[]{}()"))
				
			search = "%"+search+"%"
			cur.execute("""SELECT * FROM `factoids` WHERE `find` LIKE ? ORDER BY `id` LIMIT 5 OFFSET ?""", (search, page))
			
			conn.commit()
			data = cur.fetchall()
			
			
			if data:
				result = ""
				
				for x in range(len(data)):
				
					temp = "%s: %s %s %s" \
							% (
								data[x][0], 
								#re.sub(r"(?i)(\b)(is|are|search|factoid)(\b)", r"\1\\\2\3", data[x][2]), 
								re.sub(r"(?i)(\b)(search|factoid)(\b)", r"\1\\\2\3", data[x][2]), 
								data[x][3], 
								data[x][4]
							  )
						
					if len(temp)+len(result) > 400: break
					
					if result: result = result +" \003| "+ temp
					else: result = temp
					
				meta.sendMsg(s, channel, "Results: %s" % result)
				
			else:
				meta.sendMsg(s, channel, "Sorry %s, I couldn't find anything." % nick)
			
			return False
		
		
		###
		### protect
		###  - channel ops can keep factoids from being deleted by regular folk
		###
		elif re.match(r"(unprotect|protect) ((th|d)at|[#]?[0-9]+)[?!.]*$", textLower):
			#only ops and above can do that
			if not (meta.isOp(channel, nick) or meta.isProtected(channel, nick)):
				meta.sendMsg(s, channel, "I can't let you do that %s." % nick)
				return False
				
			word,reference=re.match(r"(unprotect|protect) (that|[#]?[0-9]+)", textLower).group(1,2)
			
			if word == "protect":
			
				if reference == "that" or reference == "dat":
					id = channels[channel]['lastFactoidId']
				else:
					id = int(reference.lstrip("#"))
				
				cur.execute("""UPDATE `factoids` SET `editable`=? WHERE `id`=?""",
					(0, id))
				conn.commit()
				
			else: # unprotect
				
				meta.sendMsg(s, channel, "unprotect is no longer available." % nick)
				return False
				
				if reference == "that" or reference == "dat":
					id = channels[channel]['lastFactoidId']
				else:
					id = int(reference.lstrip("#"))
				
				cur.execute("""UPDATE `factoids` SET `editable`=? WHERE `id`=?""",
					(1, id))
				conn.commit()
			
			meta.sendMsg(s, channel, "Ok %s" % nick)
			return False
		
		elif textLower == "?" or \
			 textLower == "help" or \
			 textLower == "docs" or \
			 textLower == "manual" or \
			 textLower == "/?":
			 
			if "help" in meta.conf:
				meta.sendMsg(s, channel, meta.conf["help"])
			else:
				meta.sendMsg(s, channel, "https://github.com/MOSW/wallybot/wiki/Manual")
			
			return False
			
		elif textLower == "source":
			 
			if "source" in meta.conf:
				meta.sendMsg(s, channel, meta.conf["source"])
			else:
				meta.sendMsg(s, channel, "https://github.com/MOSW/wallybot")
			
			return False
		
		
		#search = re.search(r'\s(is|are|<[a-z]+>)\s', text, re.ASCII | re.I)
		search = re.search(r'\s(<[a-z]+>)\s', text, re.ASCII | re.I)
		
		if search:
		
			verb = search.group(0).strip()
			
			
			tSplit = text[7 :].split(" "+verb+" ", 1)
			if len(tSplit) != 2:
				meta.sendMsg(s, channel, "%s: huh?" % nick)
				return False
			
			find = tSplit[0].strip()
			tidbit = tSplit[1].strip()
			
			verbLower = verb.lower()
			
			if verbLower != "<action>" and verbLower != "<reply>":
				verb = verb.strip("<>")
				verbLower = verb.lower()
			else:
				verb = verbLower
			
			
			
			if len(find) < 2:
				meta.sendMsg(s, channel, "%s: The fact is too short." % nick)
				return False
				
			if len(tidbit) < 2:
				meta.sendMsg(s, channel, "%s: Your 'tidbit' is too short..." % nick)
				return False
			
			
			
			find = re.sub(r"(?i)\\(is|are|search|factoid)", r"\1", find)
			tidbit = re.sub(r"(?i)\\(is|are|search|factoid)", r"\1", tidbit)
			
			#find = find.replace("\\is", "is").replace("\\are", "are").replace("\\<", "<")
			#tidbit = tidbit.replace("\\is", "is").replace("\\are", "are").replace("\\<", "<")
			tidbit = tidbit.replace(r"\\<", r"<")
			
			#grab a one word inkling. this word is the largest word
			#max was not working correctly... so I implimented my own
			#inkling = max(find.split()).lower()
			inklingSearch = find
			
			#strip out the ^ and $ so they dont appear in our inkling
			if inklingSearch[0] == "^": inklingSearch = inklingSearch[1 :]
			if inklingSearch[-1] == "$" and inklingSearch[-1] != "\\": inklingSearch = inklingSearch[:-1]
			
			inkling = None
			for word in inklingSearch.split():
				#set it to begin with
				if not inkling:
					inkling = word
					continue
				
				if len(word) > len(inkling):
					inkling = word
			
			inkling = inkling.lower()
			
			cur.execute("""INSERT INTO 
							`factoids`	(`inkling`, `find`, `verb`, `tidbit`, `nick`, `last_said`) 
							VALUES		(    ?,       ?,      ?,       ?,       ?,          ?)
						""",            ( inkling,   find,   verb,   tidbit,   nick,        0))
			channels[channel]['lastCreatedId'] = cur.lastrowid
			channels[channel]['lastFactoidId'] = cur.lastrowid
			conn.commit()
			
			meta.sendMsg(s, channel, "Ok %s" % nick)
			
			print(">>>",nick+":", find, verb, tidbit, cur.lastrowid)
			
			return False
			
		
		##
		## Factoid lookup when being spoken to.
		##
		textLower = re.sub(r"^\001action", r"/me", textLower)
		#factoidList = factoid_lookup(textLower, [], [], 0)
		
		explicit = channel in meta.conf['censor_channel']
		
		factoidList = new_factoid_lookup(textLower, [], explicit)
		
		if factoidList:
			unknownCommand = False
			
		if unknownCommand:
			meta.sendMsg(s, channel, random.choice(meta.unknownCmdReplys).format(nick=nick,chan=channel))
		
		
	##
	## Factoid lookup when not being spoken to.
	##
	elif len(textLower) > 4:
		## Limit speech with chattiness level so he's not annoying
		## - Each chattiness level represents one message
		## - Once the level has reached he can speak.
		if channel not in chattichans:
			## add channel to chattiness and make him able to talk immediately
			chattichans[channel] = meta.conf['chattiness']
		
		
		chattichans[channel] = chattichans[channel]+1
		
		if chattichans[channel] < meta.conf['chattiness']: return True
		
		## chattiness level reached. He can talk now.
		#chattichans[channel] = 0
		
		textLower = re.sub(r"^\001action", r"/me", textLower)
		
		#factoidList = factoid_lookup(textLower, [], [], 0)
		
		## does this channel need to be censored?
		explicit = channel in meta.conf['censor_channel']
		
		factoidList = new_factoid_lookup(textLower, [], explicit)
		
		
	
	
	if factoidList:
		
		##
		## Some chattiness fun
		##
		if channel not in chattichans:
			chattichans[channel] = meta.conf['chattiness']
			
		## if he was talked to directly, allow him to talk again.
		if chattichans[channel] < meta.conf['chattiness']:
			chattichans[channel] = meta.conf['chattiness']
		else:
			## otherwise reset to zero chattiness when he speaks to start again.
			chattichans[channel] = 0
		
		
		
		reply = random.choice(factoidList)
		
		channels[channel]['lastFactoidId'] = int(reply[0])
		
		replyText = reply[4]
		
		cur.execute("""UPDATE `factoids` SET `last_said`=? WHERE `id`=?""",
					(time.time(), reply[0]))
		conn.commit()
		
		replyText = replyText.replace("who*", nick)
		replyText = replyText.replace("WHO*", nick.upper())
		
		replyText = replyText.replace("chan*", channel)
		replyText = replyText.replace("CHAN*", channel.upper())
		
		randNick = None
		if replyText.find("someone*") != -1:
			randNick = meta.randomUser(channel).nick
			replyText = replyText.replace("someone*", randNick)
		
		if replyText.find("SOMEONE*") != -1:
			if not randNick:
				randNick = meta.randomUser(channel).nick
			replyText = replyText.replace("SOMEONE*", randNick.upper())
		
		
		
		if reply[3] == "<reply>":
			meta.sendMsg(s, channel, replyText)
		elif reply[3] == "<action>":
			meta.sendMsg(s, channel, "\001ACTION "+replyText+"\001")
		else:
			meta.sendMsg(s, channel, reply[2]+" "+reply[3]+" "+replyText)
			
		return False
		
	
	



def notice(s, sender, ident, host, channel, text):
	
	authd = meta.isAuthor(sender, ident, host)
	
	textLower = text.lower()
	
	if textLower == '+bucket' and authd:
		if meta.conf['bucket']:
			meta.sendNotice(s, sender, "Confirm - Bucket is already On.")
		else:
			meta.sendNotice(s, sender, "Confirm - Bucket is now On.")
			meta.conf['bucket'] = True
		return False
		
	elif textLower == '-bucket' and authd:
		if not meta.conf['bucket']:
			meta.sendNotice(s, sender, "Confirm - Bucket is already Off.")
		else:
			meta.sendNotice(s, sender, "Confirm - Bucket is now Off.")
			meta.conf['bucket'] = False
		return False
		
	if textLower.find('+censor ') == 0 and authd:
		censor = text[8:].split()
		for p in censor:
			if not p: continue
			if p in meta.conf['censor_channel']:
				meta.sendNotice(s, sender, "Confirm - Already censoring \"%s\"." % (p,))
			else:
				meta.conf['censor_channel'].append(p)
				meta.sendNotice(s, sender, "Confirm - Now censoring \"%s\"." % (p,))
			
		return False
		
	if textLower.find('-censor ') == 0 and authd:
		censor = text[8:].split()
		for p in censor:
			if not p: continue
			if p not in meta.conf['censor_channel']:
				meta.sendNotice(s, sender, "Confirm - Wasn't censoring \"%s\"." % (p,))
			else:
				meta.conf['censor_channel'].remove(p)
				meta.sendNotice(s, sender, "Confirm - Not censoring \"%s\"." % (p,))
			
		return False
		
	elif textLower.find('ignore ') == 0 and authd:
		ignore = text[7:].split()
		for p in ignore:
			if not p: continue
			if p in meta.conf['ignore']:
				meta.sendNotice(s, sender, "Confirm - Already ignoring \"%s\"." % (p,))
			else:
				meta.conf['ignore'].append(p)
				meta.sendNotice(s, sender, "Confirm - Now ignoring \"%s\"." % (p,))
		return False
		
	elif textLower.find('unignore ') == 0 and authd:
		ignore = text[9:].split()
		for p in ignore:
			if not p: continue
			if p in meta.conf['ignore']:
				meta.conf['ignore'].remove(p)
				meta.sendNotice(s, sender, "Confirm - Now Listening to \"%s\"." % (p,))
			else:
				meta.sendNotice(s, sender, "Confirm - \"%s\" not currently ignored." % (p,))
		return False
		
	elif textLower == 'mode?':
		if meta.conf['bucket']:
			meta.sendNotice(s, sender, "Mode: Bucket is On.")
		else:
			meta.sendNotice(s, sender, "Mode: Bucket is Off.")


def close(s):
	conn.commit()
	conn.close()