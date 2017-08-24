#DO NO USE THIS TOOL

This tool is deprecated in favor of using nmaps tso-enum script: https://nmap.org/nsedoc/scripts/tso-enum.html

psikotik
========

PSIKOTIK TSO User Enumerator. A fast TSO user enumerator written in straight
python without the need for s3270 or x3270. 

It should mostly work on any mainframe. If it doesn't get to the TSO logon
screen then you need to sniff a real connection to the mainframe and find out
what the hex stream looks like when you type 'TSO1' (for example) and change
tso_command to reflect that value. 

http://www.youtube.com/watch?v=sFJzvlU6EVk

arguments:
  -h, --help            show this help message and exit
  
  -t TARGET, --target TARGET  Mainframe IP address or Hostname
  
  -p PORT, --port PORT  Mainframe 3270 server port number, default is port 23
  
  -s SLEEP, --sleep SLEEP Seconds to sleep. !only change if you have problems connecting!. The default is 4 seconds.
  
  -f TSO_FAKE, --fake TSO_FAKE Fake or bad userid to use to initially get us to TSO panel. Only change if default doesn't work. Be careful with this, userIDs can only contain letters, numbers or $,# and @
  
  -u USERFILE, --userfile USERFILE  File containing list of usernames
  
  -q, --quiet           Don't show all attempts, just discovered users
  
  -l, --nologo          Do not display the logo
  
  -v, --verbose         Be verbose
