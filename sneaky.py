#!/usr/bin/env python
#----------------------------------------------------------------------
# Sneaky
# Version: 0.1
# Author: Amal Krishnan (amalkrishnancg@gmail.com)
# Copyright: None 
#
# Sneaky builds a list of scanned servers on SSLlabs (www.ssllabs.com). 
# On killing the program, the list of servers is written to an output file
#
#-----------------------------------------------------------------------

#------------------------OPTIONS----------------------------
QUERY_LOCATION = 'https://www.ssllabs.com/ssltest/index.html'
ANALYSIS_PAGE = 'analyze.html'
QUERY_INTERVAL_SECS = 10
OUTPUT_FILE = './serverlist.txt'
#-----------------------------------------------------------

import re # for scanning server urls from html page
import urllib2 # for accessing page contents at QUERY_LOCATION
import signal # for capturing CTRL-C 
import sys # for sys.exit()

from HTMLParser import HTMLParser # for parsing content from QUERY_LOCATION
from htmlentitydefs import name2codepoint # for handling entity definitions
from time import gmtime, strftime, sleep # for formatting time and sleeping

# This class parses the list of recently scanned servers
class SSLLabsParser(HTMLParser):
    in_print_block = False
    
    def handle_starttag(self, tag, attrs):
        if tag == 'div':
	    for attr in attrs:
	        if attr == ('class', 'boxHead'):
		    # If this is the second boxHead div, stop parsing
		    if (self.in_print_block == True):
		        #TODO: Find a better way to stop processing						
			self.reset()	
		    else:
		        self.in_print_block = True
        if tag == 'a' and self.in_print_block:
	    for attr in attrs:
	        if attr[0] == 'href': 
		    if ANALYSIS_PAGE in attr[1]:
		        # Pick out the server url, url decode it and add to list
			ContentManager.scanned_servers.add(urllib2.unquote(re.search('.*\?d=(.*)',attr[1]).group(1)))
					
# This class handles HTML parsing and retrieving list of servers and ratings
class ContentManager():
    scanned_servers = set([])
    
    def load_content(self):
        self.content = urllib2.urlopen(QUERY_LOCATION)
    
    def process_HTML_content(self):
	self.parser = SSLLabsParser()
	try:	
	    self.parser.feed (self.content.read())
	except AssertionError: 
	    pass	

def main():
    signal.signal(signal.SIGINT, exit_handler)
    print 'Sneaky is retrieving list of scanned servers (CTRL-C to quit)'
    manager = ContentManager()
    while(True):
        manager.load_content()
	manager.process_HTML_content()
	# Print list of servers
	print "\n--------------" + strftime("%d %b %Y %H:%M:%S", gmtime()) + "--------------"
	for server in ContentManager.scanned_servers:
	    print server+"\n"
	sleep(QUERY_INTERVAL_SECS)

# Function writes list of servers to file on termination
def exit_handler(signum, frame):
    try:
        file = open(OUTPUT_FILE, 'w+')
   	for server in ContentManager.scanned_servers:
	    file.write(server  + "\n")
    	file.close()
    	sys.exit("\nSneaky successfully wrote to " + OUTPUT_FILE)	
    except IOError:
	sys.exit("\nSneaky was unable to write to " + OUTPUT_FILE)	

if __name__ == "__main__":
    main()
