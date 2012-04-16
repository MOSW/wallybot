from tkinter import *
import traceback
import sys
import jobot
import time
import threading
import builtins


try:


	# test app in seperate thread
	class app(threading.Thread):
		
		def run(self):
			print("from test thread")
			a = ""
			while a != "stop":
				try:
					builtins.input()
					#print("written:", a)
				except:
					traceback.print_exc()
				
			
		
	

	
	# main console class
	class jobotConsole(Frame):
		
		
		# pseudo file class to be used for redirecting stdout
		class _out(object):
			def __init__(self, console):
				self.console = console
				self.encoding = "utf8"
			
			def write(self, str, tag=None):
				self.console.insert(END, str, tag)
				self.console.see(INSERT)
			
			def writelines(self, lines):
				for line in lines:
					self.write(line)
			
			def flush(self):
				pass
			
		# pseudo file class to redirect stderr
		class _err(_out):
			
			def write(self, str):
				_out.write(str, "stderr")
			
		
		
		
		
		def __init__(self, master=None):
			Frame.__init__(self, master)
			self.pack(fill=BOTH, expand=1)
			
			
			self.createWidgets()
			
			#self.top = Toplevel(master)
			#self.top.withdraw()
			
			#master.focus()
			
			self.console.stdinSem = threading.Semaphore(0)
			
			self.__stdin__ = sys.stdin
			self.__stdout__ = sys.stdout
			self.__stderr__ = sys.stderr
			
			#self.stdin = self
			
			self.stdout = self._out(self.console)
			self.stderr = self._err(self.console)
			
			#self.old_input = builtins.input
			#builtins.input = self.input
			#sys.stdin = self.stdin
			sys.stdout = self.stdout
			sys.stderr = self.stderr
			
			return
		
		
		def quit(self):
			print("QUITTING")
		def close(self):
			print("CLOSING")
		def destroy(self):
			#print("DESTROYING")
			sys.stdin = self.__stdin__
			sys.stdout = self.__stdout__
			sys.stderr = self.__stderr__
			return
		
		
		# for debugging. stdin is redirected to this class, so I wanted to know what it used.
		#def __getattr__(self, attr):
		#	print(attr)
			
			
			
		def readline(self, size=None):
			line = ""
			self.console.focus()
			#self.console.mark_set(INSERT, END)
			#self.console.insert(END, ">>> ", "stdin-pre")
			self.console.mark_set("stdio", "end-1c")
			self.console.mark_gravity("stdio", LEFT)
			self.console.reading = True
			self.console["insertwidth"] = 2
			
			
			self.console.stdinSem.acquire()
			line = self.console.get("stdio", "end-1c")
			
			if not line: line = "\n"
			#print(repr(line))
			
			self.console["insertwidth"] = 0
			self.console.reading = False
			#self.console.mark_unset(self, "stdio")
			self.console.see("insert")
			return line
		
		

		def resetoutput(self):
			if self.text.get("end-2c") != "\n":
				self.text.insert("end-1c", "\n")
			self.text.mark_set("stdio", "end-1c")
		
		def flush(self):
			pass
		
		
		# this one is for simply overwriting the input function
		def prompt(self, str=None):
			if str:
				sys.stdout.write(str)
			return self.readline()[:-1]
		
		def __print(*args):
			sys.stdout.write(' '.join(args))
		
		
		def createWidgets(self):
			self.scrollbar = Scrollbar(self, orient=VERTICAL)
			self.console = Text(self, 
						wrap=WORD,
						insertwidth=0,
						state=NORMAL,
						bd=3,
						relief=SUNKEN,
						bg="#000022",
						fg="#6666FF",
						insertbackground="#2222CC",
						width=100)
			
			self.scrollbar.config(command=self.console.yview)
			self.console.config(yscrollcommand=self.scrollbar.set)
			
			self.scrollbar.pack(side=RIGHT, anchor=NE, fill=Y)
			self.console.pack(fill=BOTH, expand=1)
			
			self.console.tag_config("stderr", foreground="#CC0000", background="#000000")
			self.console.tag_config("stdin", foreground="#00CC00")
			self.console.tag_config(">>>", foreground="#00CC99")
			
			self.console.bind("<Key>", self.keyCallback)
			self.console.bind("<Return>", self.returnCallback)
			
			
			self.console.reading = False
			
			return
		
		def keyCallback(self, e):
			if not self.console.reading: return "break"
			
			if self.console.compare(INSERT, "<", "stdio"): 
				#self.console.mark_set(INSERT, END)
				return "break"
			
			#print(e.__dict__)
			
		def returnCallback(self, e):
			if not self.console.reading: return "break"
			if self.console.compare(INSERT, "<", "stdio"): return "break"
			
			self.console.insert("insert", "\n")
			self.console.see("insert")
			
			self.console.stdinSem.release()
			#self.top.quit()
			return "break"
		
		
	if __name__ == "__main__":
		root = Tk(className="Jobot GUI")
		jConsole = jobotConsole(master=root)
		print("========= jGui 0.0.1a =========")
		bot = jobot.init(prompt=jConsole.prompt)
		bot.start()
		#app1 = app()
		#app1.start()
		#jobot.init(prompt=jConsole.prompt, idleFunc=jConsole.mainloop)
		jConsole.mainloop()
		bot.join()
	
except:
	sys.stdin = sys.__stdin__
	sys.stdout = sys.__stdout__
	sys.stderr = sys.__stderr__
	traceback.print_exc()
	input()