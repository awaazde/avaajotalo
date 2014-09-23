import sys, subprocess
import requests, json
from datetime import datetime, timedelta
from requests.exceptions import ConnectionError
from otalo.ao.models import Line, User, Dialer
from otalo.sms.models import Config, SMSMessage
from otalo.sms import sms_utils


SERVER_NAME = 'voicebox'
#specify active PRIs
NUM_PRIS = []
SENDER = User.objects.get(pk=2)
ADMINS = User.objects.filter(pk__in=[2,69016])
CONFIG = Config.objects.get(pk=2)

#celery flower api base url e.g. http://awaaz.de:5555/api/
WS_BASE_URL = ''
WS_WORKER = 'workers'

# names of workers e.g. w1@voicebox
WORKERS = []
DEFAULT_BUFFER_MINS = 5

MYSQL_CONNECTION_THRESH = 2000
PROTOCOL_ERROR_THRESH = 3000
CALL_REJECTED_ERROR_THRESH = 4000

def report_error(msg, buffer=DEFAULT_BUFFER_MINS):
	now = datetime.now()
	if not SMSMessage.objects.filter(text=SERVER_NAME+': '+msg, sent_on__gt=now-timedelta(minutes=buffer)).exists():
		sms_utils.send_sms(CONFIG, ADMINS, SERVER_NAME+": "+msg, SENDER)
	
def check_pris():
	for i in NUM_PRIS:
		p = subprocess.Popen(["/usr/sbin/wanpipemon", "-i", "w"+str(i)+"g1", "-c", "xm"], stdout=subprocess.PIPE)
		out,err = p.communicate()
		
		if 'Low' in out:
			dialer = Dialer.objects.filter(dialstring_prefix__contains='grp'+str(i))
			error_msg = 'PRI line w'+str(i)+'g1'
			if bool(dialer):
				dialer = dialer[0]
				error_msg += " (grp"+str(i)+ ")"
			error_msg += ' is down!'
			print("error "+error_msg)
			report_error(error_msg, 10)

def check_freeswitch():
	p = subprocess.Popen(["pgrep", "freeswitch"], stdout=subprocess.PIPE)
	out,err = p.communicate()
	
	if out == '':
		print("error FreeSWITCH is down!")
		report_error("FreeSWITCH is down!")	
	
	p = subprocess.Popen(['grep', 'LuaSQL: Error connecting to database.', '/usr/local/freeswitch/log/freeswitch.log'], stdout=subprocess.PIPE)
	out,err = p.communicate()
	
	if out != '':
		if 'Too many connections' in out:
			print("LuaSQL database too many connections!")
			report_error("MySQL too many connections " + str(len(out)) + " is down!", 6*60)
		elif len(out) > MYSQL_CONNECTION_THRESH:
			print("LuaSQL database connection issue!")
			report_error("MySQL connection " + str(len(out)) + " is down!", 3*60)
	
	p = subprocess.Popen(['grep', 'LuaSQL: Error connecting: Out of memory.', '/usr/local/freeswitch/log/freeswitch.log'], stdout=subprocess.PIPE)
	out,err = p.communicate()
	
	if out != '':
		print("LuaSQL out of memory!")
		report_error("LuaSQL memory " + str(len(out)) + " is down!", 6*60)
		
	
	p = subprocess.Popen(['grep', 'Originate Resulted in Error Cause: 111 \[PROTOCOL_ERROR\]', '/usr/local/freeswitch/log/freeswitch.log'], stdout=subprocess.PIPE)
	out,err = p.communicate()
	
	if out != '' and len(out) > PROTOCOL_ERROR_THRESH:
		# include the length of the output
		# to tell whether new errors are happening
		print("PROTOCOL ERROR")
		report_error("[PROTOCOL_ERROR] " + str(len(out)) + " is down!", 3*60)
		
	p = subprocess.Popen(['grep', 'Originate Resulted in Error Cause: 21 \[CALL_REJECTED\]', '/usr/local/freeswitch/log/freeswitch.log'], stdout=subprocess.PIPE)
	out,err = p.communicate()
	
	if out != '' and len(out) > CALL_REJECTED_ERROR_THRESH:
		# include the length of the output
		# to tell whether new errors are happening
		print("CALL REJECTED")
		report_error("[CALL_REJECTED] " + str(len(out)) + " is down!", 3*60)

def check_celery():
	if WORKERS:
		try:
			response = requests.get(WS_BASE_URL + WS_WORKER)
			if response.status_code == 200:
				workers_data = response.json()
				for worker in WORKERS:
					if worker in workers_data:
						status = workers_data[worker]['status']
						if not status:
							print(worker + ' status is down')
							report_error('celery ' + worker + ' status is down!') 
					else:
						print(worker + ' is down!')
						report_error('celery ' +worker + ' is down!') 
			else:
				print('Flower response is down!')
				report_error('Flower response is down!')
		except ConnectionError as e:
			print('Flower connection is down')
			report_error('Flower connection is down!')

def main():
	check_freeswitch()
	check_pris()
	check_celery()
	
main()
