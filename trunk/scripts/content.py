import otalo
import sys
from datetime import datetime
from datetime import timedelta
	
def get_categories(filename):
	crops = {}
	topics = {}
	
	f = open(filename)
	
	while(True):
		line = f.readline()
		if not line:
			break
		
		try:		
			date = otalo.get_content_date(line)
			length = otalo.get_content_length(line)
			content_type = otalo.get_content_type(line)
			name = otalo.get_content_name(line)
			village = otalo.get_content_village(line)
			transcript = otalo.get_content_transcript(line)
			crop = otalo.get_content_crop(line)
			topic = otalo.get_content_topic(line)
			
			#print("date: " + otalo.date_str(date) + " length (s): " + str(length) + " type: " + content_type + "  name: " + name + " village: " + village + " crop: " + crop + " topic: " + topic)

			if content_type.lower().find('question') == -1:
				continue
			crops[crop] = crops[crop]+1 if crop in crops.keys() else 1
			topics[topic] = topics[topic]+1 if topic in topics.keys() else 1
			
		except ValueError as err:
			#print("ValueError: " + str(err.args))
			continue
	
	crops = sorted(crops.iteritems(), key=lambda(k,v): (v,k))
	crops.reverse()
	print("Categorized by crop:")
	for crop, num in crops:
		if crop == '':
			crop = 'NONE SPECIFIED'
		print(crop + ": " + str(num))
		
	topics = sorted(topics.iteritems(), key=lambda(k,v): (v,k))
	topics.reverse()
	print('\n')
	print("Categorized by topic:")
	for topic, num in topics:
		if topic == '':
			topic = 'NONE SPECIFIED'
		print(topic + ": " + str(num))

def keywords_histogram(filename, blacklist):
	f = open(filename)
	keywords = {}
	
###############################################
## Any function doing analysis on content text
## must call this loading function first
	
	otalo.load_content_blacklist(blacklist)
##
###############################################
		
	while(True):
		line = f.readline()
		if not line:
			break
			
		transcript = otalo.get_content_transcript(line)
		if transcript == '':
			continue

		tokens = transcript.split()
		for tok in tokens:
			tok = tok.lower()
			tok = tok.strip('&.?:-"/\\%')
			if tok == '':
				continue
			if otalo.is_keyword(tok):
				keywords[tok] = keywords[tok]+1 if tok in keywords.keys() else 1
	
	keywords = sorted(keywords.iteritems(), key=lambda(k,v): (v,k))
	#keywords.reverse()
	
	print("Keyword counts")
	for kw, count in keywords:
		print(kw + ": " + str(count))

def get_content_type_by_time(filename, log="Question", phone_num_filter=0, quiet=False):
	calls = {}
	current_week_start = 0
	total = 0
	
	f = open(filename)
	
	start = datetime.strptime("2008-12-24", "%Y-%m-%d")
	delta = timedelta(7)
	end = datetime.strptime("2009-07-15", "%Y-%m-%d")
	while start <= end:
		calls[start] = 0
		start += delta
	
	while(True):
		line = f.readline()
		if not line:
			break
		try:
		
		#################################################
		## Use the calls here to determine what pieces
		## of data must exist for the line to be valid.
		## All of those below should probably always be.
			
			current_date = otalo.get_content_date(line)
			content_type = otalo.get_content_type(line)
		##
		################################################
		
			if phone_num_filter and not phone_num in phone_num_filter:
				continue
			
			current_week_start = max([d for d in calls.keys() if current_date >= d])
			
			if content_type.lower().find(log.lower()) != -1:
				if current_week_start in calls:
					calls[current_week_start] += 1
				else:
					calls[current_week_start] = 1
					
		except ValueError as err:
			#print("ValueError: " + line)
			continue
		except otalo.PhoneNumException:
			#print("PhoneNumException: " + line)
			continue
	
	if not quiet:
		if phone_num_filter:
			print("Data for phone numbers: " + str(phone_num_filter))

		print("Number of "+ log + "'s, by week:")
		dates = calls.keys()
		dates.sort()
		for date in dates:
			total += calls[date]
			if calls[date] > 0:
				print(date.strftime('%Y-%m-%d') +": "+str(calls[date]))

		print("total is " + str(total))
	
	return calls
	

def get_dates(filename):
	f = open(filename)
	
	while(True):
		line = f.readline()
		if not line:
			break
		try:
			
			print(otalo.date_str(otalo.get_content_date(line)))
		
		except ValueError as err:
			print("ValueError: " + line)
			continue
			
def get_qa(filename):
	f = open(filename)
	
	while(True):
		line = f.readline()
		if not line:
			break
		try:
			
			content_type = otalo.get_content_type(line)
			q = 'question'
			a = 'answer'
			m = 'moderation'
			if content_type.lower().find(q) != -1 or content_type.lower().find(a) != -1 or content_type.lower().find(m) != -1:
				print(line.strip())
		
		except ValueError as err:
			print("ValueError: " + line)
			continue
			
def get_identified_qs_by_time(filename, log="Question", phone_num_filter=0, quiet=False):
	calls = {}
	current_week_start = 0
	total = 0
	
	f = open(filename)
	
	start = datetime.strptime("2009-01-01", "%Y-%m-%d")
	delta = timedelta(7)
	end = datetime.strptime("2009-07-15", "%Y-%m-%d")
	while start <= end:
		calls[start] = 0
		start += delta
	
	while(True):
		line = f.readline()
		if not line:
			break
		try:
		
		#################################################
		## Use the calls here to determine what pieces
		## of data must exist for the line to be valid.
		## All of those below should probably always be.
			
			current_date = otalo.get_content_date(line)
			content_type = otalo.get_content_type(line)
			content_name = otalo.get_content_name(line)
		##
		################################################
		
			if phone_num_filter and not phone_num in phone_num_filter:
				continue
			
			current_week_start = max([d for d in calls.keys() if current_date >= d])
			
			if content_type.lower().find(log.lower()) != -1 and content_name != '':
				if current_week_start in calls:
					calls[current_week_start] += 1
				else:
					calls[current_week_start] = 1
					
		except ValueError as err:
			#print("ValueError: " + line)
			continue
		except otalo.PhoneNumException:
			#print("PhoneNumException: " + line)
			continue
	
	if not quiet:
		if phone_num_filter:
			print("Data for phone numbers: " + str(phone_num_filter))

		print('\nNumber of questions with name')
		dates = calls.keys()
		dates.sort()
		for date in dates:
			total += calls[date]
			if calls[date] > 0:
				print(date.strftime('%Y-%m-%d') +": "+str(calls[date]))

		print("total is " + str(total))
	
	return calls
	

def get_type_by_number(filename, log="Question", quiet=False):
	calls = {}
	
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

			content_type = otalo.get_content_type(line)
			phone_num = otalo.get_content_number(line)
		##
		################################################

			if content_type.lower().find(log) != -1:
				if phone_num in calls.keys():
					calls[phone_num] += 1
				else:
					calls[phone_num] = 1

		except ValueError as err:
			#print("ValueError: " + str(err.args))
			continue
		except otalo.PhoneNumException:
			continue

	if not quiet:
		print("Number of " + log + "'s by phone number:")
		calls_sorted = sorted(calls.iteritems(), key=lambda(k,v): (v,k))
		calls_sorted.reverse()
		total = 0
		for num, tot in calls_sorted:
			total += tot
			print(num +": "+str(tot))
			
		print('total is ' + str(total));	
	return calls
	
def main():
	if not len(sys.argv) > 1:
			print("Wrong")
	else:
		f = sys.argv[1]
		if len(sys.argv) == 3:
			content_blacklist_file = sys.argv[2]
		
		#get_categories(f)
		#keywords_histogram(f, content_blacklist_file)
		#get_content_type_by_time(f, log="Question")
		#get_dates(f)
		#get_qa(f)
		#get_identified_qs_by_time(f)
			
#main()
