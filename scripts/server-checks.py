import sys, subprocess
from otalo.ao.models import Line, User, Dialer
from otalo.sms.models import Config
from otalo.sms import sms_utils

SERVER_NAME = 'voicebox'
NUM_PRIS = 7
SENDER = User.objects.get(pk=2)
ADMINS = User.objects.filter(pk__in=[2])
CONFIG = Config.objects.get(pk=1)

def report_error(msg):
	sms_utils.send_sms(CONFIG, ADMINS, SERVER_NAME+": "+msg, SENDER)
	
def check_pris():
	for i in range(1,NUM_PRIS+1):	
		p = subprocess.Popen(["wanpipemon", "-i", "w"+str(i)+"g1", "-c", "xm"], stdout=subprocess.PIPE)
		out,err = p.communicate()
		
		if 'Low' in out:
			dialer = Dialer.objects.filter(dialstring_prefix__contains='grp'+str(i))
			error_msg = 'PRI line w'+str(i)+'g1'
			if bool(dialer):
				dialer = dialer[0]
				error_msg += " (grp"+str(i)+ ")"
			error_msg += ' is down!'
			print("error "+error_msg)
			report_error(error_msg)

def check_freeswitch():
	p = subprocess.Popen(["pgrep", "freeswitch"], stdout=subprocess.PIPE)
	out,err = p.communicate()
	
	if out == '':
		print("error FreeSWITCH is down!")
		report_error("FreeSWITCH is down!")
		
	
	p = subprocess.Popen(['grep', '"LuaSQL: Error connecting to database."', '/usr/local/freeswitch/log/freeswitch.log'], stdout=subprocess.PIPE)
	out,err = p.communicate()
	
	if out != '':
		print("LuaSQL database connection issue!")
		report_error("MySQL connection is down!")
		
	
	p = subprocess.Popen(['grep', '"LuaSQL: Error connecting: Out of memory."', '/usr/local/freeswitch/log/freeswitch.log'], stdout=subprocess.PIPE)
	out,err = p.communicate()
	
	if out != '':
		print("LuaSQL out of memory!")
		report_error("LuaSQL memory is down!")
		
	
	p = subprocess.Popen(['grep', '"Originate Resulted in Error Cause: 111 [PROTOCOL_ERROR]"', '/usr/local/freeswitch/log/freeswitch.log'], stdout=subprocess.PIPE)
	out,err = p.communicate()
	
	if out != '':
		print("PROTOCOL ERROR")
		report_error("[PROTOCOL_ERROR] is down!")
		# try to restart
		# UPDATE: this doesn't work, don't do
		#p = subprocess.Popen(["/etc/init.d/freeswitch", "start"])
		#p.wait()
		
def main():
	check_freeswitch()
	check_pris()
	
main()
