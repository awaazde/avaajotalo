import otalo_utils
import sys
from datetime import datetime
from otalo.AO.models import Line, User, Message

def get_calls_by_number(filename, destnum=False, log="Start call", date_start=False, date_end=False, quiet=False, legacy_log=False, transfer_calls=False):
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
			total += tot
			print(num +": "+str(tot))
			
		print('total is ' + str(total));	
		print('numbers are ' + phone_nums)
	return calls_sorted

def get_calls_by_feature(filename):		
	features = {}
	open_calls = []
	feature_chosen = 0
	
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
			
			if not phone_num in features.keys():
				features[phone_num] = {'q':0, 'a':0, 'r':0, 'e':0} 
				
			if line.find("Start call") != -1:
				# check to see if this caller already has one open
				if phone_num in open_calls:
					# close out current call					
					open_calls.remove(phone_num)

				# add new call
				#print("adding new call: " + phone_num)
				open_calls.append(phone_num)

			elif line.find("End call") != -1:
				if phone_num in open_calls:
					# close out call				
					open_calls.remove(phone_num)
			elif phone_num in open_calls:
				if line.find("okyouwant_pre") != -1:
					# on the next go-around, look for the feature
					feature_chosen = 1
					continue
				if feature_chosen and line.find("qna") != -1:
					features[phone_num]['q'] += 1
				elif feature_chosen and line.find("announcements") != -1:
					features[phone_num]['a'] += 1
				elif feature_chosen and line.find("radio") != -1:
					features[phone_num]['r'] += 1
				elif feature_chosen and line.find("experiences") != -1:
					features[phone_num]['e'] += 1
				
				feature_chosen = 0
							
		except ValueError as err:
			#print("ValueError: " + str(err.args))
			continue
		except IndexError:
			continue
		except otalo.PhoneNumException:
			continue
	
	print("Number of calls by phone number, by feature:")
	print("\t\tq&a\tannouncements\tradio\texperiences")
	features = sorted(features.iteritems(), key=lambda(k,v): (v,k))
	features.reverse()
	for num, tots in features:
		print(num +": \t"+str(tots['q']) + "\t" + str(tots['a']) + "\t\t" + str(tots['r']) + "\t" + str(tots['e']) )

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
	
def main():
	if not len(sys.argv) > 1:
		print("Wrong")
	else:
		f = sys.argv[1]
		line = False
		if len(sys.argv) == 3:
			lineid = sys.argv[2]
			line = Line.objects.get(pk=lineid)
			print('num is ' + line.number)
		if len(sys.argv) == 4:
			demographics_file = sys.argv[3]
		
		#get_calls_by_number(f,line.number)
		#get_guj_nums_only(f, legacy_log=True)
		#get_calls_by_feature(f)
		#get_calls_by_geography(f, demographics_file)
		#get_messages_by_number(['9586550654'])
		get_numbers_by_date(f, line.number)
			
#main()
