#!/usr/bin/python
"""
ircbot.py - An IRC Bot Basis in Python

License: 
   W3C Open Source License; share and enjoy!
   http://www.w3.org/Consortium/Legal/copyright-software-19980720

Original: 
   http://dev.w3.org/cvsweb/2000/scribe-bot/ircAsync.py
   Dan Connolly and Tim Berners-Lee
   Copyright (c) 2001 W3C (MIT, INRIA, Keio)

Augmentations' Author: 
   Sean B. Palmer, inamidst.com
"""

import sys, os, re, socket, asyncore, asynchat
import logging

protect = True

class Origin(object): 
   def __init__(self, origin): 
      self.origin = origin
      self.split(origin)

   def __str__(self): 
      return self.origin

   def split(self, origin):
      if origin and '!' in origin: 
         self.nick, userHost = origin.split('!', 1)
         if '@' in userHost: 
            self.user, self.host = userHost.split('@', 1)
         else: self.user, self.host = userHost, None
      else: self.nick, self.user, self.host = origin, None, None

   def replyTo(self, nickname, args): 
      if (not args) or (len(args) < 2): return
      target = args[1]
      if target == nickname: 
         self.sender = self.nick
      else: self.sender = target

def ctcp(s): return '\x01%s\x01' % s
def me(s): return ctcp('ACTION %s' % s)

class Bot(asynchat.async_chat): 
   def __init__(self, nick=None, userid=None, name=None, channels=None): 
      asynchat.async_chat.__init__(self)
      self.bufIn = ''
      self.set_terminator('\r\n')

      self.nick = nick or 'ircbot'
      self.userid = userid or 'nobody'
      self.name = name or 'ircbot.py user'

      self.documentation = {}
      self.info = {}
      self.dispatch = []
      self.msgstack = []

      self.channels = channels or ['#test']
      self.rule(self.welcome, 'welcome', cmd='001')
      self.rule(self.help, 'help', '%s[:,] help (\w+)\??' % self.nick)
        
   def run(self, host, port): 
      port = port or 6667
      self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
      debug("connecting to...", host, port)
      self.connect((host, port))
      self.bufIn = ''
      asyncore.loop()

   def welcome(self, m, origin, args, text): 
      for chan in self.channels: 
         self.todo(['JOIN', chan])

   def help(self, m, origin, args, text): 
      command = m.group(1)
      if self.documentation.has_key(command): 
         doc = self.documentation[command]
         self.msg(origin.sender, '%s: %s' % (command, doc))
      else: self.msg(origin.sender, 'No help available for %s.' % command)

   def todo(self, args, *text): 
      command = ' '.join(args)
      if text: command = command + ' :' + ' '.join(text)

      self.push(command + '\r\n')
      debug("sent/pushed command:", command)

   def handle_connect(self): 
      debug("connected")

      self.todo(['NICK', self.nick])
      self.todo(['USER', self.userid, "+iw", self.nick], self.name)

   def collect_incoming_data(self, bytes): 
      self.bufIn = self.bufIn + bytes

   def found_terminator(self): 
      line = self.bufIn
      self.bufIn = ''

      if line.startswith(':'): 
         origin, line = line[1:].split(' ', 1)
         origin = Origin(origin)
      else: origin = None

      try: args, text = line.split(' :', 1)
      except ValueError: 
         args, text = line, ''
      args = args.split()

      if origin: origin.replyTo(self.nick, args)
      debug("from::", origin, "|message::", args, "|text::", text)
      self.rxdMsg(args, text, origin)

   def rule(self, func, name, regexp=None, doc=None, cmd=None): 
      if isinstance(regexp, basestring): 
         regexp = re.compile(regexp)
      if self.documentation.has_key(name): 
         raise "DispatchError", "Function %s already added" % name

      doc = doc or func.__doc__
      if doc and doc.strip(): 
         self.documentation[name] = doc
      self.dispatch.append((cmd or 'PRIVMSG', regexp, func))

   def bind(self, func, cmd, regexp): 
      self.dispatch.append((cmd, re.compile(regexp), func))

   def rxdMsg(self, args, text, origin): 
      if args[0] == 'PING': 
         self.todo(['PONG', text])

      for cmd, pat, thunk in self.dispatch: 
         if args[0] == cmd: 
            if pat: 
               m = pat.search(text)
               if not m: continue
            else: m = None

            if protect: 
               try: thunk(m, origin, args, text)
               except Exception, e: 
                  try: self.msg(origin.sender, "%s: %s" % (e.__class__, e))
                  except: print >> sys.stderr, "%s: %s" % (e.__class__, e)
            else: thunk(m, origin, args, text)

   def pushMsg(self, msg): 
      self.msgstack = self.msgstack[-9:]
      self.msgstack.append(msg)

   def msg(self, dest, text): 
      # Flood protection
      if self.msgstack.count(text) >= 5: 
         text = '...'

      if self.msgstack.count('...') >= 2: 
         if text == '...': return

      if len(''.join(self.msgstack[:-3])) > 200: 
         import time
         time.sleep(2)

      self.pushMsg(text)
      self.todo(['PRIVMSG', dest], text)

   def safeMsg(self, channel, lines): 
      import time
      for line in lines: 
         if line: self.msg(channel, line)
         time.sleep(1)
         if len(line) > 50: time.sleep(0.7)
	    
   def notice(self, dest, text): 
      self.todo(['NOTICE', dest], text)

log = logging.getLogger('irc')
def debug(*args): 
    log.debug(' '.join([str(a) for a in args]))
   #sys.stderr.write("DEBUG: ")
   #for a in args: 
   #   sys.stderr.write(str(a))
   #sys.stderr.write("\n")

def doubleFork(): 
   # http://swhack.com/logs/2004-05-12#T10-20-11
   # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66012
   try: 
      pid = os.fork() 
      if pid > 0: sys.exit(0) 
   except OSError, e: 
      print >> sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
      sys.exit(1)
   os.chdir("/") 
   os.setsid() 
   os.umask(0) 
   try: 
      pid = os.fork() 
      if pid > 0: 
         print "Daemon PID %d" % pid 
         sys.exit(0) 
   except OSError, e: 
      print >> sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
      sys.exit(1) 

def test(host, port, channels):
   bot = Bot(nick='testIRCbot', channels=channels)

   def hi(m, origin, args, text, bot=bot): 
      bot.msg(origin.sender, "hi %s" % origin.nick)
   bot.rule(hi, 'hi', r'hi %s' % bot.nick)

   def hmm(m, origin, (cmd, chan), text, bot=bot): 
      """.test - Do some crazy test thing."""
      raise Exception, "blargh"
      bot.msg(origin.sender, 'Test')
   bot.rule(hmm, 'test', r'^\.test$')

   def bye(m, origin, args, text, bot=bot):
      bot.todo(['QUIT'], "bye bye!")
   bot.rule(bye, 'bye', r'bye bye bot')

   bot.run(host, port)
    
if __name__=='__main__': 
   test('irc.freenode.net', 6667, ['#d8uv.com'])
