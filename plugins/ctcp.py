import meta
import sys
import time



if __name__ == "__main__":
	input("You opened the wrong file. This one can not run by itself.")
	sys.exit()



def msg(s, nick, ident, host, channel, text):
	
	
	if nick in meta.conf['ignore']:
		return False
	
	if text[0] != "\001": return True

	
	if text == "\001VERSION\001":
		meta.sendNotice(s, nick, "\001VERSION Jobot, written in python\001")
		return
	
	elif text == "\001TIME\001":
		meta.sendNotice(s, nick, "\001TIME "+ time.ctime() +"\001")
		return
	
	elif text[:5] == "\001PING":
		meta.sendNotice(s, nick, text)
		return
	
	