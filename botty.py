import sys, time, os
import urllib2, base64, StringIO, pickle
from elementtree import ElementTree as et
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower
import botcommon
import v1

BOT_COMMANDS = ['commands', 'help']


class V1Bot(SingleServerIRCBot):
  def __init__(self, channel, nickname, server, port):
    SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
    if len(channel.split(' ')) > 0:
      print 'splitting channel: ' + channel
      self.join_channel = channel
      self.channel = channel.split(' ')[0]
    else:
      self.channel = channel
      self.join_channel = channel
    self.nickname = nickname
    self.queue = botcommon.OutputManager(self.connection)
    self.queue.start()

  def on_welcome(self, c, e):
    c.join(self.join_channel)

  def on_pubmsg(self, c, e):
    msg = e.arguments()[0]
    from_nick = nm_to_n(e.source())
    if msg.startswith(self.nickname + ':'):
      print msg;

class Outputter(object):
  def __init__(self, bot):
    self.bot = bot;
  
  def puts(self, text):
    self.bot.queue.send(text, self.bot.channel)

# todo: put your own credentials here. 'fiercely' is the room passwd in this case.
bot = V1Bot('#fiercefrogs fiercely', 'garydusbabek', 'irc.freenode.net', 6667)

# todo: put your own paths here.
# the second parameter is the 'timebox' (this is v1 nomenclature) that seems to correspond to a sprint in my organization.
story = v1.Scanner('Story', '/Users/gary.dusbabek/Desktop/v1/stories_counter_cookie.txt', '8/24/2011')
task = v1.Scanner('Task', '/Users/gary.dusbabek/Desktop/v1/tasks_counter_cookie.txt', '8/24/2011')

#story.catchUp()
#task.catchUp()

storyThread = v1.ScanThread(story, Outputter(bot))
taskThread = v1.ScanThread(task, Outputter(bot))

storyThread.start()
taskThread.start()
bot.start()

print 'it is all going'