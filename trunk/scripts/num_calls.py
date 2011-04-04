import otalo_utils
import sys
from datetime import datetime,timedelta
from otalo.AO.models import Message, Line
from django.db.models import Max

def get_calls(filename, destnum=False, log="Start call", phone_num_filter=False, date_start=False, date_end=False, quiet=False, legacy_log=False, transfer_calls=False):
	calls = {}
	nums = []
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
				current_week_start = current_date

			delta = current_date - current_week_start

			if delta.days > 6:
				current_week_start = current_date
			
			if phone_num not in nums:
				nums.append(phone_num)

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
			print(otalo_utils.date_str(date) +": "+str(calls[date]))

		print("total is " + str(total))
		print ("number of unique callers is " + str(len(nums)))
	
	return calls
		
# only counts when a call is verified as open 
# (i.e. in between an explicit call-started and hang-up)
def get_calls_by_feature(filename, destnum, phone_num_filter=0, date_start=False, date_end=False, quiet=False, legacy_log=False):
	features = {}
	feature_names = []
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
			
			if not current_week_start:
				current_week_start = current_date

			if not legacy_log and destnum and destnum.find(dest) == -1:
				continue

			delta = current_date - current_week_start

			if delta.days > 6:
				#flush all open calls
				open_calls = {}
				
				current_week_start = current_date
			
			if not current_week_start in features:
				features[current_week_start] = {'q':0, 'a':0, 'r':0, 'e':0} 
				features[current_week_start] = {}
				
			if line.find("Start call") != -1:
				# check to see if this caller already has one open
				if phone_num in open_calls:
					# close out current call					
					del open_calls[phone_num]
					
				# add new call with no feature access yet
				open_calls[phone_num] = 0
					
			elif line.find("End call") != -1:
				if phone_num in open_calls:
					# close out call				
					del open_calls[phone_num]
			elif phone_num in open_calls:
				if line.find("okyouwant_pre") != -1:
					# on the next go-around, look for the feature
					open_calls[phone_num] = 1
				elif open_calls[phone_num]:
					feature = line[line.rfind('/')+1:line.find('.wav')]
					#if feature not in ['announcements', 'qna', 'radio', 'experiences']:
						#print(line)
					if feature not in feature_names:
						feature_names.append(feature)
					if feature in features[current_week_start]:
						features[current_week_start][feature] += 1
					else:
						features[current_week_start][feature] = 1
				
					open_calls[phone_num] = 0
			
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
			
		print("Number of calls by feature, by week:")
		header = "\t"
		for name in feature_names:
			header += name+"\t"
		print(header)
		dates = features.keys()
		dates.sort()
		for date in dates:
			row = otalo_utils.date_str(date) +"\t"
			for name in feature_names:
				if name in features[date]:
					row += str(features[date][name]) + "\t"
				else:
					row += "0\t"
			print(row)

def get_features_within_call(filename, destnum, phone_num_filter=False, date_start=False, date_end=False, quiet=False, transfer_calls=False):
	features = {}
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
				open_calls[phone_num] = {'order':'','feature_chosen':False}
				
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
					call['feature_chosen'] = True
				elif call['feature_chosen']:
					feature = line[line.rfind('/')+1:line.find('.wav')]
					if feature in call:
						call[feature] += 1
					else:
						call[feature] = 1
					call['order'] += feature+','
					
					open_calls[phone_num]['feature_chosen'] = False
			
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
		
		print("Histogram of number of features accessed within call:")
		dates = features.keys()
		dates.sort()
		features_hist = {}
		for date in dates:
			for call in features[date]:
				features_tot = 0
				for feature in call:
					if feature != 'feature_chosen' and feature != 'order':
						features_tot += call[feature]
				if features_tot in features_hist:
					features_hist[features_tot] += 1 
				else: 
					features_hist[features_tot] = 1
			
		sorted_items = features_hist.items()
		sorted_items.sort()
		for num, tot in sorted_items:
			print(str(num)+"\t"+str(tot))
			
		print("Average features accessed within call, by week:")
		for date in dates:
			total_features = 0
			num_calls = len(features[date])
			for call in features[date]:
				for feature in call:
					if feature != 'feature_chosen' and feature != 'order':
						total_features += call[feature]
	
			print(date.strftime('%Y-%m-%d') + ": " + str(float(total_features)/float(num_calls)))	
			
	return features

def get_listens_within_call(filename, destnum, phone_num_filter=False, date_start=False, date_end=False, quiet=False, transfer_calls=False):
	listens = {}
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
			
			if not current_week_start:
				current_week_start = current_date

			delta = current_date - current_week_start

			if delta.days > 6:
				#flush all open calls
				open_calls = {}
				
				current_week_start = current_date
			
			if not current_week_start in listens:
				listens[current_week_start] = []
	
			if line.find("Start call") != -1:
				# check to see if this caller already has one open
				if phone_num in open_calls:
					# close out current call
					tot = open_calls[phone_num]
					listens[current_week_start].append(tot)
					del open_calls[phone_num]
				open_calls[phone_num] = 0
				
			elif line.find("End call") != -1:
				if phone_num in open_calls:
					# close out call				
					tot = open_calls[phone_num]
					listens[current_week_start].append(tot)
					del open_calls[phone_num]
			elif line.find("Stream") != -1:
				if phone_num in open_calls:
					open_calls[phone_num] += 1
				
			
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
		
		print("Histogram of number of listens within call")
		dates = listens.keys()
		dates.sort()
		listens_hist = {}
		for date in dates:
			for tot in listens[date]:
				if tot in listens_hist:
					listens_hist[tot] += 1 
				else: 
					listens_hist[tot] = 1
			
		sorted_items = listens_hist.items()
		sorted_items.sort()
		for num, tot in sorted_items:
			print(str(num)+"\t"+str(tot))
			
			
		print("Average listens within call, by week:")
		for date in dates:
			total_listens = 0
			num_calls = len(listens[date])
			for tot in listens[date]:
				total_listens += tot
				
			if total_listens == 0:
				avg = 0
			else:
				avg = float(total_listens)/float(num_calls)
				
			print(date.strftime('%Y-%m-%d') + ": " + str(avg))	
			
	return listens
		
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
		
def get_num_qna(line, responder_ids=[], quiet=False):
	qna = {}
	start_date = datetime(year=2010,month=7,day=1)
	oneweek = timedelta(days=7)
	end_date = Message.objects.filter(message_forum__forum__line=line).aggregate(Max('date'))
	end_date = end_date[end_date.keys()[0]]
	
	while(start_date < end_date):   
		qcount = Message.objects.filter(message_forum__status=1,message_forum__forum__line=line, date__gte=start_date, date__lt=start_date+oneweek, lft=1).count()
		acount = Message.objects.filter(message_forum__status=1, message_forum__forum__line=line, date__gte=start_date, date__lt=start_date+oneweek, lft__gt=1).count()
		if responder_ids:
			rcount = Message.objects.filter(message_forum__status=1,message_forum__forum__line=line, date__gte=start_date, date__lt=start_date+oneweek, lft__gt=1).exclude(user__in=responder_ids).count()
			qna[start_date] = [qcount, acount, rcount]
		else:
			qna[start_date] = [qcount, acount]
		
		start_date += oneweek
	
	if not quiet:	
		print("Number of questions and responses, by week:")
		if responder_ids:
			print("\t\tquestions\ttotal responses\tresponders only")
		else:
			print("\t\tquestions\tresponses")
		dates = qna.keys()
		dates.sort()
		for date in dates:
			if responder_ids:
				print(otalo_utils.date_str(date) +" \t"+str(qna[date][0]) + "\t\t" + str(qna[date][1]) + "\t\t" + str(qna[date][2]))
			else:
				print(otalo_utils.date_str(date) +" \t"+str(qna[date][0]) + "\t\t" + str(qna[date][1]))
	
	return qna

def main():
	if not len(sys.argv) > 1:
		print("Wrong")
	else:
		f = sys.argv[1]
		line = False
		if len(sys.argv) == 3:
			lineid = sys.argv[2]
			line = Line.objects.get(pk=lineid)
			
		get_calls(f, line.number)
		#get_calls_by_feature(f, line.number, legacy_log=True)
		#get_features_within_call(f)
		#get_listens_within_call(f)
		#get_log_as_percent(f, "instructions_full")
		#get_calls(f, "okrecorded")
		#get_listens_within_call(f)
		#get_log_as_percent(f, log="match")
		#get_num_questions(f)
		#responder_ids = [2,3,4,5,6,48,54,125,126]
		#get_num_qna(line, responder_ids)
			
#main()
