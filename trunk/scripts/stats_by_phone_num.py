import otalo_utils
import sys
from datetime import datetime
from otalo.AO.models import Line, Forum, User, Message

def get_calls_by_number(filename, destnum=False, log="Start call", phone_num_filter=False, date_start=False, date_end=False, quiet=False, legacy_log=False, transfer_calls=False):
	calls = {}
	phone_nums = ''
	
	if phone_num_filter:
		for num in phone_num_filter:
			calls[num] = 0
	
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
			current_date = otalo_utils.get_date(line, legacy_log)
			dest = otalo_utils.get_destination(line, legacy_log)		
		##
		################################################
		
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
					
			if destnum and destnum.find(dest) == -1:
				#print("dest num not = " + destnum)
				continue
			
			# A hacky way to test for transfer call
			# In the future you want to compare this call's
			# start time to a time window related to the end
			# of the survey call (in which you can keep the flag
			# false and give a more targeted start and end date)
			if transfer_calls:
				if len(dest) < 10:
					continue
			elif len(dest) == 10:
				continue
			
			if line.find(log) != -1:
				if phone_num in calls.keys():
					calls[phone_num] += 1
				else:
					calls[phone_num] = 1
					phone_nums += phone_num + ','

		except ValueError as err:
			#print("ValueError: " + str(err.args))
			continue
		except IndexError:
			continue
		except otalo_utils.PhoneNumException:
			continue
		
	calls_sorted = sorted(calls.iteritems(), key=lambda(k,v): (v,k))
	calls_sorted.reverse()
	if not quiet:
		print("Number of "+ log + "'s by phone number:")
		
		total = 0
		for num, tot in calls_sorted:
		#for num, tot in calls.items():
			total += tot
			print(num +"\t"+str(tot))
			
		print('total is ' + str(total));	
		print('numbers are ' + phone_nums)
	return calls_sorted

def get_calls_by_feature(filename, destnum, phone_num_filter=0, date_start=False, date_end=False, quiet=False, legacy_log=False):
	features = {}
	feature_names = []
	feature_chosen = 0
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
			current_date = otalo_utils.get_date(line, legacy_log)
			dest = otalo_utils.get_destination(line, legacy_log)					
		##
		################################################
			
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
			
			if not legacy_log and destnum and destnum.find(dest) == -1:
				continue

			if phone_num not in features:
				features[phone_num] = {}
				
			if line.find("Start call") != -1:
				# check to see if this caller already has one open
				if phone_num in open_calls:
					# close out current call					
					del open_calls[phone_num]
					
				# add new call with no feature access yet
				open_calls[phone_num] = False
					
			elif line.find("End call") != -1:
				if phone_num in open_calls:
					# close out call				
					del open_calls[phone_num]
			elif phone_num in open_calls:
				feature_chosen = open_calls[phone_num]
				feature = line[line.rfind('/')+1:line.find('.wav')]
				curr_features = features[phone_num]
				
				if feature == "okyourreplies" or feature == "okplay_all" or feature == "okplay" or feature == "okrecord":
					if feature not in feature_names:
						feature_names.append(feature)
					if feature in curr_features.keys():
						curr_features[feature] += 1
					else:
						curr_features[feature] = 1
				elif feature == "okyouwant_pre" or feature == "okplaytag_pre":
					# on the next go-around, look for the feature
					open_calls[phone_num] = True
				elif feature_chosen:
					if feature not in feature_names:
						feature_names.append(feature)
					if feature in curr_features.keys():
						curr_features[feature] += 1
					else:
						curr_features[feature] = 1
					open_calls[phone_num] = False
			
		except KeyError as err:
			#print("KeyError: " + phone_num + "-" + otalo.date_str(current_date))
			raise
		except ValueError as err:
			#print("ValueError: " + line)
			continue
		except IndexError as err:
			continue
		except otalo_utils.PhoneNumException:
			#print("PhoneNumException: " + line)
			continue
		
	if not quiet:
		if phone_num_filter:
			print("Data for phone numbers: " + str(phone_num_filter))
			
		print("Number of calls by phone number, by feature:")
		header = "\t"
		for name in feature_names:
			header += name+"\t"
		print(header)
		numbers = features.keys()
		for num in numbers:
			row = num +"\t"
			for name in feature_names:
				if name in features[num]:
					row += str(features[num][name]) + "\t"
				else:
					row += "0\t"
			print(row)
		
def get_calls_by_geography(filename, demographics):

	calls = get_calls_by_number(filename, quiet=True)
	
###############################################
## Any function compiling stats by demographics
## must call this loading function first

	otalo.load_demographics(demographics)
##
###############################################
	geo_map = otalo.get_geo_map()
	
	print("Number of calls, by geography")
	for locale, numbers in geo_map.iteritems():
		total = 0
		for num in numbers:
			try:
				total += calls[num]
			except KeyError:
				#print("no calls found: " + num)
				continue
		
		print(locale + " (" + str(len(numbers)) + " nums): " + str(total))

def get_guj_nums_only(filename, log="welcome", quiet=False, legacy_log=False):
	calls = {}
	phone_nums = ''
	
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
			current_date = otalo_utils.get_date(line, legacy_log)
			dest = otalo_utils.get_destination(line, legacy_log)		
		##
		################################################
			if line.find('guj') == -1:
				continue
				
			if line.find(log) != -1:
				if phone_num in calls.keys():
					calls[phone_num] += 1
				else:
					calls[phone_num] = 1
					phone_nums += phone_num + ','

		except ValueError as err:
			#print("ValueError: " + str(err.args))
			continue
		except IndexError:
			continue
		except otalo_utils.PhoneNumException:
			continue

	if not quiet:
		print("Number of "+ log + "'s by phone number:")
		calls_sorted = sorted(calls.iteritems(), key=lambda(k,v): (v,k))
		calls_sorted.reverse()
		total = 0
		for num, tot in calls_sorted:
			total += tot
			print(num +": "+str(tot))
			
		print('total is ' + str(total))
		print('numbers are ' + phone_nums)
	return calls

def get_messages_by_number(numbers, date_start=False, date_end=False, quiet=False):
	numbers = set(numbers)
	messages = {}
	responses = {}
	users = User.objects.filter(number__in=numbers)
	
	for user in users:
		msgs = Message.objects.filter(user=user)
		if date_start:
			msgs = msgs.filter(date__gte=date_start)
		if date_end:
			msgs = msgs.filter(date__lte=date_end)
			
		messages[user.number] = msgs.count()
		
		resp_msgs = Message.objects.filter(thread__in=msgs, lft__gt=1)
		responses[user.number] = resp_msgs.count()
			
	if not quiet:
		print("Number of messages and responses received by phone number:")
		msgs_sorted = sorted(messages.iteritems(), key=lambda(k,v): (v,k))
		msgs_sorted.reverse()
		total = 0
		for num, tot in msgs_sorted:
			total += tot
			resps = responses[num]
			print(num +": "+str(tot)+","+str(resps))
			
		print('total is ' + str(total))

	return messages

def get_numbers_by_date(filename, destnum=False, log="Start call", date_start=False, date_end=False, quiet=False, legacy_log=False):
	calls = {}
	phone_nums = ''
	
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
			current_date = otalo_utils.get_date(line, legacy_log)
			dest = otalo_utils.get_destination(line, legacy_log)		
		##
		################################################
			if date_start:
				if date_end:
					 if not (current_date >= date_start and current_date < date_end):
						continue
				else:
					if not current_date >= date_start:
						continue
					
			if destnum and destnum.find(dest) == -1:
				#print("dest num not = " + destnum)
				continue
				
			if line.find(log) != -1:
				if phone_num not in calls.keys():
					calls[phone_num] = current_date
					phone_nums += phone_num + ','

		except ValueError as err:
			#print("ValueError: " + str(err.args))
			continue
		except IndexError:
			continue
		except otalo_utils.PhoneNumException:
			continue

	if not quiet:
		print("Phone numbers by date")
		calls_sorted = sorted(calls.iteritems(), key=lambda(k,v): (v,k))
		calls_sorted.reverse()
		total = 0
		for num, date in calls_sorted:
			print(num +": "+otalo_utils.date_str(date))
			
		print('numbers are ' + phone_nums)
	return calls

def new_and_repeat_callers(filename, destnum=False, log="Start call", date_start=False, date_end=False, quiet=False, legacy_log=False, transfer_calls=False):
	calls = {}
	phone_nums = ''
	already_called = []
	current_week_start = False
	
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
			current_date = otalo_utils.get_date(line, legacy_log)
			dest = otalo_utils.get_destination(line, legacy_log)		
		##
		################################################
			if date_start:
				if date_end:
					if not (current_date >= date_start and current_date < date_end):
						continue
					if current_date > date_end:
						break
				else:
					if not current_date >= date_start:
						continue
			
			if destnum and destnum.find(dest) == -1:
				continue
			
			# A hacky way to test for transfer call
			# In the future you want to compare this call's
			# start time to a time window related to the end
			# of the survey call (in which you can keep the flag
			# false and give a more targeted start and end date)
			if transfer_calls:
				if len(dest) < 10:
					continue
			elif len(dest) == 10:
				continue
				
			if not current_week_start:
				current_week_start = datetime(year=current_date.year, month=current_date.month, day=current_date.day)

			delta = current_date - current_week_start

			if delta.days > 6:
				current_week_start = datetime(year=current_date.year, month=current_date.month, day=current_date.day)

			if line.lower().find(log.lower()) != -1:
				if current_week_start in calls:
					if phone_num not in already_called:
						already_called.append(phone_num)
						calls[current_week_start]['new'] += 1
					else:
						calls[current_week_start]['repeat'] += 1
				else:
					if phone_num not in already_called:
						already_called.append(phone_num)
						calls[current_week_start] = {'new':1,'repeat':0}
					else:
						calls[current_week_start] = {'new':0,'repeat':1}

		except ValueError as err:
			#print("ValueError: " + str(err.args))
			continue
		except IndexError:
			continue
		except otalo_utils.PhoneNumException:
			continue
		
	if not quiet:
		print("Number of "+ log + "'s by new and repeat callers:")
		print("Date\tNew Caller Calls\tRepeat Caller Calls\tNew Calls Rate")
		dates = calls.keys()
		dates.sort()
		total = 0
		for date in dates:
			total += calls[date]['new'] + calls[date]['repeat'] 
			print(otalo_utils.date_str(date) +"\t"+str(calls[date]['new'])+"\t"+str(calls[date]['repeat'])+"\t"+str(float(calls[date]['new']) / float(calls[date]['repeat'])))

		print("total is " + str(total))
		print ("number of unique callers is " + str(len(already_called)))
	
	return calls

def get_posts_by_caller(line, forums=None, date_start=False, date_end=False, quiet=False):
	calls = {}
	if not forums:
		forums = Forum.objects.filter(line=line)
		
	users = User.objects.filter(message__forum__in=forums).distinct()
	if date_start:
		users = users.filter(message__date__gte=date_start)
	if date_end:
		users = users.filter(message__date__lt=date_end)
		
	for user in users:
		msgs = Message.objects.filter(user=user, forum__in=forums)
		if date_start:
			msgs = msgs.filter(date__gte=date_start)
		if date_end:
			msgs = msgs.filter(date__lt=date_end)
			
		calls[user] = msgs.count()
		
	calls_sorted = sorted(calls.iteritems(), key=lambda(k,v): (v,k))
	calls_sorted.reverse()
	if not quiet:
		print("Number of message posts by phone number:")
		
		total = 0
		n_callers = 0
		for user, tot in calls_sorted:
			total += tot
			n_callers += 1
			print(str(user) +"\t"+str(tot))
			
		print('total is ' + str(total));	
		print('num callers is ' + str(n_callers));	
	return calls_sorted

def get_online_time(filename, destnum=False, phone_num_filter=False, date_start=False, date_end=False, quiet=False):
	online_time = {}
	current_day = 0
	open_calls = {}
	
	f = open(filename)
	
	if phone_num_filter:
		# every phone number has an entry
		for num in phone_num_filter:
			online_time[num] = 0
	
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
			
			if destnum and destnum.find(dest) == -1:
				continue
			
			if line.find("Start call") != -1:
				# check to see if this caller already has one open
				if phone_num in open_calls.keys() and current_time > open_calls[phone_num]['last']:
					# close out current call					
					call = open_calls[phone_num]
					del open_calls[phone_num]
					dur = call['last'] - call['start']		
					#print("closing out call pre-emptively: " + phone_num + ", "+otalo_utils.date_str(current_date) + ", "+otalo_utils.get_sessid(line) + ", duration: " + str(dur.seconds))
					if phone_num in online_time:
						online_time[phone_num] += dur.seconds
					else:
						online_time[phone_num] = dur.seconds
				# add new call
				#print("adding new call: " + phone_num)
				open_calls[phone_num] = {'start':current_time, 'last':current_time }
					
			elif line.find("End call") != -1:
				if phone_num in open_calls.keys():
					# close out call				
					call = open_calls[phone_num]
					dur = current_time - call['start']			
					#print("closing out call: "+phone_num + ", "+otalo_utils.date_str(current_date) + ", "+ otalo_utils.get_sessid(line) + ", duration: " + str(dur.seconds))
					if phone_num in online_time:
						online_time[phone_num] += dur.seconds
					else:
						online_time[phone_num] = dur.seconds
					del open_calls[phone_num]
			elif phone_num in open_calls:
				#print("updating call dur: " + phone_num)
				# this makes things conservative. A call is only officially counted if
				# it starts with a call_started
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
	#flush_open_calls(online_time, open_calls, current_day)
	if not quiet:
		print("Total online time, by phone number (s):")
		for num, tot in online_time.items():
			print(num +"\t"+str(tot))
			
	return online_time

def get_num_listens(filename, destnum, phone_num_filter=False, date_start=False, date_end=False, quiet=False, transfer_calls=False):
	listens = {}
	durations = {}
	current_week_start = 0
	open_calls = {}
	
	if phone_num_filter:
		# every phone number has an entry
		for num in phone_num_filter:
			listens[num] = 0
	
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
			
			# A hacky way to test for transfer call
			# In the future you want to compare this call's
			# start time to a time window related to the end
			# of the survey call (in which you can keep the flag
			# false and give a more targeted start and end date)
			if transfer_calls:
				if len(dest) < 10:
					continue
			elif len(dest) == 10:
				continue
			
			if line.find("Start call") != -1:
				# check to see if this caller already has one open
				if phone_num in open_calls:
					# close out current call
					call = open_calls[phone_num]
					n_listens = call['listens']
					if phone_num in listens:
						listens[phone_num] += n_listens
					else:
						listens[phone_num] = n_listens
					dur = call['last'] - call['start']
					if n_listens in durations:
						durations[n_listens].append(dur)
					else:
						durations[n_listens] = [dur]
					del open_calls[phone_num]
				open_calls[phone_num] = {'start':current_date, 'last':current_date, 'listens':0 }
				
			elif line.find("End call") != -1:
				if phone_num in open_calls:
					# close out call				
					call = open_calls[phone_num]
					n_listens = call['listens']
					if phone_num in listens:
						listens[phone_num] += n_listens
					else:
						listens[phone_num] = n_listens
					dur = current_date - call['start']
					if n_listens in durations:
						durations[n_listens].append(dur)
					else:
						durations[n_listens] = [dur]
					del open_calls[phone_num]
			else:
				if line.find("Stream") != -1:
					if phone_num in open_calls:
						open_calls[phone_num]['listens'] += 1
				if phone_num in open_calls:
					#print("updating call dur: " + phone_num)
					# this makes things conservative. A call is only officially counted if
					# it starts with a call_started
					open_calls[phone_num]['last'] = current_date
				
			
		except KeyError as err:
			#print("KeyError: " + phone_num + "-" + otalo.date_str(current_date))
			raise
		except ValueError as err:
			#print("ValueError: " + line)
			continue
		except IndexError as err:
			#print("IndexError: " + line)
			continue
		except otalo_utils.PhoneNumException:
			#print("PhoneNumException: " + line)
			continue
	
	if not quiet:
		if phone_num_filter:
			print("Data for phone numbers: " + str(phone_num_filter))
				
		print("Number of listens, by number:")
		for num, tot in listens.items():			
			print(str(num) + "\t" + str(tot))	
			
	return listens

def main():
	if not len(sys.argv) > 1:
		print("Wrong")
	else:
		f = sys.argv[1]
		line = False
		if len(sys.argv) == 3:
			lineid = sys.argv[2]
			line = Line.objects.get(pk=lineid)
			#print('num is ' + line.number)
		if len(sys.argv) == 4:
			demographics_file = sys.argv[3]
		
		start=datetime(year=2011,month=1,day=1)
		get_calls_by_feature(f,line.number, date_start=start)
		#get_guj_nums_only(f, legacy_log=True)
		#get_calls_by_feature(f)
		#get_calls_by_geography(f, demographics_file)
		#get_messages_by_number(['9586550654'])
		#get_numbers_by_date(f, line.number)
			
#main()
