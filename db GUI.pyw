## Copyright 2009-2012 Joey
## 
## Jobot is released under Affero GPL. Please read the license before continuing.
## 
## The latest source can be found here:
##	 https://github.com/MOSW/wallybot
##
from tkinter import *
import tkinter.messagebox
import tkinter.tix
import traceback
import sqlite3


try:


	class jobotDBInterface(Frame):
		
		
		
		
		def editItem(self, itemN=None):
			if not itemN:
				itemN = int(self.lBox.curselection()[0])
			
			
			
			item = self.flist[itemN]
			
			self.idLabel['text'] = item[0]
			
			self.idEntry.delete(0, END)
			self.idEntry['state'] = NORMAL
			self.idEntry.insert(END, item[0])
			
			self.inkEntry.delete(0, END)
			self.inkEntry['state'] = NORMAL
			self.inkEntry.insert(END, item[1])
			
			self.findEntry.delete(0, END)
			self.findEntry['state'] = NORMAL
			self.findEntry.insert(END, item[2])
			
			self.verbEntry.delete(0, END)
			self.verbEntry['state'] = NORMAL
			self.verbEntry.insert(END, item[3])
			
			self.repText.delete(1.0, END)
			self.repText['state'] = NORMAL
			self.repText.insert(END, item[4])
			
			self.proCheck['state'] = NORMAL
			if item[6]:
				self.proCheck.deselect()
			else:
				self.proCheck.select()
			
			self.lastEntry.delete(0, END)
			self.lastEntry['state'] = NORMAL
			self.lastEntry.insert(END, item[7])
			
			self.authEntry.delete(0, END)
			self.authEntry['state'] = NORMAL
			self.authEntry.insert(END, item[5])
			
			self.editing = itemN
			
			
			
			print("Modifying item", itemN)
			return
		
		
		
		def deleteItem(self):
			# there can only be one item selected, so only grab the first one.
			itemN = int(self.lBox.curselection()[0])
			
			# get the real item ID from the stored list
			id = self.flist[itemN][0]
			
			# delete it!!!
			self.cur.execute("""DELETE FROM `factoids` WHERE `id`=?""", (id,))
			self.conn.commit()
			
			# remove the item from the list control
			self.lBox.delete(itemN)
			
			# delete the item from the stored list
			del self.flist[itemN]
			
			# decriment the number of facts that we hold
			self.numFacts -= 1
			
			# update the status bar with the new decremented ammount
			self.updateStatusBar()
			
			# if the item we are deleting is the one in the editor, quit editing it
			if self.editing == itemN:
				self.editReset()
			
			print("Deleted factoid", id)
			return
		
		def explicitItem(self):
			itemN = int(self.lBox.curselection()[0])
			
			item = list(self.flist[itemN])
			
			item[8] = int(not item[8])
			
			self.cur.execute("""UPDATE `factoids` SET `explicit`=? WHERE `id`=?""",
				(item[8], item[0]))
			self.conn.commit()
			
			# save the altered local list 
			self.flist[itemN] = tuple(item)
			
			# update the list control to reflect the changes
			self.updateItem(itemN)
			
			print("(un)Expliciting", itemN, "-", item[8])
			
			# toggle the protected checkbox if this item is being edited right now
			#if itemN == self.editing:
			#	self.proCheck.toggle()
			return
		
		def protectItem(self):
			# there can only be one item selected, so only grab the first one.
			itemN = int(self.lBox.curselection()[0])
			
			
			# get the actual tuple item from the stored item list and convert
			# it to a list for easy modification
			item = list(self.flist[itemN])
			
			# flip the number
			item[6] = int(not item[6])
			
			# save it to the db
			self.cur.execute("""UPDATE `factoids` SET `editable`=? WHERE `id`=?""",
				(item[6], item[0]))
			self.conn.commit()
			
			# save the altered local list 
			self.flist[itemN] = tuple(item)
			
			# update the list control to reflect the changes
			self.updateItem(itemN)
			
			# toggle the protected checkbox if this item is being edited right now
			if itemN == self.editing:
				self.proCheck.toggle()
			
			print("(un)Protecting", itemN, "-", item[6])
			
			
			return
		
		
		def queryList(self):
			QUERY = """SELECT * FROM `factoids`"""
			WHERE = ""
			
			verb = self.showVerb.get()
			showProtected = self.showProtected.get()
			
			if verb:
				WHERE = "WHERE"
				
				vl = []
				if verb == "<other>":
					vl = ["`verb`!='is' AND `verb`!='are' AND `verb`!='<reply>' AND `verb`!='<action>' AND `verb`!='<alias>'"]
				else:
					for v in verb.split():
						vl.append("`verb`='"+v+"'")
					
				WHERE += " ("+ " OR ".join(vl) +")"
				
				
			if showProtected != 0:
				if not WHERE: WHERE = "WHERE"
				elif WHERE != "WHERE": WHERE += " AND "
				
				WHERE += " `editable`={0}".format(showProtected-1)
				
				
			if self.showNick != None:
				if not WHERE: WHERE = "WHERE"
				elif WHERE != "WHERE": WHERE += " AND "
				
				WHERE += " `nick`='"+self.showNick+"'"
			
			if self.searchText:
				if not WHERE: WHERE = "WHERE"
				elif WHERE != "WHERE": WHERE += " AND "
				
				WHERE += " (`find` LIKE '"+self.searchText+"' OR `tidbit` LIKE '"+self.searchText+"')"
			
			
			# generate the item order...
			ORDER = "ORDER BY `"+self.orderBy.get()+"` "+self.orderDIR.get()
			
			#print("%s %s %s" % (QUERY, WHERE, ORDER))
			
			# perform the dance of joy
			self.cur.execute("%s %s %s" % (QUERY, WHERE, ORDER))
			self.conn.commit()
			
			# store the generated where and order clauses
			self.WHERE = WHERE
			self.ORDER = ORDER
			
			return
		
		
		
		def queryListAll(self):
			self.cur.execute("""SELECT * FROM `factoids` ORDER BY `id` """ +self.orderDIR.get())
			self.conn.commit()
			return
		
		
		def fetchList(self):
			
			self.flist = []
			
			while True:
				tempFactoid = self.cur.fetchone()
				
				if not tempFactoid: break
				
				self.flist.append(tempFactoid)
			
			return
		
		
		
		def updateFacts(self):
			self.queryList()
			self.fetchList()
			self.updateList()
			return
			
			
		
		
		
		
		
		def updateItem(self, itemN):
			
			if self.lBox.selection_includes(itemN):
				select = True
			else:
				select = False
				
			bg = self.lBox.itemcget(itemN, 'bg')
			fg = self.lBox.itemcget(itemN, 'fg')
			
			self.lBox.delete(itemN)
			self.lBox.insert(itemN, self.flist[itemN])
			
			self.lBox.itemconfig(itemN, {"bg":bg, "fg":fg})
			
			self.lBox.activate(itemN)
			
			if select:
				self.lBox.selection_set(itemN)
			
			return
		
		
		
		
		
		def updateList(self):
			
			# clear the control
			self.lBox.delete(0, END)
			
			editId = 0
			
			if self.editing > -1 and self.editing <= len(self.flist):
				editId = self.flist[self.editing][0]
			
			# create a boolean toggle for alternating row highlights
			h = False
			
			# 
			i = 0
			
			for item in self.flist:
				self.lBox.insert(END, item)
				
				
				if item[0] == editId:
					self.editing = i
				
				# highlight every other row for readabilities sake. WE ARE
				# GOING TO GET DRUNK TONIGHT! Get it? sake? ... as in the 
				# japanese liquor? ... eh
				if h:
					self.lBox.itemconfig(END, bg="#EEEEFF", fg="#000000")
				else: 
					self.lBox.itemconfig(END, bg="#FFFFFF", fg="#000000")
				
				# flip our highlighting toggle
				h = not h
				
				i += 1
			
			self.numFacts = len(self.flist)
			self.updateStatusBar()
			
			return
		
		
		
		
		
		def updateStatusBar(self):
			self.status['text'] = "%s Factoids" % self.numFacts
			return
		
		
		def editReset(self):
			self.editing = -1
			
			self.idLabel['text'] = "0"
			
			self.idEntry.delete(0, END)
			self.idEntry['state'] = DISABLED
			
			self.inkEntry.delete(0, END)
			self.inkEntry['state'] = DISABLED
			
			self.findEntry.delete(0, END)
			self.findEntry['state'] = DISABLED
			
			self.verbEntry.delete(0, END)
			self.verbEntry['state'] = DISABLED
			
			self.repText.delete(1.0, END)
			self.repText['state'] = DISABLED
			
			self.proCheck['state'] = DISABLED
			self.proCheck.deselect()
			
			self.lastEntry.delete(0, END)
			self.lastEntry['state'] = DISABLED
			
			self.authEntry.delete(0, END)
			self.authEntry['state'] = DISABLED
			
			return
		
		
		
		
		def saveCallback(self):
			if self.editing == -1: return
			
			print("Saving", self.editing)
			
			if self.editing < len(self.flist):
				item = self.flist[self.editing]
			
			oldID = self.idLabel['text']
			
			newID = self.idEntry.get()
			inkling = self.inkEntry.get()
			find = self.findEntry.get()
			verb = self.verbEntry.get()
			tidbit = self.repText.get(1.0, END).strip()
			editable = self.proBox.get()
			last_said = self.lastEntry.get()
			nick = self.authEntry.get()
			
			try:
				self.cur.execute("""UPDATE `factoids` SET `id`=?, `inkling`=?, `find`=?, `verb`=?, `tidbit`=?, `nick`=?, `editable`=?, `last_said`=? WHERE `id`=?""",
					(newID, inkling, find, verb, tidbit, nick, editable, last_said, oldID))
				self.conn.commit()
				
				if not item or item[0] != oldID:
					self.editing = -1
					#search for it. if found, edit it, pull into view
					for i,a in enumerate(self.flist):
						if a[0] == oldID:
							self.editing = i
							break
				if self.editing != -1:
					self.flist[self.editing] = (newID, inkling, find, verb, tidbit, nick, editable, last_said)
					self.updateItem(self.editing)
				
				
				
			except:
				traceback.print_exc()
				tkinter.messagebox.showerror("Error", "Could not save that factoid.\n\nSee debug console for more information.", **options)
			return
		
		
		
		
		def verbCallback(self):
			if self.showVerb.get() == "0":
				self.showVerb.set("")
			
			self.updateFacts()
			return
		
		def proCallback(self):
			if self.showProtected.get() == 0:
				self.showProtected.set(0)
			
			self.updateFacts()
			return
		
		def dirCallback(self):
			if not self.orderDIR.get():
				self.orderDIR.set("ASC")
			
			self.updateFacts()
			return
		
		
		def orderCallback(self):
			if self.orderBy.get() == "0":
				self.orderBy.set("id")
			
			self.updateFacts()
			return
		
		
		
		def createWidgets(self):
			
			self.menu = Menu(self)
	
			self.filemenu = Menu(self.menu, tearoff=FALSE)
			
			self.menu.add_cascade(label="File", menu=self.filemenu, underline=0)
			self.filemenu.add_command(label="Reload", command=self.bell)
			self.filemenu.add_separator()
			self.filemenu.add_command(label="Exit", command=self.quit)
			
			self.editMenu = Menu(self.menu, tearoff=FALSE)
			
			self.menu.add_cascade(label="Edit", menu=self.editMenu, underline=0)
			self.editMenu.add_command(label="Find", command=self.bell)
			self.editMenu.add_command(label="Replace", command=self.bell)
			self.editMenu.add_separator()
			self.editMenu.add_command(label="Goto", command=self.bell)
			
			
			self.viewMenu = Menu(self.menu, tearoff=FALSE)
			
			
			self.menu.add_cascade(label="View", menu=self.viewMenu, underline=0)
			
			
			self.viewMenu.add_checkbutton(label="Auto Refresh", variable=self.autoRefresh)
			
			
			self.verbMenu = Menu(self.viewMenu, tearoff=FALSE)
			self.viewMenu.add_cascade(label="Verb", menu=self.verbMenu)
			
			self.verbMenu.add_checkbutton(label="is", variable=self.showVerb, onvalue="is", command=self.verbCallback)
			self.verbMenu.add_checkbutton(label="are", variable=self.showVerb, onvalue="are", command=self.verbCallback)
			self.verbMenu.add_separator()
			self.verbMenu.add_checkbutton(label="is/are", variable=self.showVerb, onvalue="is are", command=self.verbCallback)
			self.verbMenu.add_separator()
			self.verbMenu.add_checkbutton(label="<reply>", variable=self.showVerb, onvalue="<reply>", command=self.verbCallback)
			self.verbMenu.add_checkbutton(label="<action>", variable=self.showVerb, onvalue="<action>", command=self.verbCallback)
			self.verbMenu.add_checkbutton(label="<alias>", variable=self.showVerb, onvalue="<alias>", command=self.verbCallback)
			self.verbMenu.add_separator()
			self.verbMenu.add_checkbutton(label="<other>", variable=self.showVerb, onvalue="<other>", command=self.verbCallback)
			self.verbMenu.add_separator()
			self.verbMenu.add_checkbutton(label="None", variable=self.showVerb, onvalue="", command=self.verbCallback)
			
			#self.viewMenu.add_separator()
			
			
			self.proMenu = Menu(self.viewMenu, tearoff=FALSE)
			self.viewMenu.add_cascade(label="Protected", menu=self.proMenu)
			
			
			self.proMenu.add_checkbutton(label="Protected", variable=self.showProtected, onvalue=1, command=self.proCallback)
			self.proMenu.add_checkbutton(label="Unprotected", variable=self.showProtected, onvalue=2, command=self.proCallback)
			self.proMenu.add_separator()
			self.proMenu.add_checkbutton(label="None", variable=self.showProtected, onvalue=0, command=self.proCallback)
			
			
			self.ordMenu = Menu(self.viewMenu, tearoff=FALSE)
			self.viewMenu.add_cascade(label="Order", menu=self.ordMenu)
			
			
			self.ordMenu.add_checkbutton(label="Ascending", command=self.dirCallback, variable=self.orderDIR, offvalue="DESC", onvalue="ASC")
			self.ordMenu.add_checkbutton(label="Descending", command=self.dirCallback, variable=self.orderDIR, offvalue="ASC", onvalue="DESC")
			self.ordMenu.add_separator()
			self.ordMenu.add_checkbutton(label="ID  (default)", variable=self.orderBy, onvalue="id", command=self.orderCallback)
			self.ordMenu.add_checkbutton(label="Inkling", variable=self.orderBy, onvalue="inkling", command=self.orderCallback)
			self.ordMenu.add_checkbutton(label="Find", variable=self.orderBy, onvalue="find", command=self.orderCallback)
			self.ordMenu.add_checkbutton(label="Verb", variable=self.orderBy, onvalue="verb", command=self.orderCallback)
			self.ordMenu.add_checkbutton(label="Reply", variable=self.orderBy, onvalue="tidbit", command=self.orderCallback)
			self.ordMenu.add_checkbutton(label="Nick", variable=self.orderBy, onvalue="nick", command=self.orderCallback)
			self.ordMenu.add_checkbutton(label="Protected", variable=self.orderBy, onvalue="editable", command=self.orderCallback)
			self.ordMenu.add_checkbutton(label="Last Said", variable=self.orderBy, onvalue="last_said", command=self.orderCallback)
			#self.viewMenu.add_separator()
			
			self.viewMenu.add_command(label="Nick...", command=self.bell)
			
			
			self.helpMenu = Menu(self.menu, tearoff=FALSE)
			
			self.menu.add_cascade(label="Help", menu=self.helpMenu, underline=0)
			self.helpMenu.add_command(label="About...", command=self.bell)
			
			
			self.master.config(menu=self.menu)
			
			
			
			
			
			self.sframe = Frame(self)
			self.sframe.pack(side=BOTTOM, fill=X)
			self.status = Label(self.sframe, 
									text="0 Items", 
									bd=1, 
									relief=SUNKEN, 
									anchor=W,
									padx=5)
									
			self.status.pack(side=BOTTOM, fill=X)
			
			
			self.sqFrame = Frame(self)
			self.sqFrame.pack(side=BOTTOM, fill=X)
			
			self.searchLabel = Label(self.sqFrame, text="Search:")
			self.searchLabel.pack(anchor=W, side=LEFT, padx=3)
			
			self.searchEntry = Entry(self.sqFrame, width=25, invcmd=self.bell)
			self.searchEntry.pack(anchor=W, side=LEFT)
			
			self.searchCase = BooleanVar(value=False)
			self.searchCheck = Checkbutton(self.sqFrame, text="Match Case", variable=self.searchCase)
			self.searchCheck.pack(anchor=W, side=LEFT, padx=2)
			
			self.QUIT = Button(self.sqFrame, text="  Done  ", command=self.quit)
			
			self.QUIT.pack(anchor=SE, side=BOTTOM, in_=self.sqFrame)
			
			
			
			self.editFrame = Frame(self)
			self.editFrame.pack(side=TOP, fill=X, padx=5, ipadx=10, ipady=5)
			
			self.idLabel = Label(self.editFrame, text="0")
			self.idLabel.pack(side=LEFT, padx=3)
			
			self.idEntry = Entry(self.editFrame, state=DISABLED, width=4)
			self.idEntry.pack(side=LEFT, padx=5)
			
			self.inkEntry = Entry(self.editFrame, state=DISABLED, width=10)
			self.inkEntry.pack(side=LEFT)
			
			
			self.findEntry = Entry(self.editFrame, state=DISABLED, width=40)
			self.findEntry.pack(side=LEFT)
			
			
			self.verbEntry = Entry(self.editFrame, state=DISABLED, width=10)
			self.verbEntry.pack(side=LEFT)
			
			self.proBox = IntVar()
			self.proCheck = Checkbutton(self.editFrame, variable=self.proBox, onvalue=0, offvalue=1, state=DISABLED, text="protected")
			self.proCheck.pack(side=LEFT, padx=10)
			
			self.repText = Text(self, state=DISABLED, height=2, wrap=WORD)
			self.repText.pack(side=TOP, fill=X, anchor=SW)
			
			self.siFrame = Frame(self)
			self.siFrame.pack(side=TOP, fill=X, anchor=SE)
			
			self.lastEntry = Entry(self.siFrame, state=DISABLED, width=10)
			self.lastEntry.pack(side=LEFT, anchor=W)
			
			self.authEntry = Entry(self.siFrame, state=DISABLED, width=10)
			self.authEntry.pack(side=LEFT, anchor=W)
			
			self.saveButton = Button(self.siFrame, text=" Save ", command=self.saveCallback)
			self.saveButton.pack(side=RIGHT, anchor=SE)
			
			
			
			self.viewFrame = Frame(self, bg="#FFFFFF")
			self.viewFrame.pack(side=TOP, fill=BOTH, expand=1)
			
			
			
			
			
			self.scrollbar = Scrollbar(self.viewFrame, orient=VERTICAL)
			self.lBox = Listbox(self.viewFrame, selectmode=SINGLE, height=20, width=100)
			
			self.scrollbar.config(command=self.lBox.yview)
			self.lBox.config(yscrollcommand=self.scrollbar.set)
			
			
			self.lBox.bind("<Button-1>", self.lBoxClick)
			self.lBox.bind("<Button-2>", self.lBoxMClick)
			self.lBox.bind("<Button-3>", self.lBoxRClick)
			self.master.bind("<MouseWheel>", self.lBoxScroll)
			self.master.bind("<Control-f>", self.searchCallback)
			self.searchEntry.bind("<Return>", self.searchGoCallback)
			
			self.scrollbar.pack(side=RIGHT, anchor=NE, fill=Y)
			self.lBox.pack(side=LEFT, expand=1, fill=BOTH, anchor=NW)
			self.lBox.focus_set()
			
			
			
			
			self.lBoxRMenu = Menu(self.lBox, tearoff=FALSE)
			self.lBoxRMenu.add_command(label="Edit", command=self.editItem)
			self.lBoxRMenu.add_command(label="Protect", command=self.protectItem)
			self.lBoxRMenu.add_command(label="Explicit", command=self.explicitItem)
			self.lBoxRMenu.add_separator()
			self.lBoxRMenu.add_command(label="Delete", command=self.deleteItem)
			
			
			
			return
		
		
		
		
		
		def searchCallback(self, e):
			self.searchEntry.focus()
			self.searchEntry.select_range(0,END)
			
		def searchGoCallback(self, e):
			self.searchText = self.searchEntry.get()
			
			if len(self.searchText) == 0:
				self.searchText = None
			
			self.updateFacts()
			
			self.bell()
		
		
		
		def lBoxScroll(self, e):
			if e.widget == self.lBox: return
			if e.keycode > 0:
				# scroll up
				self.lBox.yview_scroll(-1, "page")
				pass
			else:
				# scroll down
				self.lBox.yview_scroll(1, "page")
				pass
			
		
		
		
		
		
		def lBoxClick(self, e):
			# get the item the mouse is over
			selected = self.lBox.nearest(e.y)
			
			# no items to select
			if selected < 0: return
			
			# clear selection so that the item selected is the only one
			self.lBox.selection_clear(0, END)
			# add it to the selection
			self.lBox.selection_set(selected)
			
			# underlined
			self.lBox.activate(selected)
			
			# fill the edit form with the selected data
			self.editItem(int(self.lBox.curselection()[0]))
			return
		
		
		
		def lBoxMClick(self, e):
			
			self.lBox.focus()
			return
			
			# get the item the mouse is over
			selected = self.lBox.nearest(e.y)
			
			# no items to select
			if selected < 0: return
			
			# clear selection so that the item selected is the only one
			self.lBox.selection_clear(0, END)
			# add it to the selection
			self.lBox.selection_set(selected)
			
			# underline it .... I guess
			self.lBox.activate(selected)
			
			
			#confirm the deletion
			if not tkinter.messagebox.askyesno("Delete?", "Are you sure you want to delete this item?"): return
			
			self.deleteItem()
			return
		
		
		
		def lBoxRClick(self, e):
			# get the item the mouse is over
			selected = self.lBox.nearest(e.y)
			
			# no items to select
			if selected < 0: return
			
			# clear selection so that the item selected is the only one
			self.lBox.selection_clear(0, END)
			# add it to the selection
			self.lBox.selection_set(selected)
			
			# underlined
			self.lBox.activate(selected)
				
			# fill the edit form with the selected data
			self.editItem(int(self.lBox.curselection()[0]))
			
			# change the text of the 'protect' menu item (item #1) to 'protect'
			# or 'unprotect' depending on the factoid.
			if self.flist[selected][6]:
				self.lBoxRMenu.entryconfig(1, label="Protect")
			else:
				self.lBoxRMenu.entryconfig(1, label="Unprotect")
			
			# Display the right click menu
			self.lBoxRMenu.post(self.lBox.winfo_rootx() + e.x, self.lBox.winfo_rooty() + e.y)
			
			return
		
		
		
		
		
		def __init__(self, master=None):
			Frame.__init__(self, master)
			self.pack(fill=BOTH, expand=1)
			
			self.editing = -1
			self.flist = []
			self.showVerb = StringVar()
			self.showProtected = IntVar(value=0)
			self.showNick = None
			self.orderBy = StringVar(value="id")
			self.orderDIR = StringVar(value="DESC")
			self.autoRefresh = BooleanVar(value=True)
			self.searchText = None
			
			self.conn = sqlite3.connect('C:\\python\\Jobot\\bucket.sql', timeout=20)
			self.cur = self.conn.cursor()
			
			self.createWidgets()
			
			self.queryListAll()
			
			self.fetchList()
			
			self.updateList()
			
			return
		
		

	root = Tk(className="Jobot Database Management GUI")
	jInterface = jobotDBInterface(master=root)
	jInterface.mainloop()


except:
	traceback.print_exc()
	input('\n\nPress [Enter] to continue...')