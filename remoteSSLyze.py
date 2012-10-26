#!/usr/bin/env python
#----------------------------------------------------------------------
# remoteSSLyze Server
# Version: 0.1
# Author: Amal Krishnan (amalkrishnancg@gmail.com)
# Copyright: None 
#
# A service that accepts a URL and tests it with SSLyze
#
#-----------------------------------------------------------------------

#------------------------OPTIONS------------------------------
SSLYZE_PATH = '/home/amal.krishnan/Tools/SSL/sslyze/sslyze.py'
LISTEN_PORT = 13373
HOST = 'localhost'
REMOTE_SERVER_URL = 
#-------------------------------------------------------------

import os
import re
import subprocess

from bottle import run, route, request
from urlparse import urlparse

@route('/sslyze')
def run_sslyze():
    if 'url' not in request.GET.keys():
        return ("The parameter \'url\' not found. Usage is ' + 'protocol://domain:port/sslyze'"
         "?url=scheme://sitetoscan:port' <br /><b>Example: http://sslyzedomain.com:port/sslyze?url="
         "https://www.salesforce.com:443</b>")
    # Check if scheme was not included by a lazy user. If not, include scheme
    if (re.match("\w+://", request.GET['url'])):
        url = request.GET['url']
    else:
        url = 'https://' + request.GET['url']
    # urlparse() does the validation of the url. Stay secure people! 
    url_parse_object = urlparse(url)
    print url_parse_object 
    if (url_parse_object.netloc == ''):
        return 'Enter a valid url. Don\'t be naughty'
    
    host_option_list = [SSLYZE_PATH, '--sslv3', '--tlsv1', '--resum',  '--certinfo=basic', '--hide_rejected_ciphers', '--http_get',  url_parse_object.netloc]
    print 'Running sslyze on' + url_parse_object.path
    host_proc = subprocess.Popen(host_option_list, 0, None, subprocess.PIPE, subprocess.PIPE, None)
    return  "<br />".join(''.join(host_proc.stdout.readlines()).split("\n")) # reads the output and replaces \n with <br/>
    
run(host=HOST, port=LISTEN_PORT)
