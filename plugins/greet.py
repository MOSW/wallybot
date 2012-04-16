import meta
import sys



if __name__ == "__main__":
	input("You opened the wrong file. This one can not run by itself.")
	sys.exit()



if 'greetchan' not in meta.conf:
	meta.conf['greetchan'] = []
else:
	meta.conf['greetchan'] = meta.conf['greetchan'].split(',')

if 'greet' not in meta.conf:
	meta.conf['greet'] = False

	
a = meta.conf['greetchan'][:]
meta.conf['greetchan'] = {}

for c in a:
	meta.conf['greetchan'][c.lower()] = c

#print(meta.conf['greetchan'])

	
def handle(s, nick, ident, host, cmd, data):
	if cmd == "JOIN" and meta.conf['greet']:
		channel = data[1 :].lower()
		if nick != meta.conf['nick'] and channel in meta.conf['greetchan']:
			meta.sendMsg(s, channel, "Hey %s, Welcome to %s!"%(nick, meta.conf['greetchan'][channel]))
			return True
	
	
	
	

def notice(s, nick, ident, host, sender, text):
	
	
	authd = meta.isAuthor(nick, ident, host)
	
	textLower = text.lower()
	
		
	if textLower[:11] == '+greetchan ' and authd:
		chan = text[11:]
		if chan.lower() in meta.conf['greetchan']:
			meta.sendNotice(s, nick, "Confirm - %s already being greeted."%chan)
		else:
			meta.conf['greetchan'][chan.lower()] = chan
			meta.sendNotice(s, nick, "Confirm - Now greeting %s."%chan)
		return False
	
		
	elif textLower[:11] == '-greetchan ' and authd:
		chan = text[11:]
		if chan.lower() in meta.conf['greetchan']:
			del meta.conf['greetchan'][chan.lower()]
			meta.sendNotice(s, nick, "Confirm - No longer greeting %s."%chan)
		else:
			meta.sendNotice(s, nick, "Confirm - %s was never being greeted."%chan)
		return False
		
	elif textLower[:6] == '+greet' and authd:
		meta.sendNotice(s, nick, "Confirm - Greet is On.")
		meta.conf['greet'] = True
		return False
		
	elif textLower[:6] == '-greet' and authd:
		meta.sendNotice(s, nick, "Confirm - Greet is Off.")
		meta.conf['greet'] = False
		return False
		
	elif textLower == 'mode?':
		if meta.conf['greet']:
			meta.sendNotice(s, nick, "Mode: Greeting is On.")
		else:
			meta.sendNotice(s, nick, "Mode: Greeting is Off.")
		meta.sendNotice(s, nick, "Greeting channels: %s"%repr(meta.conf['greetchan']))
