import sys, os
import pickle, base64, StringIO
import urllib2
import threading
import datetime, time
from elementtree import ElementTree as et

SEL_FIELDS = 'Name,ChangeDateUTC,ChangeComment,ChangeReason,ChangedBy.Name,ChangedBy.Nickname'

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
  def __init__(self, type, v1opts):
    self.v1opts = v1opts
    self.type = type
    self.timebox = None
  
  def fetch(self):
    url = self.v1opts['host'] + '/' + self.v1opts['enterprise'] + '/rest-1.v1/Hist/' + self.type + '?sel=' + SEL_FIELDS
    if self.timebox:
      url += '&where=Timebox.Name=\'' + self.timebox + '\''
    url += '&sort=ChangeDateUTC'
    
    req = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (self.v1opts['user'], self.v1opts['password']))[:-1]
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
      return 0
      
    # first we need to flush the cookie
    if os.path.exists(self.v1opts['cookiePath']):
      os.remove(self.v1opts['cookiePath'])
    self.timebox = timebox
    skipped = self.catchUp()
    return skipped
    # things should be good on the next scan
  
  def scan(self, maxNew=10):
    '''returns just the new items. '''
    if not self.timebox:
      return []
    
    existingCount = 0
    if os.path.exists(self.v1opts['cookiePath']):
      existingCount = int(open(self.v1opts['cookiePath'], 'r').read())
    xml = self.fetch()
    history = self._parseHistory(xml)
    # lop off the old ones.
    history = history[existingCount:]
    # trim the ones past max.
    if len(history) > maxNew:
      print 'trimming history from %d to %d' % (len(history), maxNew)
      history = history[:maxNew]
      
    f = open(self.v1opts['cookiePath'], 'w')
    
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









    