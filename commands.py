import sys

BOT_COMMANDS = ['commands', 'help', 'watch', 'voice', 'status']

HELP = {
  'watch': 'watch {timebox}',
  'voice': 'voice {on|off}',
  'status': 'status',
  'commands': 'commands',
  'help': 'help {command}'
}

class Watch(object):
  def __init__(self, args):
    self.timebox = args[0]
  
  def execute(self, **kwargs):
    # assume parsed.
    for scanner in kwargs.get('scanners'):
      scanner.setTimebox(self.timebox)
    return ['timebox set to ' + self.timebox]

class Voice(object):
  def __init__(self, args):
    self.status = args[0]
  
  def execute(self, **kwargs):
    kwargs.get('bot').setVoice(True if self.status == 'on' else False)
    return ['voice set to ' + self.status]

class Status(object):
  def execute(self, **kwargs):
    resp = []
    scanners = kwargs.get('scanners')
    bot = kwargs.get('bot')
    if len(scanners) > 0:
      resp.append('watching ' + ('Nothing' if not scanners[0].timebox else scanners[0].timebox))
    resp.append('I am ' + ('' if bot.voiced else 'not') + ' voiced')
    return resp
  
class Help(object):
  def __init__(self, args):
    cmd = args[0]
    if not HELP.has_key(cmd):
      self.response = 'No help for that command'
    else:
      self.response = HELP[cmd]
      
  def execute(self, **kwargs):
    return [self.response]

class StringResponse(object):
  def __init__(self, response):
    self.response = response
  def execute(self, **kwargs):
    return self.response

def makeCommand(args):
  if args[0] == 'diediedie':
    print 'remote quit'
    sys.exit(0)
  if not args[0] in BOT_COMMANDS:
    return None
  elif args[0] == 'commands':
    return StringResponse(['commands are: ' + ' '.join(BOT_COMMANDS)])
  elif args[0] == 'help':
    return Help(args[1:])
  elif args[0] == 'watch':
    return Watch(args[1:])
  elif args[0] == 'voice':
    return Voice(args[1:])
  elif args[0] == 'status':
    return Status()
  else:
    return None