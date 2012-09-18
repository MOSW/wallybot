## Copyright 2009-2012 Joey
## 
## Jobot is released under Affero GPL. Please read the license before continuing.
## 
## The latest source can be found here:
##	 https://github.com/MOSW/wallybot
##
import sys
import re
import traceback
import PorterStemmer
import pickle

try:
	
	def _uniquify(seq, idfun=None): 
		# order preserving
		if idfun is None:
			def idfun(x): return x
		seen = {}
		result = []
		for item in seq:
			marker = idfun(item)
			# in old Python versions:
			# if seen.has_key(marker)
			# but in new ones:
			if marker in seen: continue
			seen[marker] = 1
			result.append(item)
		return result
	
	def uniquify(seq):
		# not order preserving
		return list({}.fromkeys(seq).keys())
	
	
	def genList(fileName):

		try:
			f = open(fileName, 'r', buffering=1, encoding='utf8', errors='replace')
		except:
			input('Could not open list.')
			return None
		
		
		stemmer = PorterStemmer.PorterStemmer()
		
		rawVerbs = []

		for line in f:
			if line[0] == ">":
				rawVerbs.append(list(map(lambda x:str.lower(stemmer.stem(x,0,len(x)-1)), re.split(r'[\s\\/]', line[1:])[:-2])))
				print(rawVerbs[-1])
			
		
		
		
		
		wordlist = []
		
		for verbs in rawVerbs:
			uVerbs = uniquify(verbs)
			if len(uVerbs) < 2: continue
			
			wordlist.append(uVerbs)
		
		
		return wordlist
	
	
	
	wordlist = genList('Verblist.vrb')
	wordlist.extend(genList('replaceable.txt'))
	
	#wordlist.append(list(map(lambda x:stemmer.stem(x,0,len(x)-1),['i','you','he','she','it','we','they'])))
	
	for i in wordlist:
		print(i)
	
	
	
	input('Continue... (dump)')
	
	wf = open('replaceable.list', 'wb')
	
	pickle.dump(wordlist, wf)
	
	wf.close()
	
	wf.close()
	input('Done!')
except:
	traceback.print_exc()
	input()