import otalo_utils
import sys
from datetime import datetime

def get_call_durations(filename, destnum, phone_num_filter=False, date_start=False, date_end=False, quiet=False):
	durations = {}
	current_week_start = 0
	open_calls = {}
	
	f = open(filename)
	
	while(True):
		line = f.readline()
		if not line:
			break
		try:
		
		#################################################
		## Use the calls here to determine what pieces
		## of data must exist for the line to be valid.
		## All of those below should probably always be.
		
			phone_num = otalo_utils.get_phone_num(line)
			current_date = otalo_utils.get_date(line)	
			dest = otalo_utils.get_destination(line)			
		##
		################################################
			
			current_time = otalo_utils.get_time(line)
			
			if phone_num_filter and not phone_num in phone_num_filter:
				continue
				
			if date_start:
				if date_end:
					if not (current_date >= date_start and current_date < date_end):
						continue
					if current_date > date_end:
						break
				else:
					if not current_date >= date_start:
						continue
			
			if destnum.find(dest) == -1:
				continue
			
			if not current_week_start:
				current_week_start = current_date

			delta = current_date - current_week_start

			if delta.days > 6:
				#flush all open calls
				flush_open_calls(durations, open_calls, current_week_start)				
				open_calls = {}
				
				current_week_start = current_date
			
			if not current_week_start in durations:
				durations[current_week_start] = [] 

			if line.find("Start call") != -1:
				# check to see if this caller already has one open
				if phone_num in open_calls.keys() and current_time > open_calls[phone_num]['last']:
					# close out current call					
					call = open_calls[phone_num]
					del open_calls[phone_num]
					dur = call['last'] - call['start']		
					#print("closing out call pre-emptively: " + phone_num + ", duration: " + str(dur.seconds) + " ending " + otalo.date_str(current_date) + " " + otalo.time_str(current_time))
					durations[current_week_start].append([phone_num,dur])
					
				# add new call
				#print("adding new call: " + phone_num)
				open_calls[phone_num] = {'start':current_time, 'last':current_time }
					
			elif line.find("End call") != -1:
				if phone_num in open_calls.keys():
					# close out call				
					call = open_calls[phone_num]
					dur = current_time - call['start']			
					#print("closing out call: " + phone_num + ", duration: " + str(dur.seconds) + " ending " + otalo.date_str(current_date) + " " + otalo.time_str(current_time))
					durations[current_week_start].append([phone_num,dur])
					del open_calls[phone_num]
			elif line.find(phone_num):
				#print("updating call dur: " + phone_num)
				# this makes things conservative. A call is only officially counted if
				# it starts with a call_started
				if phone_num in open_calls.keys():
					open_calls[phone_num]['last'] = current_time
			
			#print("open_calls: " + str(open_calls))
		
		except KeyError as err:
			#print("KeyError: " + phone_num + "-" + otalo.date_str(current_date) + " " + otalo.time_str(current_time))
			raise
		except ValueError as err:
			#print("ValueError: " + line)
			continue
		except IndexError:
			continue
		except otalo_utils.PhoneNumException:
			#print("PhoneNumException: " + line)
			continue
	
	#flush the last week
	flush_open_calls(durations, open_calls, current_week_start)
	
	if not quiet:
		if phone_num_filter:
			print("Data for phone numbers: " + str(phone_num_filter))
		
		print("Average call duration, by week (s):")
		dates = durations.keys()
		dates.sort()
		secs = 0
		calls = 0
		for date in dates:
			durs_by_call = durations[date]
			durs = [dur[1].seconds for dur in durs_by_call]
			
			secs += sum(durs)
			calls += len(durs)
			print(date.strftime('%Y-%m-%d') +": "+ str(sum(durs)/len(durs)))
		
		if calls > 0:
			print('Overall Average: ' + str(secs/calls))
	
	return durations

def get_calls_by_duration(filename):
	current_week_start = 0
	open_calls = {}
	durations = {60:0, 120:0, 180:0, 240:0, 300:0, '+300':0}
	
	f = open(filename)
	
	while(True):
		line = f.readline()
		if not line:
			break
		try:
		
		#################################################
		## Use the calls here to determine what pieces
		## of data must exist for the line to be valid.
		## All of those below should probably always be.
		
			phone_num = otalo.get_phone_num(line)
			current_date = otalo.get_date(line)				
		##
		################################################
			
			current_time = otalo.get_time(line)

			if line.find("Start call") != -1:
				# check to see if this caller already has one open
				if phone_num in open_calls.keys() and current_time > open_calls[phone_num]['last']:
					# close out current call					
					call = open_calls[phone_num]
					del open_calls[phone_num]
					dur = call['last'] - call['start']		
					#print("closing out call pre-emptively: " + phone_num + ", duration: " + str(dur.seconds) + " ending " + otalo.date_str(current_date) + " " + otalo.time_str(current_time))
					bucket_duration(dur, durations)
					
				# add new call
				#print("adding new call: " + phone_num)
				open_calls[phone_num] = {'start':current_time, 'last':current_time }
					
			elif line.find("End call") != -1:
				if phone_num in open_calls.keys():
					# close out call				
					call = open_calls[phone_num]
					dur = current_time - call['start']			
					#print("closing out call: " + phone_num + ", duration: " + str(dur.seconds) + " ending " + otalo.date_str(current_date) + " " + otalo.time_str(current_time))
					bucket_duration(dur, durations)
					del open_calls[phone_num]
			elif line.find(phone_num):
				#print("updating call dur: " + phone_num)
				# this makes things conservative. A call is only officially counted if
				# it starts with a call_started
				if phone_num in open_calls.keys():
					open_calls[phone_num]['last'] = current_time
			
			#print("open_calls: " + str(open_calls))
		
		except KeyError as err:
			#print("KeyError: " + phone_num + "-" + otalo.date_str(current_date) + " " + otalo.time_str(current_time))
			raise
		except ValueError as err:
			#print("ValueError: " + line)
			continue
		except IndexError:
			continue
		except otalo.PhoneNumException:
			#print("PhoneNumException: " + line)
			continue
	
	#flush the last week
	flush_open_calls(open_calls, current_week_start)
	
	print("Calls by duration (seconds):")
	calls = 0
	for bucket in durations:
		calls += durations[bucket]
		print(str(bucket) +":\t"+ str(durations[bucket]))
	print("total is " + str(calls))
	
def bucket_duration(dur, durations):
	if (dur.seconds <= 60):
		durations[60] += 1
	elif (dur.seconds <= 120):
		durations[120] += 1
	elif (dur.seconds <= 180):
		durations[180] += 1
	elif (dur.seconds <= 240):
		durations[240] += 1
	elif (dur.seconds <= 300):
		durations[300] += 1
	else:
		durations['+300'] += 1
	

def flush_open_calls(durations, open_calls, week):
	for num in open_calls.keys():
		last = open_calls[num]['last']
		dur = last - open_calls[num]['start']
		#print("flushing: " + num + ", duration: " + str(dur.seconds))
		durations[week].append([num,dur])
	
def main():
	if len(sys.argv) != 2:
		print("Wrong")
	else:
		f = sys.argv[1]
		get_call_durations(f, destnum='30142000')
		#get_calls_by_duration(f)

#main()
