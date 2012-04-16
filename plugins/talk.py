import meta
import sys



if __name__ == "__main__":
	input("You opened the wrong file. This one can not run by itself.")
	sys.exit()



#meta.help.append('[+|-]talk - Turn automatic talking on or off. (Op)')


if 'talkto' not in meta.conf:
	meta.conf['talkto'] = meta.conf['channel'].split(',')[0]

if 'talk' not in meta.conf:
	meta.conf['talk'] = False



#:Diet-Drew!drew465@hide-70516ADF.dsl.pltn13.pacbell.net PRIVMSG #xkcd :ACTION clicks very quickly to woot.com
#:Diet-Drew!drew465@hide-70516ADF.dsl.pltn13.pacbell.net PRIVMSG #xkcd :\001ACTION clicks very quickly to woot.com\001

"""def msg(s, nick, ident, host, sender, text):
	if not meta.conf['talk']:
		return
	
	t = text.lower()
	out = "";
	if t == "hey" or t == "hi" or t == "hello":
		out = "hey"
	elif t == "hi to jobot" or t == "\"hi to jobot\"":
		out = "...smart ass"
	elif t == "you suck":
		out = "no, YOU suck."
	elif t.find('izbot') != -1:
		out = "Izbot...? That poser?"
	elif t.find('jobot') != -1:
		if t.find('fuck') != -1 or t.find('ass') != -1 or t.find('bitch') != -1 or t.find('damn') != -1 or t.find('darn') != -1 or t.find('dick') != -1 or t.find('hell') != -1 or t.find('shut up') != -1 or t.find('suck') != -1 or t.find('fag') != -1 or t.find('gay') != -1 or t.find('ghey') != -1 :
			out = "watch your mouth, asshole"
		else: out = "quit talking about me"
	
	if out:
		meta.sendMsg(s, sender, out)"""

def notice(s, nick, ident, host, sender, text):
	
	
	authd = meta.isAuthor(nick, ident, host)
	
	textLower = text.lower()
	
		
	if textLower[:7] == 'say to ' and authd:
		meta.conf['talkto'] = textLower[7:]
		return False
		
	elif textLower[:4] == 'say ' and authd:
		meta.sendMsg(s, meta.conf['talkto'], text[4:])
		return False
		
	elif textLower[:4] == 'act ' and authd:
		meta.sendMsg(s, meta.conf['talkto'], "\001ACTION %s\001" % text[4:])
		return False
		
	elif textLower == '+talk' and authd:
		if meta.conf['talk']:
			meta.sendNotice(s, nick, "Confirm - Talking is already On.")
		else:
			meta.sendNotice(s, nick, "Confirm - Talking is now On.")
			meta.conf['talk'] = True
		return False
		
	elif textLower == '-talk' and authd:
		if meta.conf['talk']:
			meta.sendNotice(s, nick, "Confirm - Talking is already Off.")
		else:
			meta.sendNotice(s, nick, "Confirm - Talking is now Off.")
			meta.conf['talk'] = False
		return False
		
	elif textLower == 'mode?':
		if meta.conf['talk']:
			meta.sendNotice(s, nick, "Mode: Talking is On.")
		else:
			meta.sendNotice(s, nick, "Mode: Talking is Off.")
