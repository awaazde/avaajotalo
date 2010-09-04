import otalo_utils
import sys
from datetime import datetime
from otalo.AO.models import Line

def get_calls(filename, destnum=False, log="Start call", phone_num_filter=0, date_filter=0, quiet=False, legacy_log=False):
	calls = {}
	current_week_start = 0
	total = 0
	
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
			#print(phone_num + ': dest = ' + dest)
			
			if phone_num_filter and not phone_num in phone_num_filter:
				continue
			
			if date_filter and (current_date.year != date_filter.year or current_date.month != date_filter.month or current_date.day != date_filter.day):
				#print("filtering out " + otalo_utils.date_str(current_date))
				continue
			
			if destnum and destnum.find(dest) == -1:
				continue
				
			if not current_week_start:
				current_week_start = current_date

			delta = current_date - current_week_start

			if delta.days > 6:
				current_week_start = current_date

			if line.lower().find(log.lower()) != -1:
				if current_week_start in calls:
					calls[current_week_start] += 1
				else:
					calls[current_week_start] = 1
					
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

		print("Number of "+ log + "'s, by week:")
		dates = calls.keys()
		dates.sort()
		for date in dates:
			total += calls[date]
			print(date.strftime('%Y-%m-%d') +": "+str(calls[date]))

		print("total is " + str(total))
	
	return calls
		
# only counts when a call is verified as open 
# (i.e. in between an explicit call-started and hang-up)
def get_calls_by_feature(filename, destnum, phone_num_filter=0, legacy_log=False):
	features = {}
	current_week_start = 0
	feature_chosen = 0
	open_calls = []
	
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
			
			if not current_week_start:
				current_week_start = current_date

			if not legacy_log and destnum and destnum.find(dest) == -1:
				continue

			delta = current_date - current_week_start

			if delta.days > 6:
				#flush all open calls
				open_calls = []
				
				current_week_start = current_date
			
			if not current_week_start in features:
				features[current_week_start] = {'q':0, 'a':0, 'r':0, 'e':0} 
			
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
					features[current_week_start]['q'] += 1
				elif feature_chosen and line.find("announcements") != -1:
					features[current_week_start]['a'] += 1
				elif feature_chosen and line.find("radio") != -1:
					features[current_week_start]['r'] += 1
				elif feature_chosen and line.find("experiences") != -1:
					features[current_week_start]['e'] += 1
				elif feature_chosen and line.find("dg") != -1:
					features[current_week_start]['r'] += 1
				
				feature_chosen = 0
			
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
	
	if phone_num_filter:
		print("Data for phone numbers: " + str(phone_num_filter))
		
	print("Number of calls by feature, by week:")
	print("\t\tq&a\tannouncements\tradio\texperiences")
	dates = features.keys()
	dates.sort()
	for date in dates:
		print(otalo_utils.date_str(date) +": \t"+str(features[date]['q']) + "\t" + str(features[date]['a']) + "\t\t" + str(features[date]['r']) + "\t" + str(features[date]['e']) + "\t")

def get_features_within_call(filename, destnum, date_filter=0, phone_num_filter=0, quiet=False):
	features = {}
	current_week_start = 0
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
			current_date = otalo_utils.get_date(line)		
			dest = otalo_utils.get_destination(line)			
		##
		################################################
			
			if phone_num_filter and not phone_num in phone_num_filter:
				continue
				
			if date_filter and (current_date.year != date_filter.year or current_date.month != date_filter.month or current_date.day != date_filter.day):
				continue
			
			if destnum.find(dest) == -1:
				continue
			
			if not current_week_start:
				current_week_start = current_date

			delta = current_date - current_week_start

			if delta.days > 6:
				#flush all open calls
				open_calls = {}
				
				current_week_start = current_date
			
			if not current_week_start in features:
				features[current_week_start] = []
	
			if line.find("Start call") != -1:
				# check to see if this caller already has one open
				if phone_num in open_calls:
					# close out current call
					call = open_calls[phone_num]
					features[current_week_start].append(call)
					del open_calls[phone_num]
					
				# add new call
				#print("adding new call: " + phone_num)
				open_calls[phone_num] = {'q':0, 'a':0, 'r':0, 'e':0, 'order':''} 
					
			elif line.find("End call") != -1:
				if phone_num in open_calls:
					# close out call				
					call = open_calls[phone_num]
					features[current_week_start].append(call)
					del open_calls[phone_num]
			elif phone_num in open_calls:
				call = open_calls[phone_num]
				if line.find("okyouwant_pre") != -1:
					# on the next go-around, look for the feature
					feature_chosen = 1
					continue
				if feature_chosen and line.find("qna") != -1:
					call['q'] += 1
					call['order'] += 'q'
				elif feature_chosen and line.find("announcements") != -1:
					call['a'] += 1
					call['order'] += 'a'
				elif feature_chosen and line.find("radio") != -1:
					call['r'] += 1
					call['order'] += 'r'
				elif feature_chosen and line.find("experiences") != -1:
					call['e'] += 1
					call['order'] += 'e'
				elif feature_chosen and line.find("dg") != -1:
					call['r'] += 1
					call['order'] += 'r'
				
				feature_chosen = 0
			
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
	
	if phone_num_filter:
		print("Data for phone numbers: " + str(phone_num_filter))
	
	if not quiet:
		print("Histogram of number of features accessed within call, by week:")
		dates = features.keys()
		dates.sort()
		for date in dates:
			features_hist = {}
			for call in features[date]:
				features_tot = call['q'] + call['a'] + call['r'] + call['e']
				if features_tot in features_hist:
					features_hist[features_tot] += 1 
				else: 
					features_hist[features_tot] = 1
			
			sorted_items = features_hist.items()
			sorted_items.sort()
			#features_hist = [[k,v] for k,v in sorted_items]
			
			print(date.strftime('%Y-%m-%d') + ": " + str(sorted_items))
			
		print("Average features accessed within call, by week:")
		for date in dates:
			total_features = 0
			num_calls = len(features[date])
			for call in features[date]:
				total_features += call['q'] + call['a'] + call['r'] + call['e']
	
			print(date.strftime('%Y-%m-%d') + ": " + str(float(total_features)/float(num_calls)))	
			
	return features
#ignoring announcements, since its typically all or nothing
def get_listens_within_call(filename, phone_num_filter=0):
	listens = {}
	current_week_start = 0
	feature_chosen = 0
	feature = 0
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
		##
		################################################
			
			if phone_num_filter and not phone_num in phone_num_filter:
				continue
			
			if not current_week_start:
				current_week_start = current_date

			delta = current_date - current_week_start

			if delta.days > 6:
				#flush all open calls
				open_calls = {}
				
				current_week_start = current_date
			
			if not current_week_start in listens:
				listens[current_week_start] = {'q':[], 'q-longest':0, 'r':[], 'r-longest':0, 'a':[], 'a-longest':0, 'e':[], 'e-longest':0}
	
			if line.find("Start call") != -1:
				# check to see if this caller already has one open
				if phone_num in open_calls:
					# close out current call
					call = open_calls[phone_num]
					if call['qcount'] > 0:
						count = call['qcount']
						listens[current_week_start]['q'].append(count)
						listens[current_week_start]['q-longest'] = max(listens[current_week_start]['q-longest'], count)
					elif call['rcount'] > 0:
						count = call['rcount']
						listens[current_week_start]['r'].append(count)
						listens[current_week_start]['r-longest'] = max(listens[current_week_start]['r-longest'], count)
					elif call['acount'] > 0:
						count = call['acount']
						listens[current_week_start]['a'].append(count)
						listens[current_week_start]['a-longest'] = max(listens[current_week_start]['a-longest'], count)
					elif call['ecount'] > 0:
						count = call['ecount']
						listens[current_week_start]['e'].append(count)
						listens[current_week_start]['e-longest'] = max(listens[current_week_start]['e-longest'], count)
					
					del open_calls[phone_num]
					
				# add new call
				#print("adding new call: " + phone_num)
				open_calls[phone_num] = {'qcount':0, 'rcount':0, 'acount':0, 'ecount':0} 
					
			elif line.find("End call") != -1:
				if phone_num in open_calls:
					# close out call				
					call = open_calls[phone_num]
					if call['qcount'] > 0:
						count = call['qcount']
						listens[current_week_start]['q'].append(count)
						listens[current_week_start]['q-longest'] = max(listens[current_week_start]['q-longest'], count)
					elif call['rcount'] > 0:
						count = call['rcount']
						listens[current_week_start]['r'].append(count)
						listens[current_week_start]['r-longest'] = max(listens[current_week_start]['r-longest'], count)
					elif call['acount'] > 0:
						count = call['acount']
						listens[current_week_start]['a'].append(count)
						listens[current_week_start]['a-longest'] = max(listens[current_week_start]['a-longest'], count)
					elif call['ecount'] > 0:
						count = call['ecount']
						listens[current_week_start]['e'].append(count)
						listens[current_week_start]['e-longest'] = max(listens[current_week_start]['e-longest'], count)
										
					del open_calls[phone_num]
			elif phone_num in open_calls:
				call = open_calls[phone_num]
				if line.find("okyouwant_pre") != -1:
					# on the next go-around, look for the feature
					feature_chosen = 1
					continue
				if feature_chosen and line.find("qna") != -1:
					feature = 'q'
				elif feature_chosen and line.find("announcements") != -1:
					feature = 'a'
				elif feature_chosen and line.find("radio") != -1:
					feature = 'r'
				elif feature_chosen and line.find("experiences") != -1:
					feature = 'e'
					
				feature_chosen = 0
				if line.find("Stream") != -1:
					call[feature+'count'] += 1
			
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
	
	if phone_num_filter:
		print("Data for phone numbers: " + str(phone_num_filter))
		
	print("Average number of content listens within call, by week:")
	dates = listens.keys()
	dates.sort()
	for date in dates:
		totals = listens[date]
		avg_q = float(sum(totals['q'])) / float(len(totals['q']))
		avg_a = float(sum(totals['a'])) / float(len(totals['a']))
		avg_r = float(sum(totals['r'])) / float(len(totals['r']))
		avg_e = 0 if len(totals['e']) == 0 else float(sum(totals['e'])) / float(len(totals['e']))
		
		print(date.strftime('%Y-%m-%d') + ": Questions - " + str(avg_q) + "; longest = " + str(totals['q-longest']) + "\tAnnouncements - " + str(avg_a) + "; longest = " + str(totals['a-longest']) + "\tRadio - " + str(avg_r) + "; longest = " + str(totals['r-longest']) + "\tExperiences - " + str(avg_e) + "; longest = " + str(totals['e-longest']) )
		
def get_log_as_percent(filename, log, phone_num_filter=0):
	calls = {}
	current_week_start = 0
	current_week_calls = 0
	total = 0
	
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
		##
		################################################
		
			if phone_num_filter and not phone_num in phone_num_filter:
				continue
			
			if not current_week_start:
				current_week_calls = 0
				current_week_start = current_date

			delta = current_date - current_week_start

			if delta.days > 6:
				call_tot = calls[current_week_start]
				calls[current_week_start] =  float(call_tot) / float(current_week_calls)
				current_week_calls = 0
				current_week_start = current_date

			if line.find("Start call") != -1:
				current_week_calls += 1
				
			if line.find(log) != -1:
				if current_week_start in calls:
					calls[current_week_start] += 1
				else:
					calls[current_week_start] = 1
					
		except ValueError as err:
			#print("ValueError: " + line)
			continue
		except IndexError as err:
			continue
		except otalo_utils.PhoneNumException:
			#print("PhoneNumException: " + line)
			continue
	
	if phone_num_filter:
		print("Data for phone numbers: " + str(phone_num_filter))
		
	print("Percent of "+ log + "'s as a percentage of total calls, by week:")
	dates = calls.keys()
	dates.sort()
	for date in dates:
		print(date.strftime('%Y-%m-%d') +": "+str(calls[date]))
		
	
	
def main():
	if not len(sys.argv) > 1:
		print("Wrong")
	else:
		f = sys.argv[1]
		line = False
		if len(sys.argv) == 3:
			lineid = sys.argv[2]
			line = Line.objects.get(pk=lineid)
		
		#get_calls(f, legacy_log=True)
		get_calls_by_feature(f, line.number, legacy_log=True)
		#get_features_within_call(f)
		#get_listens_within_call(f)
		#get_log_as_percent(f, "instructions_full")
		#get_calls(f, "okrecorded")
		#get_listens_within_call(f)
		#get_log_as_percent(f, log="match")
		#get_num_questions(f)
			
main()
