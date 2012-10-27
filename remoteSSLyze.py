#!/usr/bin/env python
#-------------------------------------------------------------
# remoteSSLyze Server
# Version: 0.1a
# Author: Amal Krishnan (amalkrishnancg@gmail.com)
# Copyright: None
#
# A service that accepts a URL and tests it with SSLyze
#
#-------------------------------------------------------------
 
#------------------------OPTIONS------------------------------
SSLYZE_PATH = '/home/amal.krishnan/Tools/SSL/sslyze/sslyze.py'
LISTEN_PORT = 13373
HOST = 'amalkrishnan-wsl1'
REMOTE_SERVER_URL = '10.0.41.101:13373'
OPENSSL_V0_9_OPTS = '--sslv3 --tlsv1 --resum --certinfo=basic --hide_rejected_ciphers --http_get'
OPENSSL_V1_0_OPTS = '--tlsv1_1 --tlsv1_2 --compression --reneg --hide_rejected_ciphers'  
OPENSSL_VERSION = 0.9
QUERY_REMOTE_SERVER = True
#-------------------------------------------------------------

import httplib
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
    # Check if scheme was not included by a lazy user. If not inlcuded, add scheme
    if (re.match("\w+://", request.GET['url'])):
        url = request.GET['url']
    else:
        url = 'https://' + request.GET['url']
    # urlparse() does the validation of the url. Stay secure people!
    url_parse_object = urlparse(url)
    if (url_parse_object.netloc == ''):
        return 'Enter a valid url. Don\'t be naughty'
    if (OPENSSL_VERSION == 0.9):
        host_option_list = [SSLYZE_PATH] + OPENSSL_V0_9_OPTS.split() +  [url_parse_object.netloc]
    else:
        host_option_list = [SSLYZE_PATH] + OPENSSL_V1_0_OPTS.split() +  [url_parse_object.netloc]
    host_proc = subprocess.Popen(host_option_list, 0, None, subprocess.PIPE, subprocess.PIPE, None)    
    # reads the output and replaces \n with <br/>
    output =  "<br />".join(''.join(host_proc.stdout.readlines()).split("\n"))
    if (QUERY_REMOTE_SERVER):
        connection = httplib.HTTPConnection(REMOTE_SERVER_URL)
        connection.request('GET','/sslyze?url=' + url_parse_object.netloc)
        output_r= connection.getresponse().read()
        output += '<br />-----------------------------------------------------------'
        output += '<br /> Results from remote scan <br />'
        output += '-----------------------------------------------------------'
        output += "<br />".join(''.join(output_r).split("\n"))
        connection.close()
    return output

run(host=HOST, port=LISTEN_PORT)
