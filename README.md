# v1-bot loves you

Things are crude at the moment.

v1.py polls VersionOne.  botty.py contains the IRC bot and startup.  

Look at the todos to see where you put the room and cookie path configuration. 

You need to specify these things to construct an API URL:

* V1_HOST is 'https://www.something.com'
* V1_ENTERPRISE identifies your organization
* V1_USER is a v1 login name
* V1_PASS is a v1 password

You can suss out V1_HOST and V1_ENTERPRISE from the URL you use to access V1 with a browser.

# TODO

* Load settings (v1 env, chat room, server, etc.) from a configuration file.
* Figure out why ctrl+c doesn't kill everything.  (I'm new to python threading).
* Document this stuff.
