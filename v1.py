import sys, os
import pickle, base64, StringIO
import urllib2
import threading
import datetime, time
from elementtree import ElementTree as et

V1_HOST = os.getenv('V1_HOST')
V1_ENTERPRISE = os.getenv('V1_ENTERPRISE')
V1_USER = os.getenv('V1_USER')
V1_PASS = os.getenv('V1_PASS')
if not (V1_USER or V1_PASS):
    print 'V1 env not configured'
    sys.exit(-1)

SEL_FIELDS = 'Name,ChangeDateUTC,ChangeComment,ChangeReason,ChangedBy.Name,ChangedBy.Nickname'

def fetch(type, timebox):
  url = V1_HOST + '/' + V1_ENTERPRISE + '/rest-1.v1/Hist/' + type + '?sel=' + SEL_FIELDS
  if timebox:
    url += '&where=Timebox.Name=\'' + timebox + '\''
  url += '&sort=ChangeDateUTC'
  
  req = urllib2.Request(url)
  base64string = base64.encodestring('%s:%s' % (V1_USER, V1_PASS))[:-1]
  authheader =  "Basic %s" % base64string
  req.add_header("Authorization", authheader)
  try:
    handle = urllib2.urlopen(req)
    xml = handle.read()
    return xml
  except IOError, e:
    print '*** PROBLEM ***'
    print e.headers
    return None

class Asset(object):
  def __init__(self, type, id, name, changed, reason, who):
    self.type = type
    self.id = id
    self.name = name
    self.changed = changed
    self.reason = reason
    self.who = who
  
  def prettyString(self):
    return '%s "%s" updated by %s on %s. reason: %s' % (self.type, self.name, self.who, self.changed, self.reason)

class Scanner(object):
  def __init__(self, type, cookiePath):
    self.type = type
    self.cookiePath = cookiePath
    self.timebox = None
    
  def _parseHistory(self, xml):
    '''constructs a history object.'''
    assets = []
    tree = et.parse(StringIO.StringIO(xml))
    for elem in tree.findall('Asset'):
      params = {}
      for att in elem.findall('Attribute'):
        params[att.attrib['name']] = att.text
      asset = Asset(self.type, elem.attrib['id'], params['Name'], params['ChangeDateUTC'], params['ChangeReason'], params['ChangedBy.Name'])
      assets.append(asset)
    return assets
  
  def setTimebox(self, timebox):
    if (timebox == self.timebox):
      return
      
    # first we need to flush the cookie
    os.remove(self.cookiePath)
    self.timebox = timebox
    skipped = self.catchUp()
    return skipped
    # things should be good on the next scan
  
  def scan(self, maxNew=10):
    '''returns just the new items. '''
    if not self.timebox:
      return []
    
    existingCount = 0
    if os.path.exists(self.cookiePath):
      existingCount = int(open(self.cookiePath, 'r').read())
    xml = fetch(self.type, self.timebox)
    history = self._parseHistory(xml)
    # lop off the old ones.
    history = history[existingCount:]
    # trim the ones past max.
    if len(history) > maxNew:
      print 'trimming history from %d to %d' % (len(history), maxNew)
      history = history[:maxNew]
      
    f = open(self.cookiePath, 'w')
    
    f.write(str(len(history) + existingCount))
    f.close()
    if len(history) > 0:
      print 'skipping %d history items' % existingCount
      print '%s %d new items' % (self.type, len(history))
    return history
  
  def catchUp(self):
    count = 0
    scan_count = len(self.scan(1000))
    while scan_count > 0:
      count += scan_count
      scan_count = len(self.scan(1000))
    print '%s caught up by skipping %d' % (self.type, count)
    return count
    
class ScanThread(threading.Thread):
  def __init__(self, scanner, outputter):
    threading.Thread.__init__(self)
    self.scanner = scanner
    self.outputter = outputter
    
  def run(self):
    while True:
      updates = self.scanner.scan()
      for asset in updates:
        self.outputter.puts(asset.prettyString())
      time.sleep(10)









    