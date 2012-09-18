## Copyright 2009-2012 Joey
## 
## Jobot is released under Affero GPL. Please read the license before continuing.
## 
## The latest source can be found here:
##	 https://github.com/MOSW/wallybot
##
from http.server import *
import http.cookies
#import meta           ## no direct management at this point
import traceback
import threading
import re
import sqlite3
import urllib.parse
import os
import mimetypes
from datetime import datetime
import time
import binascii
import hashlib
import random
import json
from configparser import ConfigParser
import runpy

## check whether they are set yet or not (module could be reloaded during execution)
try: httpd
except: httpd = None
try: server
except: server = None
try: conf
except: conf = None



sessions = {}


WSESSID = ''
DOC_ROOT = ''
	
	
def esc(text):
	return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def compURL(base, params):
	if not params: return base
	
	p = []
	for k in params:
		p += [k +'='+ urllib.parse.quote_plus(str(params[k]))]
		
	return base +'?'+ '&'.join(p)
	
	
def size_fmt(num, prec=1):
    for x in [' bytes','kb','mb','gb','tb']:
        if num < 1024.0:
            return ("%3."+str(prec)+"f%s") % (num, x)
        num /= 1024.0

	
	
class serverThread(threading.Thread):
		
		def run(self):
			global httpd
			httpd = HTTPServer((conf.get('httpd','address'), conf.getint('httpd','port')), MyHandler)
			httpd.serve_forever()

def loadConf():
	global conf, WSESSID, DOC_ROOT, DIR_INDX, RUN_PY
	
	## load configuration
	conf = ConfigParser()
	conf.read('httpd.conf')
	
	if conf.has_option('httpd', 'WSESSID'):
		WSESSID = conf.get('httpd', 'WSESSID', 'WSESSID')
	else:
		WSESSID = 'WSESSID'
		
	if conf.has_option('httpd', 'document_root'):
		DOC_ROOT = conf.get('httpd', 'document_root')
	else:
		DOC_ROOT = './htdocs/'
		
	if conf.has_option('httpd', 'dir_index'):
		DIR_INDX = conf.get('httpd', 'dir_index').split()
	else:
		DIR_INDX = []
		
	if conf.has_option('httpd', 'run_py'):
		RUN_PY = conf.getboolean('httpd', 'run_py')
	else:
		RUN_PY = False
	
	return
	
def init(s=None):
	global httpd, server
	
	loadConf()
	
	## start the server in its own thread
	server = serverThread()
	server.start()
	
def restart():
	shutdown()
	init()
	return
	
	
def shutdown():
	global MyHandler, httpd, server
	
	httpd.shutdown()
	server.join()
	

class MyHandler(BaseHTTPRequestHandler):
	server_version = 'wally - Powered by Skynet'
	querystr = ''
	post = {}
	get = {}
	set_cookies = http.cookies.SimpleCookie()
	cookies = http.cookies.SimpleCookie()
	session = {}
	sessid = ''
	
	
	css = '<link rel="stylesheet" href="/style.css" type="text/css" />'
	js = """<script type="text/javascript" src="/jquery-1.8.1.min.js"></script>
			<script type="text/javascript" src="/wally-web.js"></script>"""
	
	
	
	##
	## Give me a fancy server version! Tell no one of server software
	##
	def version_string(s):
		return s.server_version
	
	
	
	## 
	## Gimme an Error!
	##
	def e(s, errno, short="", msg=""):
		s.send_response(int(errno))
		s.send_header("Content-type", "text/html;charset=utf-8")
		s.end_headers()
		
		s.send("<html><head><title>wally - %d</title>%s%s</head>" % (errno, s.css, s.js))
		s.send("<body><h1>%d %s</h1>"%(errno,esc(short)))
		if msg:
			s.send("<p>%s</p>" % (esc(msg)))
		s.send("<p>Request path: %s</p>" % s.path)
		s.send("</body></html>")
		return
	
	
	
	## 
	## Error page: 404
	##
	def e404(s, msg=""):
		return s.e(404,"Page Not Found", msg)
	
	
	
	## 
	## Error page: 500
	##
	def e500(s, msg=""):
		return s.e(500,"Bork", msg)
	
	
	
	
	
	##
	## home UI
	##
	def home(s):
		s.session_start()
		
		if not s.require_user(): return
		
		
		
		s.send_response(200)
		s.send_header("Content-type", "text/html;charset=utf-8")
		s.send_header("Cache-Control", "no-cache, must-revalidate")
		s.send_header("Pragma", "no-cache")
		s.end_headers()
		
		s.send("<html><head><title>wally - factoids</title>%s%s</head>" % (s.css, s.js))
		s.send("<body><h2 class=\"it\">wally</h2>")
		
		
		s.send("<span class=\"wbub1\"></span><span class=\"wbub2\"></span><span class=\"wbub3\"></span>")
		s.send("<span class=\"wbub\" title=\"\"> </span>")
		
		s.send("""
			<form id="sf">
				<input type="text" placeholder="ID" id="id" name="id" />
				<span style="font-size:0.8em;"> | </span>
				<input type="text" placeholder="Nickname" id="nick" name="nick" />
				<span style="font-size:0.8em;"> | </span>
				<input type="text" placeholder="Search" id="search" name="search" />
				<input type="submit" value="Apply" />
				<input type="reset" value="Clear" />
				<div class="extra" style="text-align:center;">
					<input type="text" style="width:90px" placeholder="Deleter" id="deleter" name="deleter" />
					&nbsp;|&nbsp;
					<label style="font-size:0.8em;" title="Applies to Nick and Deleter fields" for="exactnick">Exact Nick:</label>
					<input type="checkbox" title="Applies to Nick and Deleter fields" checked="checked" name="exactnick" id="exactnick" /> 
					&nbsp;|&nbsp;
					<label style="font-size:0.8em;" for="sfind">Search <i>Find</i>:</label>
					<input type="checkbox" checked="checked" name="sfind" id="sfind" />
					&nbsp;|&nbsp;
					<label style="font-size:0.8em;" for="sreply">Search <i>reply</i>:</label>
					<input type="checkbox" checked="checked" name="sreply" id="sreply" />
				</div>
				</div>
				<span class="more" title="Show More Options"><span></span></span>
			</form>""")
			
		s.send("<div class=\"frb\">")
			
		s.send("""<div class="tlinks"><a href="factoids" title="factoids" class="tab"><span class="fbut">Factoids<span class="factoids c">0</span></span></a>
				&nbsp;
				<a href="del_factoids" title="del_factoids" class="tab"><span class="fbut">Deleted<span class="del_factoids c">0</span></span></a>""")
		
		s.send("""<span class="sort">Sort By: <a href="#" title="id" class="active">Time Added</a><a href="#" title="last_said">Last Said</a><a href="#" title="find">Find</a><a href="#" title="inkling">Inkling</a><a href="#" title="verb">Verb</a><a href="#" title="reply">Reply</a><a href="#" title="nick">Nick</a></span>""")
		
		s.send("""<span class="sett_links">
				<a class="users" href="#users">Users</a>
				<!--<a class="settings" href="#settings">Settings</a>-->
				&nbsp;|&nbsp;
				<a class="logout" href="/logout">Logout</a>
			</span>""")
			
		s.send("</div>")# tlinks
		
		s.send("<div class=\"flist\" width=\"100%\" height=\"350px\"></div>")
		
		s.send("<span class=\"showing\"></span>")
		s.send("<span class=\"page_control\"><a class=\"prev\" href=\"#previous_page\">previous</a><a class=\"next\" href=\"#next_page\">next</a></span>")
		
		s.send("""<div class="userlistw">
				<div class="userlist"></div>
				<span class="adduser">
					<span class="adduserform">
						<input class="user" type="text" style="width:70px;" placeholder="User" />&nbsp;
						<input class="pass" type="password" style="width:90px;" placeholder="Password">&nbsp;
						<input class="level" type="text" placeholder="Level*" style="width:50px;">&nbsp;
						<a href="#create_user" class="createuser">Create</a>&nbsp;
					</span>
					<a class="adduserlnk" href="#">+ Add User</a>
				</span>
				<br clear="both" />
			</div>""")
		
		s.send("</div>")# /frb
		
		s.send("</body></html>")
		
		return
	
	
	
	
	
	##
	## list users
	##
	def ajax_userlist(s):
		s.session_start()
		
		if not s.require_user(1): return
		
		resp = {'error':0,'success':0,'users':[]}
		
		s.send_response(200)
		s.send_header("Content-type", "text/html;charset=utf-8")
		s.send_header("Cache-Control", "no-cache, must-revalidate")
		s.send_header("Pragma", "no-cache")
		s.end_headers()
	
		conn = sqlite3.connect('bucket.sql', timeout=20)
		cur = conn.cursor()
		
		cur.execute("""SELECT `id`,`user`,`nick`,`ident`,`host`,`level` FROM `users`""")
		
		resp['users'] = cur.fetchall()
		resp['success'] = 1
		
		s.send(json.dumps(resp))
		
		conn.close()
		return
	
	
	
	
	
	##
	## save a changes to a user
	##
	def ajax_saveuser(s):
		s.session_start()
		
		if not s.require_user(20): return
		
		resp = {'error':0,'success':0}
		
		s.send_response(200)
		s.send_header("Content-type", "text/html;charset=utf-8")
		s.send_header("Cache-Control", "no-cache, must-revalidate")
		s.send_header("Pragma", "no-cache")
		s.end_headers()
	
		conn = sqlite3.connect('bucket.sql', timeout=20)
		cur = conn.cursor()
		
		q = []
		p = []
		
		if 'id' not in s.post:
			resp['error'] = 1
			s.send(json.dumps(resp))
			return
		
		if 'user' in s.post and s.post['user']:
			q += ['`user`=?']
			p += [s.post['user']]
			
		if 'pass' in s.post and s.post['pass'] and (s.post['id'] == str(s.session['userid']) or s.session['userlevel']>=50):
			q += ['`pass`=?']
			p += [hashlib.md5(bytes(s.post['pass']+'94--s9g', 'utf8')).hexdigest()]
			
		if 'nick' in s.post and s.post['nick']:
			q += ['`nick`=?']
			p += [s.post['nick']]
			
		if 'ident' in s.post and s.post['ident']:
			q += ['`ident`=?']
			p += [s.post['ident']]
			
		if 'host' in s.post and s.post['host']:
			q += ['`host`=?']
			p += [s.post['host']]
			
		if 'level' in s.post and s.post['level']:
			q += ['`level`=?']
			p += [s.post['level']]
		
		if not q:
			resp['error'] = 2
			s.send(json.dumps(resp))
			return
		
		
		p += [s.post['id']]
		
		
		cur.execute("""UPDATE `users` SET """+', '.join(q)+""" WHERE `id`=?""", p)
		
		resp['success'] = cur.rowcount
		conn.commit()
		
		s.send(json.dumps(resp))
		
		conn.close()
		return
	
	
	
	
	##
	## save a changes to a user
	##
	def ajax_newuser(s):
		s.session_start()
		
		if not s.require_user(20): return
		
		resp = {'error':0,'success':0,'temppass':''}
		
		s.send_response(200)
		s.send_header("Content-type", "text/html;charset=utf-8")
		s.send_header("Cache-Control", "no-cache, must-revalidate")
		s.send_header("Pragma", "no-cache")
		s.end_headers()
	
		conn = sqlite3.connect('bucket.sql', timeout=20)
		cur = conn.cursor()
		
		
		
		if 'user' not in s.post or not s.post['user']:
			resp['error'] = 1
			s.send(json.dumps(resp))
			return
		else:
			user = s.post['user']
		
		
		if 'pass' not in s.post or not s.post['pass']:
			resp['error'] = 2
			s.send(json.dumps(resp))
			return
		else:
			passwd = hashlib.md5(bytes(s.post['pass']+'94--s9g', 'utf8')).hexdigest()
		
		
		if 'nick' in s.post and s.post['nick']:
			nick = s.post['nick']
		else:
			nick = ''
			
		if 'ident' in s.post and s.post['ident']:
			ident = s.post['ident']
		else:
			ident = ''
			
		if 'host' in s.post and s.post['host']:
			host = s.post['host']
		else:
			host = ''
			
		if 'level' in s.post and s.post['level']:
			lvl = s.post['level']
		else:
			lvl = 0 # read only
		
		
		
		
		cur.execute("""INSERT INTO `users` (`user`,`pass`,`nick`,`ident`,`host`,`level`) VALUES (?, ?, ?, ?, ?, ?)""", (user, passwd, nick, ident, host, lvl))
		
		resp['success'] = cur.lastrowid
		conn.commit()
		
		s.send(json.dumps(resp))
		
		conn.close()
		return
	
	
	
	
	
	##
	## delete a user
	##
	def ajax_deluser(s):
		s.session_start()
		
		if not s.require_user(20): return
		
		resp = {'error':0,'success':0}
		
		s.send_response(200)
		s.send_header("Content-type", "text/html;charset=utf-8")
		s.send_header("Cache-Control", "no-cache, must-revalidate")
		s.send_header("Pragma", "no-cache")
		s.end_headers()
	
		conn = sqlite3.connect('bucket.sql', timeout=20)
		cur = conn.cursor()
		
		
		if 'id' not in s.post or not s.post['id']:
			resp['error'] = 1
			s.send(json.dumps(resp))
			return
		
		
		## you are not allowed to delete yourself
		if s.post['id'] == str(s.session['userid']) or s.post['id'] == '1':
			resp['error'] = 2
			s.send(json.dumps(resp))
			return
		
		cur.execute("""DELETE FROM `users` WHERE `id`=?""",(s.post['id'],))
		
		if cur.rowcount:
			resp['success'] = cur.rowcount
		else:
			resp['error'] = 3
			
		conn.commit()
		
		s.send(json.dumps(resp))
		
		conn.close()
		return
	
	
	
	
	
	##
	## retrieve a random factoid to be used as a quote
	##
	def ajax_stats(s):
		s.session_start()
		
		if not s.require_user(): return
		
		s.send_response(200)
		s.send_header("Content-type", "text/html;charset=utf-8")
		s.send_header("Cache-Control", "no-cache, must-revalidate")
		s.send_header("Pragma", "no-cache")
		s.end_headers()
		
		resp = {'factoids':0, 'del_factoids':0}
		
		conn = sqlite3.connect('bucket.sql', timeout=20)
		cur = conn.cursor()
		
		cur.execute("""SELECT COUNT(`id`) FROM `factoids`""")
		
		count = cur.fetchone()
		if count:
			resp['factoids'] = count[0]
		else:
			resp['factoids'] = 0
		
		
		cur.execute("""SELECT COUNT(`id`) FROM `del_factoids`""")
		
		count = cur.fetchone()
		if count:
			resp['del_factoids'] = count[0]
		else:
			resp['del_factoids'] = 0
		
		
		s.send(json.dumps(resp))
		
		conn.close()
		return
	
	
	
	
	##
	## retrieve a random factoid to be used as a quote
	##
	def ajax_quote(s):
		s.session_start()
		
		if not s.require_user(): return
		
		s.send_response(200)
		s.send_header("Content-type", "text/html;charset=utf-8")
		s.send_header("Cache-Control", "no-cache, must-revalidate")
		s.send_header("Pragma", "no-cache")
		s.end_headers()
	
		conn = sqlite3.connect('bucket.sql', timeout=20)
		cur = conn.cursor()
		
		cur.execute("""SELECT `id`,`nick`,`tidbit` FROM `factoids` WHERE `verb`='<reply>' ORDER BY RANDOM() LIMIT 1""")
		
		
		## why itch? idk..
		itch = cur.fetchone()
		
		#json.dump(itch, s.wfile)
		s.send(json.dumps(itch))
		
		conn.close()
		return
	
	
	
	
	
	##
	## save a factoid that has been edited
	##
	def ajax_save(s):
		s.session_start()
		
		if not s.require_user(): return
		
		resp = {'error':0,'success':0}
		
		s.send_response(200)
		s.send_header("Content-type", "text/html;charset=utf-8")
		s.send_header("Cache-Control", "no-cache, must-revalidate")
		s.send_header("Pragma", "no-cache")
		s.end_headers()
	
		conn = sqlite3.connect('bucket.sql', timeout=20)
		cur = conn.cursor()
		
		
		if 'type' not in s.post or s.post['type'] not in ['factoids', 'del_factoids']:
			resp['error'] = 1
			s.send(json.dumps(resp))
			return
		
		if 'find' not in s.post:
			resp['error'] = 2
			s.send(json.dumps(resp))
			return
			
		if 'inkling' not in s.post:
			resp['error'] = 3
			s.send(json.dumps(resp))
			return
			
		if 'verb' not in s.post:
			resp['error'] = 4
			s.send(json.dumps(resp))
			return
			
		if 'reply' not in s.post:
			resp['error'] = 5
			s.send(json.dumps(resp))
			return
		
		
		
		cur.execute("""UPDATE `"""+s.post['type']+"""` SET `find`=?, `inkling`=?, `verb`=?, `tidbit`=? WHERE `id`=?""", (s.post['find'], s.post['inkling'], s.post['verb'], s.post['reply'], s.post['id']))
		
		resp['success'] = cur.rowcount
		conn.commit()
		
		s.send(json.dumps(resp))
		
		conn.close()
		return
	
	
	
	
	##
	## return a list of factoids formatted in json
	##
	def ajax_list(s):
		s.session_start()
		
		if not s.require_user(): return
		
		
		s.send_response(200)
		s.send_header("Content-type", "text/html;charset=utf-8")
		s.send_header("Cache-Control", "no-cache, must-revalidate")
		s.send_header("Pragma", "no-cache")
		s.end_headers()
		
		
		## base query to be added onto
		q = ''
		sel = 'SELECT * FROM '
		p = []
		count_sel = 'SELECT COUNT(`id`) FROM '
		count_par = []
		resp = {'error':0,'rows':[],'count':0,'from':''}
		
		
		
		
		
		if 'from' in s.get and s.get['from'] in ['factoids','del_factoids']:
			q += '`'+s.get['from']+'`'
			resp['from'] = s.get['from']
		else:
			resp['error'] = 1
			s.send(json.dumps(resp))
			return
		
		## create where clause
		w = ''
		if 's' in s.get and s.get['s']:
		
			if w: w += ' AND'
			
			search = []
			
			if 'sfind' in s.get and s.get['sfind'] == 'true':
				search += ['`find` LIKE ?']
				p += ['%'+s.get['s']+'%']
				
			if 'sreply' in s.get and s.get['sreply'] == 'true':
				search += ['`tidbit` LIKE ?']
				p += ['%'+s.get['s']+'%']
				
			if search:
				w += ' ('+' OR '.join(search)+')'
				
			
		
		## nick search
		if 'nick' in s.get and s.get['nick']:
		
			if w: w += ' AND'
			
			w += " `nick` LIKE ?"
			if 'exactnick' in s.get and s.get['exactnick']=='true':
				p += [s.get['nick']]
			else:
				p += ['%'+s.get['nick']+'%']
			
		## deleter search
		if 'from' in s.get and s.get['from']=='del_factoids' and 'deleter' in s.get and s.get['deleter']:
		
			if w: w += ' AND'
			
			w += " `del_nick` LIKE ?"
			if 'exactnick' in s.get and s.get['exactnick']=='true':
				p += [s.get['deleter']]
			else:
				p += ['%'+s.get['deleter']+'%']
		
		
		## ID select
		if 'id' in s.get and s.get['id']:
			
			if w: w += ' AND'
			
			w += " `id`=?"
			p += [s.get['id']]
		
		
		## append the where clause to the query
		if w:
			q += ' WHERE'+w
			
		## create order clause
		orders = ['id', 'find', 'inkling', 'verb', 'tidbit', 'nick', 'last_said']
		
		if 'by' in s.get and s.get['by'] in orders:
			q += ' ORDER BY `%s`' % (s.get['by'],)
			
			if 'ord' in s.get and s.get['ord'] in ['DESC','ASC']:
				q += ' %s' % (s.get['ord'],)
			else:
				q += ' DESC'
		else:
			q += ' ORDER BY `id` DESC'
		
		## Extract current query before limits/offsets are added for use in the count
		count_sel += q
		count_par = p[:]
		
		## paging
		if 'limit' in s.get and int(s.get['limit']):
			q += ' LIMIT ?'
			limit = int(s.get['limit'])
			p += [limit]
		else:
			q += ' LIMIT 100'
			limit = 100
			
		if 'p' in s.get and int(s.get['p']):
			q += ' OFFSET ?'
			page = int(s.get['p'])
			p += [(page-1)*limit]
		else:
			page = 1
		
		
		conn = sqlite3.connect('bucket.sql', timeout=20)
		cur = conn.cursor()
		
		
		## fetch rows
		cur.execute(sel+q, p)
		
		resp['rows'] = cur.fetchall()
		
		
		## fetch row count for use in pagination
		cur.execute(count_sel, count_par)
		
		count = cur.fetchone()
		if count:
			resp['count'] = count[0]
		else:
			resp['count'] = 0
		
		## send rows and count back via json
		s.send(json.dumps(resp))
		
		
		conn.close()
		return


	
	
	
	##
	## process an ajax delete request
	##
	def ajax_del(s):
		return e404()
		s.session_start()
		
		if not s.require_user(1): return
		
		
		s.send_response(200)
		s.send_header("Content-type", "text/html;charset=utf-8")
		s.send_header("Cache-Control", "no-cache, must-revalidate")
		s.send_header("Pragma", "no-cache")
		s.end_headers()
		
		if 'id' not in s.post or not s.post['id']:
			s.send(json.dumps({'success':0,'error':1}))
			return
			
		if 'type' not in s.post or not s.post['type']:
			s.send(json.dumps({'success':0,'error':2}))
			return
		
		conn = sqlite3.connect('bucket.sql', timeout=20)
		cur = conn.cursor()
		
		if s.post['type'] == 'del_factoids':
			#s.del_factoid(conn, cur, 'del_factoids', s.post['id'])
			pass
		elif s.post['type'] == 'factoids':
			#s.forget_factoid(conn, cur, s.post['id'])
			pass
		else:
			s.send(json.dumps({"success":0,"error":3}))
		
		
		s.send(json.dumps({'success':1,'error':0}))
		
		conn.close()
		
		return
	
	
	
	
	##
	## process an ajax forget request
	##
	def ajax_forget(s):
		s.session_start()
		
		if not s.require_user(): return
		
		
		s.send_response(200)
		s.send_header("Content-type", "text/html;charset=utf-8")
		s.send_header("Cache-Control", "no-cache, must-revalidate")
		s.send_header("Pragma", "no-cache")
		s.end_headers()
		
		if 'id' not in s.post or not s.post['id']:
			s.send(json.dumps({'success':0,'error':1}))
			return
			
		
		conn = sqlite3.connect('bucket.sql', timeout=20)
		cur = conn.cursor()
		
		s.forget_factoid(conn, cur, s.post['id'])
		
		s.send(json.dumps({'success':1,'error':0}))
		
		conn.close()
		
		return
	
	
	
	
	##
	## process an ajax unforget request
	##
	def ajax_unforget(s):
		s.session_start()
		
		if not s.require_user(): return
		
		
		s.send_response(200)
		s.send_header("Content-type", "text/html;charset=utf-8")
		s.send_header("Cache-Control", "no-cache, must-revalidate")
		s.send_header("Pragma", "no-cache")
		s.end_headers()
		
		if 'id' not in s.post or not s.post['id']:
			s.send(json.dumps({'success':0,'error':1}))
			return
			
		
		conn = sqlite3.connect('bucket.sql', timeout=20)
		cur = conn.cursor()
		
		s.unforget_factoid(conn, cur, s.post['id'])
		
		s.send(json.dumps({'success':1,'error':0}))
		
		conn.close()
		
		return
	
	
	
	
	##
	## delete a factoid from a given table
	##
	def del_factoid(s, conn, cur, table, id):
		if table not in ['factoids','del_factoids']: return False
		cur.execute("""DELETE FROM `%s` WHERE `id`=?"""%(table,), (id,))
		conn.commit()
		return (cur.rowcount > 0)
	
	
	
	
	##
	## move a factoid from the factoids table to del_factoids
	##
	def forget_factoid(s, conn, cur, id):
		cur.execute("""SELECT * FROM `factoids` WHERE `id`=? LIMIT 1""", (int(id),))
		
		res = cur.fetchone()
		
		if not res:
			return False
			
		
		cur.execute("""INSERT INTO 
				`del_factoids`	(`inkling`, `find`, `verb`, `tidbit`, `nick`, `editable`, `last_said`, `del_id`, `del_time`, `del_nick`, `del_ident`, `del_host`, `del_channel`) 
				VALUES		( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
				( res[1], res[2], res[3], res[4], res[5], res[6], res[7], id, time.time(), s.session['user'], '', s.client_address[0], '@web-interface' ))
		
		if not cur.lastrowid: return False
		
		return s.del_factoid(conn, cur, 'factoids', id)
	
	
	
	##
	## move a factoid from the factoids table to del_factoids
	##
	def unforget_factoid(s, conn, cur, id):
		cur.execute("""SELECT * FROM `del_factoids` WHERE `id`=? LIMIT 1""", (int(id),))
		
		res = cur.fetchone()
		
		if not res:
			return False
			
		
		cur.execute("""INSERT INTO 
				`factoids`	(`inkling`, `find`, `verb`, `tidbit`, `nick`, `editable`, `last_said`) 
				VALUES		( ?, ?, ?, ?, ?, ?, ?)""", 
				( res[1], res[2], res[3], res[4], res[5], res[6], res[7] ))
		
		if not cur.lastrowid: return False
		
		return s.del_factoid(conn, cur, 'del_factoids', id)
	
	
	
	
	##
	## Show a login page
	##
	def show_login(s):
		s.send_response(200)
		s.send_header('Content-type', 'text/html;charset=utf-8')
		s.end_headers()
		
		s.send('<html><head><title>wally - login</title>%s%s</head>'%(s.css,s.js))
		s.send('<body id="login" onload="$(\'#pass\').focus()"><center>')
		
		s.send("""<form method="post" action="/login">
				<input type="text" placeholder="Username" id="user" name="user" />
				<input type="password" placeholder="Password" id="pass" name="pass" />
				<input type="submit" value="Login" />
			</form>""")
		
		s.send('</center></body></html>')
		return False
	
	
	
	
	##
	## Called during a login attempt
	##
	def check_login(s):
		s.session_start()
		
		if 'user' not in s.post or 'pass' not in s.post:
			return s.show_login()
		
		conn = sqlite3.connect('bucket.sql', timeout=20)
		cur = conn.cursor()
		
		
		cur.execute("""SELECT `user`,`level`,`id` FROM `users` WHERE `user`=? AND `pass`=? LIMIT 1""", (s.post['user'], hashlib.md5(bytes(s.post['pass']+'94--s9g', 'utf8')).hexdigest()))
		
		res = cur.fetchone()
		
		if res:
			s.session['user'] = res[0]
			s.session['userlevel'] = res[1]
			s.session['userid'] = res[2]
			s.send_response(302)
			s.send_header('Content-type', 'text/html;charset=utf-8')
			s.send_header('Location', '/')
			s.end_headers()
			s.send('Login Successful. Redirecting')
			return True
		
		
		conn.close()
		# else, show login
		return s.show_login()
	
	
	##
	## log a user out 
	##
	def logout(s):
		s.session_start()
		
		if not s.logged_in():
			return s.redirect('/')
			
		del s.session['user']
		del s.session['userlevel']
		del s.session['userid']
		
		return s.redirect('/')
		
	
	
	##
	## require a user of a certain level to be logged in to continue
	##
	def require_user(s, level=0):
		return s.logged_in() and s.session['userlevel'] >= level or s.show_login()
	
	
	
	
	##
	## is a user logged in? dur
	##
	def logged_in(s):
		return 'user' in s.session and s.session['user']
	
	
	
	
	
	##
	## redirect a page BEFORE any headers are sent
	##
	def redirect(s, loc, msg="Redirecting."):
		s.send_response(302)
		s.send_header('Content-type', 'text/html;charset=utf-8')
		s.send_header('Location', loc)
		s.end_headers()
		s.send(msg)
		return
	
	
	
	
	##
	## woo code comments...
	##
	def hasHeader(s, header):
		return header in s.headers
	
	
	
	##
	## load cookies from the current request header 
	##
	def loadCookies(s):
		if 'Cookie' in s.headers:
			s.cookies.load(s.headers['Cookie'])
		return
	
	
	
	##
	## overwrite current to send cookies before headers close
	##  - sending cookies prematurely will UPSET THE NATURAL ORDER!!
	##
	def end_headers(s):
		for c in s.set_cookies:
			s.send_header('Set-Cookie', s.set_cookies[c].OutputString())
		return BaseHTTPRequestHandler.end_headers(s)
	
	
	
	##
	## Load session variables into the current scope
	##
	def session_start(s):
		global sessions, WSESSID
		
		if s.sessid: return
		
		if WSESSID in s.cookies and \
			s.cookies[WSESSID].value in sessions and \
			sessions[s.cookies[WSESSID].value]['ip'] == s.client_address[0]:
			
			s.sessid = s.cookies[WSESSID].value
		else:
			s.sessid = s.createSession()
			
			s.set_cookies[WSESSID] = s.sessid
		
		## ATTENTION:: s.session is a reference to sessions[s.sessid]['data']
		##             and it will remain that way so that data can be changed
		##             as long as s.session is not overwritten.
		##             Do not: `s.session = {'spam':'eggs'}`
		##             Do: `s.session['spam'] = 'eggs'`
		##             Do not overwrite s.session!
		##             Do modify s.session
		s.session = sessions[s.sessid]['data']
		return
	
	
	
	##
	## create a new unique session id and 
	##
	def createSession(s):
		global sessions, WSESSID
		
		m = hashlib.md5()
		
		m.update(bytes(str(s.client_address)+"_+SD65"+str(s.headers)+str(random.random()),'utf8'))
		h = m.hexdigest()
		
		while h in sessions:
			m.update(bytes(str(random.random()),'utf8'))
			h = m.hexdigest()
			
		sessions[h] = {
			'ip':			s.client_address[0],
			'useragent':	'User-Agent' in s.headers and s.headers['User-Agent'] or '',
			'data':			{'asdf':1}
			}
		return h
	
	
	def send(s, text):
		return s.wfile.write(bytes(text,'utf8'))
	
	
	##
	## HEAD request - for fetching just the header and no content
	##
	def do_HEAD(s):
		s.send_response(200)
		s.send_header("Content-type", "text/html;charset=utf-8")
		s.end_headers()
		return
	
	
	
	## 
	## GET request
	##
	def do_GET(s):
		return s.magic()
	
	
	
	## 
	## POST request
	##
	def do_POST(s):
		return s.magic()
	
	
	
	##
	## parse gets, posts then dispatch
	##
	def magic(s):
		## apparently, the server saves the instances and reuses them
		s.querystr = ''
		s.post = {}
		s.get = {}
		s.set_cookies = http.cookies.SimpleCookie()
		s.cookies = http.cookies.SimpleCookie()
		s.session = {}
		s.sessid = ''
		
		## COOKIE MONSTER!! OMNOMNOMONOMNOM
		s.loadCookies()
		
		
		if s.command == "POST" and 'Content-Length' in s.headers:
			## read in POST vars
			p = s.rfile.read(int(s.headers['Content-Length'])).decode('utf8')
			p = str(p).split('&')
			
			for i in range(len(p)):
				a = p[i].split('=', 1)
				if a and len(a) == 2:
					s.post[urllib.parse.unquote_plus(a[0])] = urllib.parse.unquote_plus(a[1])
				elif a:
					s.post[urllib.parse.unquote_plus(a[0])] = ""
			
		
		
		## save the whole url
		s.url = s.path
		
		## split the request string up into its parts
		r = re.match(r"^(.+?)(?:\?(.*?))?$", s.path)
		
		if not r:
			return do_500(s, "Unable to process your request")
			
		## save!
		s.path, s.querystr = r.groups()
		
		## Gimme dem GET vars
		if s.querystr:
			g = str(s.querystr).split('&')
			
			for i in range(len(g)):
				a = g[i].split('=', 1)
				if a and len(a) == 2:
					s.get[urllib.parse.unquote_plus(a[0])] = urllib.parse.unquote_plus(a[1])
				elif a:
					s.get[urllib.parse.unquote_plus(a[0])] = ""
			
		
		return s.dispatch()
	
	
	
	def dispatch(s):
		"""Respond to a GET request."""
		
		
		if s.path == "/":
			# show the main interface
			s.home()
			return
		elif s.path == "/login/" or s.path == "/login":
			# login
			s.check_login()
			return
		elif s.path == "/logout/" or s.path == "/logout":
			# logout
			s.logout()
			return
		elif s.path[:3] == "/f/" or s.path == "/f":
			# regular factoids listing
			s.factoid_list()
			return
		elif s.path[:3] == "/d/" or s.path == "/d":
			# deleted factoids listing
			s.deleted_list()
			return
		elif s.path == "/ajax/del":
			# delete factoid
			s.ajax_del()
			return
		elif s.path == "/ajax/save":
			# delete factoid
			s.ajax_save()
			return
		elif s.path == "/ajax/list":
			# list factoids
			s.ajax_list()
			return
		elif s.path == "/ajax/stats":
			# fetch row counts
			s.ajax_stats()
			return
		elif s.path == "/ajax/quote":
			# fetch random quote
			s.ajax_quote()
			return
		elif s.path == "/ajax/forget":
			# forget a factoid
			s.ajax_forget()
			return
		elif s.path == "/ajax/unforget":
			# unforget a factoid
			s.ajax_unforget()
			return
		elif s.path == "/ajax/userlist":
			# generate and return userlist
			s.ajax_userlist()
			return
		elif s.path == "/ajax/saveuser":
			# save changes to a user
			s.ajax_saveuser()
			return
		elif s.path == "/ajax/newuser":
			# add a new user
			s.ajax_newuser()
			return
		elif s.path == "/ajax/deluser":
			# delete a user
			s.ajax_deluser()
			return
		
		s.path = urllib.parse.unquote_plus(s.path)
		
		s.path = s.path.replace('../','').\
						replace('..\\','').\
						replace('./','').\
						replace('.\\','').\
						lstrip('/\\')
		
		
		## index page if referring to a directory
		if os.path.isdir(DOC_ROOT+s.path):
			if s.path and s.path[-1] not in ['/','\\']:
				s.path += '/'
			for ndx in DIR_INDX:
				if os.path.isfile(DOC_ROOT+s.path + ndx):
					s.path += ndx
					break
		
		
		## directory indexing
		if os.path.isdir(DOC_ROOT+s.path):
			if not conf.getboolean('httpd', 'indexing'):
				return s.e404()
			else:
				s.send_response(200)
				s.send_header("Content-type", "text/html;charset=utf-8")
				#s.send_header("Cache-Control", "no-cache, must-revalidate")
				#s.send_header("Pragma", "no-cache")
				s.end_headers()
				s.send('<h2>Directory Index</h2>')
				s.send('<div>Path: %s</div>'%(s.path,))
				s.send('<br />')
				for fi in os.listdir(DOC_ROOT+s.path):
					# dont show hidden files
					if fi[0] == '.': continue
					s.send('<a href="./%s">%s</a> - %s<br />'%(fi, fi, size_fmt(os.stat(DOC_ROOT+s.path+fi).st_size)))
				return
		
		
		## no hidden files for you
		fn = os.path.basename(s.path)
		if fn and fn[0] == '.':
			return s.e404()
		
		
		## execute a python file
		if RUN_PY and os.path.isfile(DOC_ROOT+s.path) and s.path[-3:] == '.py':
			
			
			with open(DOC_ROOT+s.path, 'r') as f:
				source = f.read()
				
			#print(source)
			## attempt to compile the source and run it
			try:
				o = compile(source, DOC_ROOT+s.path, 'exec')
				exec(o)
			except:
				traceback.print_exc()
				return
			
			return
		
		## display a static file
		if os.path.isfile(DOC_ROOT+s.path):
			s.send_response(200)
			
			mime = mimetypes.guess_type(s.path)[0]
			
			if mime:
				s.send_header("Content-type", mime)
			else:
				s.send_header("Content-type", 'text/plain')
			
			# gather file information
			st = os.stat(DOC_ROOT+s.path)
			
			# send file size
			s.send_header("Content-Length", st.st_size)
			
			# send modification date RFC 2822
			#s.send_header("Last-Modified", strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime(st.st_mtime)))
			
			s.end_headers()
			with open(DOC_ROOT+s.path, 'br') as f:
				while True:
					b = f.read(1024)
					if not b: break
					s.wfile.write(b)
			return
		
		return s.e404()
	
	



if __name__ == "__main__":
	try:
		init("ubersocket!")
	except:
		traceback.print_exc()
		input("Press enter to close")
