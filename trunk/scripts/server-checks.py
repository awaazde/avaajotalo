import sys, subprocess
from otalo.ao.models import Line, User
from otalo.sms.models import Config
from otalo.sms import sms_utils

SERVER_NAME = 'voicebox'
NUM_PRIS = 7
SENDER = User.objects.get(pk=2)
ADMINS = User.objects.filter(pk__in=[2])
CONFIG = Config.objects.get(pk=1)

def report_error(msg):
	sms_utils.send_sms(CONFIG, ADMINS, SERVER_NAME+": "+msg, sender)
	
def check_pris():
	for i in range(NUM_PRIS):	
		p = subprocess.Popen(["wanpipemon", "-i", "w"+str(i)+"g1", "-c", "xm"], stdout=subprocess.PIPE)
		out,err = p.communicate()
		
		if 'Low' in out:
			line = Line.objects.filter(dialstring_prefix__contains='grp'+str(i))
			error_msg = 'PRI Line w'+str(i)+'g1 down'
			if bool(line):
				line = line[0]
				error_msg += " "+line.name + '-' + line.number
			print("error "+error_msg)
			report_error(error_msg)

def check_freeswitch():
	p = subprocess.Popen(["pgrep", "freeswitch"], stdout=subprocess.PIPE)
	out,err = p.communicate()
	
	if out == '':
		print("error FreeSWITCH is down!")
		report_error("FreeSWITCH is down!")
			
def main():
	check_freeswitch()
	check_pris()
	
main()
