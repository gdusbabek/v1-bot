import sys, time, os
import urllib2, base64, StringIO, pickle
from elementtree import ElementTree as et
import ConfigParser as cp
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower
import botcommon
import v1
import commands

class V1Bot(SingleServerIRCBot):
  def __init__(self, channel, nickname, server, port):
    SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
    self.voiced = True
    if len(channel.split(' ')) > 0:
      self.join_channel = channel
      self.channel = channel.split(' ')[0]
    else:
      self.channel = channel
      self.join_channel = channel
    self.scanners = []
    self.nickname = nickname
    self.queue = botcommon.OutputManager(self.connection)
    self.queue.start()

  def on_welcome(self, c, e):
    print 'connected. joining %s' % self.channel
    c.join(self.join_channel)

  def on_pubmsg(self, c, e):
    msg = e.arguments()[0]
    from_nick = nm_to_n(e.source())
    if msg.startswith(self.nickname + ':'):
      args = msg.split(' ')[1:]
      cmd = commands.makeCommand(args)
      if cmd:
        responses = cmd.execute(scanners=self.scanners, bot=self)
        for resp in responses:
          self.puts(resp, True)
  
  def puts(self, text, force=False):
    if self.voiced or force:
      self.queue.send(text, self.channel)
    else:
      print 'UNVOICED: ' + text
    
  def setVoice(self, status):
    self.voiced = status


def main(args):
  # load config:
  if len(args) < 2:
    print 'expected a config file path'
    sys.exit(-1)
  config = cp.RawConfigParser()
  config.read(args[1])
  
  channel_string = config.get('bot', 'channel') + ('' if not config.has_option('bot', 'channel_pass') else (' ' + config.get('bot', 'channel_pass')))
  bot = V1Bot(channel_string, 
              config.get('bot', 'nick'), 
              config.get('bot', 'server'), 
              config.getint('bot', 'port'))
  
  storyOpts = {
    'cookiePath': config.get('v1', 'story_cookie'),
    'host': config.get('v1', 'host'),
    'enterprise': config.get('v1', 'enterprise'),
    'user': config.get('v1', 'user'),
    'password': config.get('v1', 'pass')
  }
  story = v1.Scanner('Story', storyOpts)
  
  taskOpts = {
    'cookiePath': config.get('v1', 'task_cookie'),
    'host': config.get('v1', 'host'),
    'enterprise': config.get('v1', 'enterprise'),
    'user': config.get('v1', 'user'),
    'password': config.get('v1', 'pass')
  }
  task = v1.Scanner('Task', taskOpts)
  
  bot.scanners = [story, task] # ugly coupling for now.
  
  # set the time box. this skips over every change up until $now.
#  print 'set and skip ' + str(story.setTimebox('8/24/2011'))
#  print 'set and skip ' + str(task.setTimebox('8/24/2011'))
  
  storyThread = v1.ScanThread(story, bot)
  taskThread = v1.ScanThread(task, bot)
  
  storyThread.start()
  taskThread.start()
  
  try:
    bot.start()
  except KeyboardInterrupt, e:
    print 'Quitting'
    sys.exit(0)

if __name__ == '__main__':
  main(sys.argv)