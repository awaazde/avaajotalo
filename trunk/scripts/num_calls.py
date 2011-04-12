import otalo_utils
import sys
from datetime import datetime,timedelta
from otalo.AO.models import User, Message_forum, Forum, Line
from django.db.models import Min,Max

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
				current_week_start = datetime(year=current_date.year, month=current_date.month, day=current_date.day)

			delta = current_date - current_week_start

			if delta.days > 6:
				current_week_start = datetime(year=current_date.year, month=current_date.month, day=current_date.day)
			
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
				current_week_start = datetime(year=current_date.year, month=current_date.month, day=current_date.day)

			if not legacy_log and destnum and destnum.find(dest) == -1:
				continue

			delta = current_date - current_week_start

			if delta.days > 6:
				#flush all open calls
				open_calls = {}
				
				current_week_start = datetime(year=current_date.year, month=current_date.month, day=current_date.day)
			
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
				current_week_start = datetime(year=current_date.year, month=current_date.month, day=current_date.day)

			delta = current_date - current_week_start

			if delta.days > 6:
				#flush all open calls
				open_calls = {}
				
				current_week_start = datetime(year=current_date.year, month=current_date.month, day=current_date.day)
			
			if not current_week_start in features:
				features[current_week_start] = []
	
			if line.find("Start call") != -1:
				# check to see if this caller already has one open
				if phone_num in open_calls:
					# close out current call
					call = open_calls[phone_num]
					features[current_week_start].append(call)
					dur = call['last'] - call['start']
					n_features = 0
					for feature in call:
						if feature != 'order' and feature != 'feature_chosen' and feature != 'start' and feature != 'last':
							n_features += call[feature]
					if n_features in durations:
						durations[n_features].append(dur)
					else:
						durations[n_features] = [dur]
					del open_calls[phone_num]
					
				# add new call
				#print("adding new call: " + phone_num)
				open_calls[phone_num] = {'order':'','feature_chosen':False,'start':current_date,'last':current_date}
				
			elif line.find("End call") != -1:
				if phone_num in open_calls:
					# close out call				
					call = open_calls[phone_num]
					features[current_week_start].append(call)
					dur = current_date - call['start']
					n_features = 0
					for feature in call:
						if feature != 'order' and feature != 'feature_chosen' and feature != 'start' and feature != 'last':
							n_features += call[feature]
					if n_features in durations:
						durations[n_features].append(dur)
					else:
						durations[n_features] = [dur]
					del open_calls[phone_num]
			elif phone_num in open_calls:
				call = open_calls[phone_num]
				if line.find("okyouwant_pre") != -1 or line.find("okyourreplies") != -1:
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
		print("Features\tCalls\tAvg Duration")
		dates = features.keys()
		dates.sort()
		features_hist = {}
		for date in dates:
			for call in features[date]:
				features_tot = 0
				for feature in call:
					if feature != 'feature_chosen' and feature != 'order' and feature != 'start' and feature != 'last':
						features_tot += call[feature]
				if features_tot in features_hist:
					features_hist[features_tot] += 1 
				else: 
					features_hist[features_tot] = 1
			
		sorted_items = features_hist.items()
		sorted_items.sort()
		for num, tot in sorted_items:
			durs_by_call = durations[num]
			durs = [dur.seconds for dur in durs_by_call] 
			print(str(num)+"\t"+str(tot)+"\t"+str(sum(durs)/len(durs)))	
			
		print("Average features accessed within call, by week:")
		for date in dates:
			total_features = 0
			num_calls = len(features[date])
			for call in features[date]:
				for feature in call:
					if feature != 'feature_chosen' and feature != 'order' and feature != 'start' and feature != 'last':
						total_features += call[feature]
	
			print(date.strftime('%Y-%m-%d') + ": " + str(float(total_features)/float(num_calls)))	
			
	return features

def get_listens_within_call(filename, destnum, phone_num_filter=False, date_start=False, date_end=False, quiet=False, transfer_calls=False):
	listens = {}
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
				current_week_start = datetime(year=current_date.year, month=current_date.month, day=current_date.day)

			delta = current_date - current_week_start

			if delta.days > 6:
				#flush all open calls
				open_calls = {}
				
				current_week_start = datetime(year=current_date.year, month=current_date.month, day=current_date.day)
			
			if not current_week_start in listens:
				listens[current_week_start] = []
	
			if line.find("Start call") != -1:
				# check to see if this caller already has one open
				if phone_num in open_calls:
					# close out current call
					call = open_calls[phone_num]
					n_listens = call['listens']
					listens[current_week_start].append(n_listens)
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
					listens[current_week_start].append(n_listens)
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
		
		print("Histogram of number of listens within call")
		print("Listens\tCalls\tAvg Duration")
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
			durs_by_call = durations[num]
			durs = [dur.seconds for dur in durs_by_call] 
			print(str(num)+"\t"+str(tot)+"\t"+str(sum(durs)/len(durs)))		
			
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
				current_week_start = datetime(year=current_date.year, month=current_date.month, day=current_date.day)

			delta = current_date - current_week_start

			if delta.days > 6:
				call_tot = calls[current_week_start]
				calls[current_week_start] =  float(call_tot) / float(current_week_calls)
				current_week_calls = 0
				current_week_start = datetime(year=current_date.year, month=current_date.month, day=current_date.day)

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
		
def get_num_qna(line, forum=False, date_start=False, date_end=False, quiet=False):
	qna = {}
	oneweek = timedelta(days=7)
	
	if not date_start:
		if forum:
			date_start = Message_forum.objects.filter(forum=forum).aggregate(Min('message__date'))
		else:
			date_start = Message_forum.objects.filter(forum__line=line).aggregate(Min('message__date'))
		date_start = date_start[date_start.keys()[0]]
	if not date_end:
		if forum:
			date_end = Message_forum.objects.filter(forum=forum).aggregate(Max('message__date'))
		else:		
			date_end = Message_forum.objects.filter(forum__line=line).aggregate(Max('message__date'))
		date_end = date_end[date_end.keys()[0]]
	
	while(date_start < date_end):
		if forum:
			this_weeks_msgs = Message_forum.objects.filter(forum=forum, message__date__gte=date_start, message__date__lt=date_start+oneweek)
		else:
			this_weeks_msgs = Message_forum.objects.filter(forum__line=line, message__date__gte=date_start, message__date__lt=date_start+oneweek)
		questions = this_weeks_msgs.filter(message__lft=1)
		n_questions = questions.count()
		n_qs_unique = questions.values('message__user').distinct().count()
		n_qs_approved = questions.filter(status=Message_forum.STATUS_APPROVED).count()
		
		responses = this_weeks_msgs.filter(message__lft__gt=1)
		n_responses = responses.count()
		n_rs_unique = responses.values('message__user').distinct().count()
		n_rs_approved = responses.filter(status=Message_forum.STATUS_APPROVED).count()
		
		responders = User.objects.filter(forum__line=line).distinct()
		responder_responses = responses.filter(message__user__in=responders)
		n_responders = responder_responses.count()
		n_responders_unique = responder_responses.values('message__user').distinct().count()
		n_responders_approved = responder_responses.filter(status=Message_forum.STATUS_APPROVED).count()
		responder_rate=0
		if n_responses>0:
			responder_rate = float(n_responders)/float(n_responses)
		
		qna[date_start] = [n_questions, n_qs_approved, n_qs_unique, n_responses, n_rs_approved, n_rs_unique, n_responders,n_responders_approved,n_responders_unique,responder_rate]
		
		date_start += oneweek
	
	if not quiet:	
		print("Number of questions and responses, by week:")
		print("Date\ttot messages\ttot approved\tunique posters\ttotal responses\tapproved\tunique\tresponder msgs\tapproved\tunique\trate")
		
		dates = qna.keys()
		dates.sort()
		for date in dates:
			row = otalo_utils.date_str(date) +"\t"
			stats = qna[date]
			for stat in stats:
				row += str(stat) + "\t"
			print(row)
	return qna

def get_lurking_and_posting(filename, destnum, forums, phone_num_filter=False, date_start=False, date_end=False, quiet=False, transfer_calls=False):
	listens = {}
	durations = {}
	current_week_start = 0
	open_calls = {}
	
	f = open(filename)
	
	forum_names = forums.values('name_file')
	forum_names = [pair.values()[0] for pair in forum_names]
	
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
				current_week_start = datetime(year=current_date.year, month=current_date.month, day=current_date.day)

			delta = current_date - current_week_start

			if delta.days > 6:
				#flush all open calls
				open_calls = {}
				
				current_week_start = datetime(year=current_date.year, month=current_date.month, day=current_date.day)
			
			if not current_week_start in listens:
				listens[current_week_start] = {'lurks':0,'posts':0,'listens':[]}
	
			if line.find("Start call") != -1:
				# check to see if this caller already has one open
				if phone_num in open_calls:
					# close out current call
					call = open_calls[phone_num]
					listens[current_week_start]['lurks'] += call['lurks']
					listens[current_week_start]['posts'] += call['posts']
					listens[current_week_start]['listens'].append(call['listens'])
					del open_calls[phone_num]
				open_calls[phone_num] = {'lurks':0, 'posts':0, 'listens':0, 'forum':False }
				
			elif line.find("End call") != -1:
				if phone_num in open_calls:
					# close out call				
					call = open_calls[phone_num]
					listens[current_week_start]['lurks'] += call['lurks']
					listens[current_week_start]['posts'] += call['posts']
					listens[current_week_start]['listens'].append(call['listens'])
					del open_calls[phone_num]
			elif phone_num in open_calls:
				call = open_calls[phone_num]
				for name in forum_names:
					if line.find(name) != -1:
						call['forum'] = True
				# for record need the . to seperate from okrecorded and okrecordresponse
				if call['forum'] and otalo_utils.is_prompt(line) and line.find("okrecord.") != -1:
					call['posts'] += 1
					call['forum'] = False
				elif call['forum'] and otalo_utils.is_prompt(line) and line.find("okplay") != -1:
					call['lurks'] += 1
					call['forum'] = False
				elif line.find("Stream") != -1:
					filename = line[line.rfind('/')+1:]
					if bool(Message_forum.objects.filter(forum__in=forumids, message__content_file=filename.strip())):
						#print("counting " + filename)
					# check to make sure it's in the forums of interest
						call['listens'] += 1
					#else:
						#print("rejecting" + filename)
			
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
			
		print("Lurks, Posts, and Average listens within call, by week:")
		print("Date\tLurks\tPosts\tLurking Rate\tListens per call")
		dates = listens.keys()
		dates.sort()
		for date in dates:
			lurks = listens[date]['lurks']
			posts = listens[date]['posts']
			lurk_rate = float(lurks)/float(lurks + posts)
			n_listens = listens[date]['listens']
			avg_listens = float(sum(n_listens))/float(len(n_listens))
				
			print(date.strftime('%Y-%m-%d') + "\t" + str(lurks) + "\t" + str(posts) + "\t" + str(lurk_rate) + "\t" + str(avg_listens))	
			
	return listens

def get_recordings(filename, destnum=False, phone_num_filter=False, date_start=False, date_end=False, legacy_log=False, transfer_calls=False):
	files = []
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
				current_week_start = datetime(year=current_date.year, month=current_date.month, day=current_date.day)

			delta = current_date - current_week_start

			if delta.days > 6:
				current_week_start = datetime(year=current_date.year, month=current_date.month, day=current_date.day)
			

			if otalo_utils.is_record(line):
				filename = otalo_utils.get_prompt(line)
				filename = filename[filename.rfind('/')+1:]
				files.append(filename)
					
		except ValueError as err:
			#print("ValueError: " + line)
			continue
		except IndexError as err:
			continue
		except otalo_utils.PhoneNumException:
			#print("PhoneNumException: " + line)
			continue
	
	return files

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
