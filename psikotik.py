#!/usr/bin/python

import re #for username regex
from Queue import Queue #for threading
from select import select
import socket
import os
import time
import random
import getpass
import signal
import sys
import argparse #needed for argument parsing

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


##Colours for us to use
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
#--------------------------\
# Logo by Dark Warri0r from Punc0196:
# http://sixteencolors.net/pack/punc0196/12-PSIKO.ASC
#--------------------------/
	print bcolors.DARKGREY + '''
     .       ..       . .   . .        . .       ..         ..   . .        .
     .       ..       . .   . .        . .       ..         ..   . .        .'''+bcolors.DARKBLUE+'''
     :       ::    ___: :   : :        : :       ::         ::   : :        :
     |    o  ||   (__   |   | |        / |   |   |`--.   ,--'|   | |        /'''+bcolors.BLUE+'''
     |    __,'`.__   `. |   | |       <  |   |   |   |   |   |   | |       <
     |   |     ___)   | |   | |        \ |   |   |   |   |   |   | |        \\'''+bcolors.WHITE+'''
     |   |    |       | |   | |    \    >|   |   |   |   |   |   | |    \    >
    (_____)'''+bcolors.DARKGREY+'''SoF'''+bcolors.WHITE+'''|______,'(_____)`.__,'`\/' `._____,'  (_____) (_____)`.__,'`\/'
'''
	print bcolors.DARKGREY+'''
,xX$'"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""$$$
$$$' x(     tool     : '''+bcolors.BLUE+"PSI"+bcolors.WHITE+"K"+bcolors.BLUE+"OTI"+bcolors.WHITE+"K"+bcolors.RED+" TSO "+bcolors.WHITE+"USER ENUMERATOR"+bcolors.DARKGREY+'''                     )x  $$$
$$$  x(    creator   : '''+bcolors.GREEN+"Soldier of Fortran"+bcolors.DARKGREY+'''                               )x ,$$$
$$$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx4$$"' '''


	return "BBS4EVAR"
def osp(stringer): #Old School Printer
    for c in stringer:
	sys.stdout.write( c )
        sys.stdout.flush()
        time.sleep(random.uniform(0, 0.35))
    print "\n",

def mcp(s):
    for c in s:
	sys.stdout.write( c )
        sys.stdout.flush()
        time.sleep(random.uniform(0, 0.1))
    print "\n",



def encom_easter():
	print bcolors.BLUE
	osp("D9165747830")
	time.sleep(random.random())	
	print "\n\nEEEEEEE"
	print "EE      nn nnn    cccc  oooo  mm mm mmmm"
	time.sleep(random.random())
	print "EEEEE   nnn  nn cc     oo  oo mmm  mm  mm"
	print "EE      nn   nn cc     oo  oo mmm  mm  mm"
	time.sleep(random.random())	
	print "EEEEEEE nn   nn  ccccc  oooo  mmm  mm  mm\n"
	print "READY"
	time.sleep(random.random())	
	osp("CLU")                                          
	time.sleep(random.random())		
	mcp("\nREQUEST ACCESS TO CLU PROGRAM")
	time.sleep(random.random())	
	osp("CODE 6 PASSWORD TO MEMORY 0222")
	time.sleep(random.random())
	mcp("\nILLEGAL CODE...")
	mcp("CLU PROGRAM DETACHED FROM SYSTEM\n")
	osp("REQUEST ACCESS TO CLU PROGRAM")	
	time.sleep(random.random())	
	mcp("\nLAST LOCATION: HIGH CLEARANCE MEMORY C4")
	print bcolors.RED
	mcp("\n\nCONNECTION CLOSED\n\n")
	print bcolors.BLUE
	time.sleep(3)	
	osp("D9165747830")	
	time.sleep(random.random())	
	print "\n\nEEEEEEE"
	print "EE      nn nnn    cccc  oooo  mm mm mmmm"
	time.sleep(random.random())
	print "EEEEE   nnn  nn cc     oo  oo mmm  mm  mm"
	print "EE      nn   nn cc     oo  oo mmm  mm  mm"
	time.sleep(random.random())	
	print "EEEEEEE nn   nn  ccccc  oooo  mmm  mm  mm\n"
	print "READY"
	time.sleep(random.random())	
	osp("ACCESS CODE 6. PASSWORD SERIES PS 17.")
	osp("REINDEER FLOTILLA -WRITE")
	time.sleep(random.random())	
	os.system("clear")
	print "\n\n\n\n\n"
	flynn = "YOU SHOULDN'T HAVE COME BACK ",getpass.getuser().upper()
	mcp(flynn)
	time.sleep(3)
	print "\n\n\nREADY"
	time.sleep(random.random())	
	osp("REACTIVATE HIGH CLEARANCE MEMORY LOCATION C4")
	time.sleep(random.random())	
	osp("................")
	time.sleep(random.random())
	osp("................")
	osp("................")	
	time.sleep(random.random())
	print "CODE SERIES C49-123",
	mcp(" ... ACTIVATE.")
	time.sleep(random.random())	
	print "CODE SERIES C4D-E38", 
	mcp(" ... ACTIVATE.")
	time.sleep(random.random())	
	print "CODE SERIES C4C-036", 
	mcp(" ... ACTIVATE.")	
	time.sleep(random.random())
	os.system("clear")
	print "\n\n\n\n\n"	
	flynn = "THAT ISN'T GOING TO DO YOU ANY GOOD ",getpass.getuser().upper()
	mcp(flynn)
	time.sleep(3)
	print "\n\nREADY"
	time.sleep(random.random())	
	osp("DIVIDE SYS6.RAND.FLOAT BY ZERO")
	print "\n\n"
	osp("xXxXXXxXX.../\//////////////")
	mcp("   c  x   $   @  #  */  ****")
	mcp(" 00 <.  $ v g   b...........")
	time.sleep(2)
	os.system("clear")
	print "\n\n"
	time.sleep(random.random())	
	flynn = "STOP ",getpass.getuser().upper(),"\nYOU REALIZE I CAN'T ALLOW THIS"
	mcp(flynn)
	time.sleep(4)
	print "\n\nREADY"
	time.sleep(random.random())	
	mcp("\nACCESS COMMUNICATION SOCKET")
	time.sleep(3)
	mcp("TRON PROGRAM UPDATED\n")
	time.sleep(random.random())	
	print bcolors.WHITE+"\n[TRON]"+bcolors.BLUE+"",
	mcp(" DEACTIVATE MCP IN PROGRESS")
	time.sleep(random.random())	
	mcp("................")
	time.sleep(random.random())
	mcp("................")
	mcp("................")	
	print bcolors.WHITE+"\n[TRON]"+bcolors.BLUE+"",
	mcp(" MCP DEACTIVATED")
	print "\n\nREADY"
	time.sleep(random.random())
	osp("PRINT HISTORY - DSK1:DILLINGER.GAMES.ACCOUNTING.TRASH")
	time.sleep(random.random())	
	mcp('''
DSK1:DILLINGER.GAMES.ACCOUNTING.TRASH
--------------------------------------------------------------------------------
Access control:
	This User: Encryption protection (level 5)
	Other Users: Access Denied

Access History:
	File name   Project name       File Created       Last Access
	WORM        "Worm"             04-AUG by FLYNN    30-AUG by DILLINGER
	TANK        "Tank Hunter"      18-MAY by FlYNN    30-AUG by DILLINGER
	LITBIKE     "Light Bike"       22-JUN by FLYNN    30-AUG by DILLINGER
	PARA        "Space Paranoids"  21-MAR by FLYNN    30-AUG by DILLINGER

''') 
	print bcolors.ENDC
	sys.exit(0)
	




#start argument parser
parser = argparse.ArgumentParser(description='PSIKOTIK TSO User Enumerator. A fast TSO user enumerator written in straight python without the need for s3270 or x3270. You must make a simple change to the script. See the guide at http://github.com/mainframed/psikotik',epilog='Eh TSO Brutus?')
parser.add_argument('-t','--target', help='Mainframe IP address or Hostname', required=True,dest='target')
parser.add_argument('-p','--port', help='Mainframe 3270 server port number, default is port 23', required=False,default="23",dest='port')
parser.add_argument('-s','--sleep',help='Seconds to sleep. !only change if you have problems connecting!. The default is 4 seconds.',default=4,type=int,dest='sleep')
parser.add_argument('-f','--fake',help='Fake or bad userid to use to initially get us to TSO panel. Only change if default doesn\'t work. Be careful with this, userIDs can only contain letters, numbers or $,# and @',default="fakey",dest='tso_fake')
parser.add_argument('-u','--userfile',help='File containing list of usernames', required=True,dest='userfile')
parser.add_argument('-q','--quiet',help='Don\'t show all attempts, just discovered users',default=True,dest='quiet',action='store_false')
parser.add_argument('-l','--nologo',help='Do not display the logo',default=True,dest='logo',action='store_false')
parser.add_argument('-v','--verbose',help='Be verbose',default=False,dest='verbose',action='store_true')
args = parser.parse_args()
results = parser.parse_args() # put the arg results in the variable results


if results.tso_fake == "ENCOM" and results.port == "42":
	easter_came_early = encom_easter()

if results.logo: yay = logo()


if results.tso_fake[0].isdigit() or len(results.tso_fake.strip()) > 7:# or re.match(r"\W", results.tso_fake): 
	print bcolors.RED+"[!]You entered an invalid TSO userID with -f. The rules are: <=7, cannot start with a number and only letters/numbers"
	print "       you entered",results.tso_fake,""+bcolors.ENDC
	sys.exit(0)

usernames = Queue() #for eventual threading

#--------------------------\
# catch the ctrl-c to exit and say something instead of Punt!
#--------------------------/
def signal_handler(signal, frame):
        print "BRUTE!" + bcolors.ENDC
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

#--------------------------\
# User file enum chunk     
#--------------------------/
userfile=open(results.userfile)
total_users = 0
skipped = 0

for username in userfile:

#TSO has weird rules for the user name so this checks that:
# - The username doesn't start with a number
# - It's not longer than 7 chars
# - It only contains A-z, 0-9, #, @ and $
	if not username[0].isdigit() and len(username.strip()) <= 7 and not re.match(r"[\W]", username): 
		usernames.put(username.strip()) #using a queue for eventually adding threading. 
		total_users += 1
	else:
		if results.verbose: print ""+ bcolors.PURPLE + "skipping " +bcolors.WHITE+ "" + username.strip()
		skipped += 1
print  bcolors.DARKGREY+"lll"+bcolors.PURPLE + " User Names ->  " +bcolors.WHITE+ "" + str(total_users)
print bcolors.DARKGREY+":::"+bcolors.PURPLE + " Skipped Names ->  " +bcolors.WHITE+ "" + str(skipped)

for i in xrange(1000): #for threading to be added at a later date
	usernames.put(None)

#-------------------------|


try:
	MFsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	MFsock.connect( (results.target, int(results.port)) )
	MFsock.setblocking(0)
except Exception, e:
 	print  bcolors.RED + "[ERR] could not connect to ",results.target,":",results.port,"" + bcolors.ENDC
	print bcolors.RED + "",e,"" + bcolors.ENDC
	sys.exit(0)

###################################################
# Declarations. It ain't got no aliby
########
at_screen = False #This is used below to send the TSO command in the stream. There's no way to tell when the MF screen shows up otherwise.
enumeratin = False #Connect to the mainframe. Then enumerate when this becomes true
done = False #such hackery 
pouring_one_out = "\x40" #for my homies
too_many = False # Make sure we don't skip a user if we reach the max guesses
valid_users = list() #A 1d array to hold the found user IDs. Displays all users IDs at the end. 


#print bcolors.PURPLE+"    Ultra Hyper-Threading Technology:"+bcolors.RED+" ON" #It's actually just normal threads. But, meh. When threading is added this will be enabled. 

while(1):
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

	if re.match("\xFF\xFD\x18$",buffer): #You need uppercase hex values ...,,,;;;;:::::The more you know 
		MFsock.send("\xff\xfb\x18") # Will Terminal type

	if re.match("\xFF\xFA\x18\x01\xFF\xF0$",buffer): MFsock.send("\xff\xfa\x18\x00\x49\x42\x4d\x2d\x33\x32\x37\x39\x2d\x32\x2d\x45\xff\xf0") #Sending terminal type IBM-3279-2-E
	if re.match ("\xFF\xFD\x19\xFF\xFB\x19$",buffer): MFsock.send("\xff\xfb\x19\xff\xfd\x19") # Will end of record/Do End of record
	if re.match("\xFF\xFD\x00\xFF\xFB\x00$",buffer): 
		MFsock.send("\xff\xfb\x00\xff\xfd\x00") # Will Binary Tranmission/Do Binary Transmission
		at_screen = True
	if at_screen:#		if re.match("\xFF\xEF$",buffer): 
		time.sleep(results.sleep) #the hackiest work around
		at_screen = False
		if results.verbose: print bcolors.YELLOW + "    [!]Sending TSO command"
		###############################################################
		###############################################################
		###############################################################
		# If the script doesn't work you need to change me by sniffing your connection and see what row/column
		# and command you need to run. For now it works on ADCD
		MFsock.send("\x7d\xd9\xd8\x11\xd9\xd5\xa3\xa2\x96\xff\xef") #Putting TSO at row 21 column 22
		###############################################################
		###############################################################
		###############################################################
	
	if re.match("\xF3\x00\x06\x40\x00\xF1\xC2\x00\x05\x01\xFF\xFF\x02\xFF\xEF$",buffer):
		MFsock.send("\x88\x00\x16\x81\x86\x00\x08\x00\xf4\xf1\xf1\xf2\xf2\xf3\xf3\xf4\xf4\xf5\xf5\xf6\xf6\xf7\xf7\x00\x0d\x81\x87\x04\x00\xf0\xf1\xf1\xf2\xf2\xf4\xf4\x00\x22\x81\x85\x82\x00\x07\x10\x00\x00\x00\x00\x07\x00\x00\x00\x00\x65\x00\x25\x00\x00\x00\x02\xb9\x00\x25\x01\x00\xf1\x03\xc3\x01\x36\x00\x2e\x81\x81\x03\x00\x00\x50\x00\x18\x00\x00\x01\x00\x48\x00\x01\x00\x48\x07\x10\x00\x00\x00\x00\x00\x00\x13\x02\x00\x01\x00\x50\x00\x18\x00\x00\x01\x00\x48\x00\x01\x00\x48\x07\x10\x00\x1c\x81\xa6\x00\x00\x0b\x01\x00\x00\x50\x00\x18\x00\x50\x00\x18\x0b\x02\x00\x00\x07\x00\x10\x00\x07\x00\x10\x00\x07\x81\x88\x00\x01\x02\x00\x16\x81\x80\x80\x81\x84\x85\x86\x87\x88\xa1\xa6\xa8\x96\x99\xb0\xb1\xb2\xb3\xb4\xb6\x00\x08\x81\x84\x00\x0a\x00\x04\x00\x06\x81\x99\x00\x00\xff\xef") #Whoa! Look it up. 
	if re.match("\xF1\xC2\xFF\xEF$",buffer) or re.search("\xF1\xC2\x11\x40\x40\x1D\xC8\xC9\xD2\xD1\xF5\xF6\xF7\xF0\xF0",buffer): 
		if results.verbose: print bcolors.YELLOW+"    [!]Sending bad userid", fake_tso_user
		MFsock.send("\x7d\xc1\xd5\x11\x40\x5a"+AsciiToEbcdic(results.tso_fake)+"\xff\xef")
	if re.search("\xC8"+AsciiToEbcdic(results.tso_fake.upper()),buffer): #c8 + userid = bad :)
			if results.verbose: print bcolors.YELLOW+"    [!]At TSO: "+bcolors.GREEN+"!!!!!Start Enumeratin'!!!!!"
			enumeratin = True
			if not too_many: user = usernames.get()
			if results.quiet: print bcolors.YELLOW+"    [!]Trying"+bcolors.RED+"",user,
			encoded = AsciiToEbcdic(user)+pouring_one_out*(7-len(user))
			MFsock.send("\x7d\xc9\xc3\x11\xc6\xe3"+encoded+"\xff\xef")
	elif re.search("\xE8"+AsciiToEbcdic(results.tso_fake.upper()),buffer): #e8 + userid matches a known user
			print bcolors.RED+"    [!]At TSO with a Valid UserID when we need a bad one initially, pick a different userID with -f [user]"+ bcolors.ENDC

			sys.exit(0)
	########
	####
	# Phew, after all that we can now start enumerating users. Sorta
	####
	########
	while enumeratin:

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


		if re.search("LOGON REJECTED, TOO MANY ATTEMPTS",ascii_out):
			if results.verbose: print bcolors.YELLOW+"\n    [!]LOGON REJECTED, TOO MANY ATTEMPTS: Restarting"
			at_screen = True
			enumeratin = False
			too_many = True
			encoded = AsciiToEbcdic(user)+pouring_one_out*(7-len(user))
			MFsock.send("\x7d\xc9\xc3\x11\xc6\xe3"+encoded+"\xff\xef")
			time.sleep(results.sleep)
		elif re.search("\xC8"+AsciiToEbcdic(user.upper()),buffer):
			if results.quiet: print bcolors.BLUE+"\t - Not a User"
			user = usernames.get()
			if user == None: 
				done = True
				break
			if results.quiet: print bcolors.YELLOW+"    [!]Trying"+bcolors.RED+"",user,
			encoded = AsciiToEbcdic(user)+pouring_one_out*(7-len(user))
			MFsock.send("\x7d\xc9\xc3\x11\xc6\xe3"+encoded+"\xff\xef")
		elif re.search("\xE8"+AsciiToEbcdic(user.upper()),buffer):
			if results.quiet: print bcolors.GREEN+"\t - User FOUND!"
			else: print bcolors.YELLOW+"    [+]Valid User Found:"+bcolors.GREEN+"",user.upper()
 
			valid_users.append(user)
			MFsock.send("\xf3\xc9\xc3\xff\xef")
			at_screen = True
			enumeratin = False
			if too_many: too_many = False
			time.sleep(results.sleep)

	if done: break


print bcolors.DARKGREY+'''
                                                                            :::
                                                                            111
,xX$'"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""$$$
$$$  x(  total found :'''+bcolors.RED+"",'%05d' % len(valid_users),""+bcolors.DARKGREY+'''                                           )x  $$$'''


for users in valid_users:
	print "$$$  x(  valid user  :"+bcolors.GREEN+"",users,""+bcolors.DARKGREY+"\t                                        )x ,$$$"


print '''$$$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx4$$"' '''

print bcolors.ENDC



