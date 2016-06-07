#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#########################################################
#
# for FRITZ!OS:06.50 (e.g. 6490 Cable)
#
#########################################################


import hashlib
import httplib
import re
import sys
from xml.dom import minidom

from bs4 import BeautifulSoup
from tools.helper import format_gib

import ConfigParser

#
# TODO:
#   - login credentials auslagern
#

USER_AGENT="Mozilla/5.0 (U; Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0"

class fritzTraffic(object):

    def __init__(self, data=[]):
        self.label = ""
        self.online = ""
        self.total = 0
        self.upload = 0
        self.download = 0
        self.connections = 0
        
        if len(data) == 6:
            self.label = data[0]
            self.online = data[1]
            self.total = int(data[2])
            self.upload = int(data[3])
            self.download = int(data[4])
            self.connections = int(data[5])

    def __str__(self):
        return '{} ({}h): Total: {}, Up: {}, Down: {}'.format(
            self.label, self.online, format_gib(self.total), format_gib(self.upload),
            format_gib(self.download))


class fritzController(object):

    def getPage(self, server, sid, page, port=80):

        conn = httplib.HTTPConnection(server+':'+str(port))

        headers = { "Accept" : "application/xml",
                    "Content-Type" : "text/plain",
                    "User-Agent" : USER_AGENT}

        pageWithSid=page+"?sid="+sid
        conn.request("GET", pageWithSid, '', headers)
        response = conn.getresponse()
        data = response.read()
        if response.status != 200:
            print "%s %s" % (response.status, response.reason)
            print data
            sys.exit(0)
        else:
            return data

    def loginToServer(self, server,password,port=80):

        conn = httplib.HTTPConnection(server+':'+str(port))

        headers = { "Accept" : "application/xml",
                    "Content-Type" : "text/plain",
                    "User-Agent" : USER_AGENT}

        initialPage='/login_sid.lua'
        conn.request("GET", initialPage, '', headers)
        response = conn.getresponse()
        data = response.read()
        if response.status != 200:
            print "%s %s" % (response.status, response.reason)
            print data
            sys.exit(0)
        else:
            theXml = minidom.parseString(data)
            sidInfo = theXml.getElementsByTagName('SID')
            sid=sidInfo[0].firstChild.data
            if sid == "0000000000000000":
                challengeInfo = theXml.getElementsByTagName('Challenge')
                challenge=challengeInfo[0].firstChild.data
                challenge_bf = (challenge + '-' + password).decode('iso-8859-1').encode('utf-16le')
                m = hashlib.md5()
                m.update(challenge_bf)
                response_bf = challenge + '-' + m.hexdigest().lower()
            else:
                return sid

        headers = { "Accept" : "text/html,application/xhtml+xml,application/xml",
                    "Content-Type" : "application/x-www-form-urlencoded",
                    "User-Agent" : USER_AGENT}

        loginPage="/login_sid.lua?&response=" + response_bf
        conn.request("GET", loginPage, '', headers)
        response = conn.getresponse()
        data = response.read()

        if response.status != 200:
            print "%s %s" % (response.status, response.reason)
            print data
            sys.exit(0)
        else:
            sid = re.search('<SID>(.*?)</SID>', data).group(1)
            if sid == "0000000000000000":
                print "ERROR - No SID received because of invalid password"
                sys.exit(0)
            return sid

    def getTrafficInfo(self):
        Config = ConfigParser.ConfigParser()
        Config.read("settings.ini")
        server=Config.get('FritzBox', 'address')
        password=Config.get('FritzBox', 'secret')

        sid = self.loginToServer(server,password)

        if not sid:
            print "ERROR logging on"
            sys.exit(0)

        page = self.getPage(server,sid,"/internet/inetstat_counter.lua")

        start = page.find('<table id="tStat">')
        end = page.find('</table>')
        htmlStr = page[start:end]

        soup = BeautifulSoup(htmlStr, 'html.parser')

        #print soup.prettify()
        table = soup.find('table') #, attrs={'class':'lineItemsTable'})

        data = []
        ftCon = []

        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [cell.text.strip() for cell in cols]
            data.append([cell for cell in cols if cell]) # Get rid of empty values

        for d in data:
            if len(d) > 0:
                ft = fritzTraffic(d)
                ftCon.append(ft)
                #print ft

        return ftCon

#fc = fritzController()
#for data in fc.getTrafficInfo():
#    print data