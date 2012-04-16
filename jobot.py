#!/usr/bin/env python

# Copyright 2009-2011 Joey

# This file is part of Jobot.
#
#    Jobot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Jobot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Jobot.  If not, see <http://www.gnu.org/licenses/>.
#


import imp
import sys
import traceback

def decode(bytes): 
	try:
		text = bytes.decode('utf-8')
	except UnicodeDecodeError: 
		try:
			text = bytes.decode('iso-8859-1')
		except UnicodeDecodeError: 
			text = bytes.decode('cp1252')
	
	return text

	
	
	
	
def reload(plugins):

	#pluginPath = sys.path[0] + "/plugins/"
	
	for p in plugins:
		if p not in sys.modules: 
			print('Module', p, 'does not exist in sys.modules.')
			continue
		try:
			imp.reload(sys.modules[p])
		except:
			traceback.print_exc()

	
	
	
def init(prompt=None, idleFunc=None):
	import time
	import threading
	import os
	import sys
	import imp
	import traceback
	import builtins
	import socket
	import ssl
	import configparser
	from glob import glob

	if not prompt:
		prompt = builtins.input

	# TODO: switch to ConfigParser, redesign plugin interface.
	#config = configparser.ConfigParser()
	#config.read("bot.ini")
	
	
	HOST = "irc.foonetic.net"
	PORT = 6667
	#HOST = "127.0.0.1" #stunnel loopback
	#PORT = 5000 #stunnel port
	plugins = []



	
	pluginPath = sys.path[0] + "/plugins/"

	sys.path.append(pluginPath)


	import meta
	meta.init(None)
	
	# save the prompt function for everyone to use
	meta.prompt = prompt

	def debug():
		if 'debug' in meta.conf:
			return meta.conf["debug"]
		
		
	
	pLen = len(pluginPath)
	pluginsL = glob(pluginPath+"*.py")


	
	for plugin in pluginsL:
		pName = plugin[pLen : -3]
		
		#dont reload the meta module
		if pName == "meta": continue
		
		try:
			fm, pm, dm = imp.find_module(pName, [pluginPath])
		except:
			print("Error: Could not find plugin:", pName)
			traceback.print_exc()
		else:
			try:
				print('Loading Plugin: ', pName, sep='',end='')
				mod = imp.load_module(pName, fm, pm, dm)
			except:
				print("\nError: Could not load plugin:", pName)
				traceback.print_exc()
			else:
				plugins.append( mod )
				print('.....Done')
			finally:
				if fm: fm.close()



	

	class botThread(threading.Thread):
		
		
		def run(self):
			
			if not meta.conf['autostart']:
				meta.prompt('\nPress Enter to connect.\n')
				
			print("Connecting to:", HOST, PORT)
			
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#ssl_s = ssl.wrap_socket(s)
			s.connect((HOST, PORT))
			
			meta.send(s, "NICK %s\r\nUSER %s \"%s\" \"%s\" :%s\r\n" % (meta.conf['nick'], meta.conf['ident'], meta.conf['ident'], meta.conf['ident'], meta.conf['realname']))
			meta.send(s, "MODE %s +B\r\n" % meta.conf['nick'])
			
			
			# This is for plugins that require objects to be created
			# in the calling thread.
			for plugin in plugins:
				if 'init' in plugin.__dict__:
					plugin.init(s)
			
			
			
			while not meta.quit:
				
				readbuffer = ""
				
				while True:
					
					temp = decode(s.recv(4096))#.decode("utf-8", "ignore")
					#temp = decode(ssl_s.read(4096))#.decode("utf-8", "ignore")
					readbuffer = readbuffer + temp
					
					if len(temp) < 4096: break
					
				# unexpected socket close
				if not readbuffer:
					break
					
				
				readbuffer = readbuffer.split("\r\n")
				
				for line in readbuffer:
					#line = line.rstrip()
					# dont mess with empty lines
					if not line: continue
					parseMsg(s, line)
					
				
			
			
			# quit was issued
			print("Shutting Down...\n")
			
			# run all closing module functions
			for plugin in plugins:
				if 'close' not in plugin.__dict__: continue
				try:
					plugin.close(s)
				except:
					traceback.print_exc()
			
			meta.send(s, "QUIT :Goodbye\r\n")
			try:
				s.close()
				print("Connection closed.")
			except:
				print("Connection alread closed.")
				#stdin.stderr.write("Socket already closed!")
			
			for plugin in plugins:
				if 'shutdown' not in plugin.__dict__: continue
				try:
					plugin.shutdown()
				except:
					traceback.print_exc()



	def parseMsg(s, rawMsg):
		if rawMsg[0] == ':':
			orgSplit = rawMsg.find('!',1)
			orgEnd = rawMsg.find(' ',1)
			
			if orgEnd == -1: orgEnd = len(rawMsg)
			
			if orgSplit != -1 and orgSplit < orgEnd:
				orgName = rawMsg[1 : orgSplit]
				orgHost = rawMsg[orgSplit+1 : orgEnd]
				
				Iend = orgHost.find('@')
				
				if Iend != -1:
					orgIdent = orgHost[: Iend]
					orgHost = orgHost[Iend+1 :]
					
			else:
				orgName = rawMsg[1 : orgEnd]
				orgIdent = ""
				orgHost = ""
			
			rawMsg = rawMsg[orgEnd+1 :]
		else:
			orgName = ""
			orgIdent = ""
			orgHost = ""
			
		cmdEnd = rawMsg.find(' ')
		if cmdEnd != -1:
			cmd = rawMsg[: cmdEnd].upper()
			params = rawMsg[cmdEnd+1 :]
		else:
			cmd = rawMsg.upper()
			params = ""
		
		
		
		#http://docs.python.org/3.1/library/functions.html?highlight=filter#filter
		#http://docs.python.org/3.1/library/functions.html?highlight=map#map
		
		for plugin in plugins:
			if 'handle' in plugin.__dict__:
				try:
					t = plugin.handle(s, orgName, orgIdent, orgHost, cmd, params)
					if t == False: break
				except:
					traceback.print_exc()
				
		if cmd == "PRIVMSG" or cmd == "NOTICE":
			senderEnd = params.find(' ')
			sender = params[: senderEnd]
			text = params[senderEnd+2 :]
			
			if len(text) == 0:
				return
			
			
		
		if cmd == "NOTICE":
			for plugin in plugins:
				if 'notice' in plugin.__dict__:
					try:
						t = plugin.notice(s, orgName, orgIdent, orgHost, sender, text)
						if t == False: break
					except:
						traceback.print_exc()
			
		
		elif cmd == "PRIVMSG":
			for plugin in plugins:
				if 'msg' in plugin.__dict__:
					try:
						t = plugin.msg(s, orgName, orgIdent, orgHost, sender, text)
						if t == False: break
					except:
						traceback.print_exc()
				
			
		
		if meta.reload != []:
			
			reload(meta.reload)
			
			meta.reload = []
		






	return botThread()

	print("Starting Bot Thread")
	bot = botThread()
	bot.start()




	
	if idleFunc:
		idleFunc()

	bot.join()




	if debug():
		prompt('>>> Done <<<')


if __name__ == "__main__":
	
	bot = init()
	bot.start()
	