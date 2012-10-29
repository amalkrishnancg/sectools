#!/usr/bin/env python
#-------------------------------------------------------------
# remoteSSLyze Server
# Version: 0.1b
# Author: Amal Krishnan (amalkrishnancg@gmail.com)
# Copyright: None
#
# A SSL scanning server that uses iSecPartner's sslyze
#
#-------------------------------------------------------------
 
#<------------------------OPTIONS------------------------------
SSLYZE_PATH = '/home/amal.krishnan/Tools/SSL/sslyze/sslyze.py'
LISTEN_PORT = 1337
HOST = 'amalkrishnan-wsl1'
REMOTE_SERVER_URL = '10.0.41.101:13373' # Format: IPAddress:Port
OPENSSL_V0_9_OPTS = '--sslv3 --tlsv1 --resum --certinfo=basic --hide_rejected_ciphers --http_get'
OPENSSL_V1_0_OPTS = '--tlsv1_1 --tlsv1_2 --compression --reneg --hide_rejected_ciphers'  
OPENSSL_HOST_VERSION = 0.9
QUERY_REMOTE_SERVER = True # True|False
#-------------------------------------------------------------/>

#<--------------------MESSAGES---------------------------------
URL_MISSING = """ Usage is protocol://domain:port/sslyze?url=sitetoscan[:port]'
                <br /><b>Example: http://sslyzedomain.com:port/sslyze?url=
                www.salesforce.com:443</b>"""
LOGIN_PAGE = """ <form method="POST" action="/sslyze">
                 Scan URL (site:port) <input name="url" type="text" />
                 <input type="submit" />
                 </form><br />"""
INSTRUCTIONS = "Example: <b>www.google.com:443</b> or <b>www.google.com</b> (default port: 443)"
INVALID_URL = 'Enter a valid url. Don\'t be naughty'
ERROR_URL = 'Unable to access URL. Are you sure the server is up?'
XSS_TAUNT = '<script> alert("1") </script> <img src="http://i.qkme.me/3rk3fq.jpg" alt="derp" />'
SQL_INJ_TAUNT = '<img src="http://i.qkme.me/3rk3l2.jpg" alt="derp" />'
COOKIE_TAUNT = 'bovjna=Guvf vf abg gur pbbxvr lbh\'er ybbxvat sbe'
UNSUPPORTED_METHOD = ' method is not supported. Don\'t be naughty '
MESSAGE_404 = '<img src=\'http://i.qkme.me/3rjyzb.jpg\' alt=\'404 Page not found\' />'
DIVISION = '<br />-----------------------------------------------------------'
REMOTE_SCAN_TITLE = '<br />Results from remote scan <br />'
REMOTE_SERVER_DOWN = '<br />Remote server does not seem to be responding. Is ' + REMOTE_SERVER_URL + ' up?' 
#--------------------------------------------------------------/>

import httplib # for contacting remote server & url validation
import re # for verifying if user include protocol scheme in url
import subprocess # for forking sslyze

from bottle import error, get, post, run, route, request, response # for request handling
from socket import gaierror # for handling [Errno -2] Name or service not known
from httplib import InvalidURL # for handling invalid URLS 
 
@route ('/')
def login_form():
    return LOGIN_PAGE + INSTRUCTIONS

@route('/sslyze')
@post('/sslyze')
def run_sslyze():
    if (request.method == 'GET'): 
        if 'url' not in request.GET.keys():
            return (URL_MISSING)
        else:
            url = request.GET['url']
    elif (request.method == 'POST'):
        if not request.forms.get('url'):
            return (URL_MISSING)
        else:
            url = request.forms.get('url')
    else: # request is not a GET or POST
        return request.method + UNSUPPORTED_METHOD
    # Validate URL 
    # Unnecessary security taunts------------------- 
    if (re.match('.*(<|>)+.*', url)):
        print request.remote_addr + ' entered ' + url 
        return XSS_TAUNT
    elif (re.match('.*\'.*', url)):
        print request.remote_addr + ' entered ' + url
        return SQL_INJ_TAUNT
    response.set_header('Set-Cookie', COOKIE_TAUNT)
    #----------------------------------------------->
    #TODO: Find a better way to handle an invalid URL though this works exceptionally well
    try:
        connection = httplib.HTTPConnection(url, timeout=1)
        connection.request('GET','/')
        connection.close()
    except gaierror:
        return INVALID_URL
    except InvalidURL:
        return INVALID_URL
    except Exception:
        return ERROR_URL
    if (OPENSSL_HOST_VERSION == 0.9):
        host_option_list = [SSLYZE_PATH] + OPENSSL_V0_9_OPTS.split() +  [url]
    else:
        host_option_list = [SSLYZE_PATH] + OPENSSL_V1_0_OPTS.split() +  [url]
    print request.remote_addr + ' initiated scan request for ' + url 
    host_proc = subprocess.Popen(host_option_list, 0, None, subprocess.PIPE, subprocess.PIPE, None)    
    # reads the output and replaces \n with <br/>
    output =  "<br />".join(''.join(host_proc.stdout.readlines()).split("\n"))
    # Query the remote SSLyze server and append report
    if (QUERY_REMOTE_SERVER):
        try:
            connection = httplib.HTTPConnection(REMOTE_SERVER_URL)
            connection.request('GET','/sslyze?url=' + url)
            output_r= connection.getresponse().read()
            output += DIVISION
            output += REMOTE_SCAN_TITLE
            output += DIVISION
            output += "<br />".join(''.join(output_r).split("\n"))
            connection.close()
        except Exception:
            output += DIVISION
            output += REMOTE_SCAN_TITLE
            output += DIVISION
            output += REMOTE_SERVER_DOWN 
    return output

@error(404)
def error(error):
    return MESSAGE_404

run(host=HOST, port=LISTEN_PORT)
