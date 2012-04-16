import time
import meta
import sqlite3
import sys
import traceback


#meta.help.append('[+|-]logmsg - Turn message logging on or off.')



if __name__ == "__main__":
	input("You opened the wrong file. This one can not run by itself.")
	sys.exit()
	



if 'logmsg' not in meta.conf:
	meta.conf['logmsg'] = False


"""def showMsg(nick, ident, host, cmd, data):
	if ident: ident = "!"+ ident
	else: ident = ""
	if host: host = "@"+ host
	else: host = ""
	
	print("{0} {1}{2}{3} {4} {5}".format(time.strftime("[%H:%M]"), nick, ident, host, cmd, data))"""


	
try:
	l = open('msg.log', 'ta', buffering=1, encoding='utf8', errors='replace')
except:
	print('Could not open log.\nLogging -Off')
	meta.conf['logmsg'] = False

if meta.conf['logmsg']:
	l.write("\n"+ time.strftime("%c") +" | "+ "New Session\n")

def log(text):
	if meta.conf['logmsg']:
		l.write(time.strftime("%c") +" | "+ text.rstrip('\r\n') +"\n")


def handle(s, name, ident, host, cmd, data):
	pass




def displayNotice(nick, text):
	print("NOTICE: {0}: {1}".format(nick, text))

def displayCNotice(nick, text):
	#print("NOTICE: {0}: {1}".format(nick, text))
	sys.stdout.write("NOTICE: ")
	sys.stdout.write(nick)
	sys.stdout.console.tag_add("nick","end-%sc"%(len(nick)+1),"end-1c")
	sys.stdout.write(": %s\n" % text)

try:
	#only try to color the message if we are using the custom console
	if 'console' in sys.stdout.__dict__:
		displayNotice = displayCNotice
		sys.stdout.console.tag_config("nick", foreground="#00CC99")
except:
	print("ERROR")
	traceback.print_exc()

def notice(s, sender, ident, host, channel, text):
	
	displayNotice(sender, text)
	
	authd = meta.isAuthor(sender, ident, host)
	text = text.lower()
	
	if text == '+logmsg' and authd:
		if meta.conf['logmsg']:
			meta.sendNotice(s, sender, "Confirm - Logging is already On.")
		else:
			meta.sendNotice(s, sender, "Confirm - Logging is now On.")
		meta.conf['logmsg'] = True
		
	elif text == '-logmsg' and authd:
		if meta.conf['logmsg']:
			meta.sendNotice(s, sender, "Confirm - Logging is now Off.")
		else:
			meta.sendNotice(s, sender, "Confirm - Logging is already Off.")
		meta.conf['logmsg'] = False
		
	elif text == 'mode?':
		if meta.conf['logmsg']:
			meta.sendNotice(s, sender, "Mode: Logging is On.")
		else:
			meta.sendNotice(s, sender, "Mode: Logging is Off.")





def msg(s, sender, ident, host, channel, text):
	log("%s!%s %s :%s" % (sender, host, channel, text))
	



def close(s = None):
	l.close()
