# v1-bot loves you

Things are crude at the moment.

v1.py polls VersionOne.  botty.py contains the IRC bot and startup.  

Look at the todos to see where you put the room and cookie path configuration. 

You can suss out V1_HOST and V1_ENTERPRISE from the URL you use to access V1 with a browser.

# TODO

* Document this stuff.
* Connect to irc (in separate thread) before polling v1
* Things would be a lot cleaner if there was a controller that consumed 
  messages from the scanners and pumped them into the irc bot.
* commands:
  *  get/set the timebox (when a new sprint starts)
  *  get details for a specific task/story.