#!/usr/bin/env python

import time
import random

import rpyc
from rpyc.utils.server import ThreadedServer
from threading import Thread


# Actual Access Point Logic
class CL:
    
    def __init__(self):
        self.message = 0
        self.intercepted = False
        self.replayCounter = None
        self.ANonce = None
        self.SNonce = None
        self.MAC = '34-25-B8-1C-17-EB'
        self.apconn = None
        self.ap = None
        self.jammed = False
        self.m1 = None
        self.m3 = None
        self.reset = False

    def getMessage1(self, mnum, message):
        self.m1 = message
        self.message = mnum
        print(self.m1)

    def getMessage3(self, mnum, message):
        if (self.m3 == None):
            self.m3 = message
            self.message = mnum
            print(self.m3)
        else:
            print('reinstalling key')
            self.reset = True
    
    def getHijacked(self):
        print('hijacked')
        self.apconn = rpyc.connect("localhost", 18814)
        self.ap = self.apconn.root
        self.ap.exposed_reqConnection()
        return(self.message)

    def reqAPConnection(self):
        print('connecting')
        self.apconn = rpyc.connect("localhost", 18812)
        self.ap = self.apconn.root
        self.ap.exposed_reqConnection()

# RPYC Server Stuff
class CLService(rpyc.Service):
    
    def exposed_sendMessage1(self, mnum, message):
        cl.getMessage1(mnum, message)

    def exposed_sendMessage3(self, mnum, message):
        cl.getMessage3(mnum, message)

    def exposed_hijack(self):
        return cl.getHijacked()
        
    
# start the CLserver
server = ThreadedServer(CLService, port = 18813)
t = Thread(target = server.start)
t.daemon = True
t.start()

cl = CL()

input('Initiate 4-way handshake? (y/y) ')
cl.reqAPConnection()

while True:
    time.sleep(1)
    if(cl.message == 1):
        print('sending message 2')
        time.sleep(3)
        cl.ap.exposed_sendMessage2(cl.message, 'message2')
        time.sleep(3)
    if(cl.message == 3):
        print('sending message 4')
        time.sleep(3)
        cl.ap.exposed_sendMessage4(cl.message, 'message4')
        time.sleep(3)
        cl.message = 5
    if(cl.message == 5):
        print('sending message 5')
        time.sleep(3)
        cl.ap.exposed_sendMessage5(cl.message, 'message5')
        time.sleep(3)
        cl.message = 6
    if(cl.message == 6):
        print('sending message 6')
        time.sleep(3)
        if (cl.reset == False):
            cl.ap.exposed_sendMessage6(cl.message, 'message6')
        else:
            cl.ap.exposed_sendMessage6(cl.message, 'reset key')
        print('Communications done')
        break
    
