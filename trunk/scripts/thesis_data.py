import sys
from datetime import datetime, timedelta
from django.db.models import Count
import otalo_utils, num_calls, stats_by_phone_num, call_duration
from otalo.surveys.models import Survey, Call, Subject
from otalo.AO.models import Line, Forum, Message_forum

def calls_by_caller(f, line, min=False, max=False, date_start=None, date_end=None):
	calls = stats_by_phone_num.get_calls_by_number(filename=f, destnum=str(line.number), date_start=date_start, date_end=date_end, quiet=True)
	
	print("Number of calls by phone number:")
	call_dict = {}
	if min or max:
		for num, tot in calls:
			if (not min or tot >= min) and (not max or tot <= max):
				print(num +": "+str(tot))
				call_dict[num] = tot
	else:
		for num, tot in calls:
			print(num +": "+str(tot))
			call_dict[num] = tot
	
	return call_dict
	
def posts_by_caller(line, numbers=None, threshold=None, start_date=None, end_date=None):
	posts = Message_forum.objects.filter(forum__line=line)
	
	if start_date:
		posts = posts.filter(message__date__gte=start_date)
	if end_date:
		posts = posts.filter(message__date__lt=end_date)
		
	if not numbers:
		numbers = posts.values('message__user__number').distinct().annotate(num_posts=Count('id')).order_by('-num_posts')
		numbers = [vals['message__user__number'] for vals in numbers]
	
	by_number = {}
	print("Number of messages by caller:")
	print("Number\t\tOriginal Posts\t\tResponses")
	for number in numbers:
		calls = {}
		orig = posts.filter(message__user__number=number, message__lft=1)
		calls['orig'] = orig.count()
		calls['orig_app'] = orig.filter(status=Message_forum.STATUS_APPROVED).count()
		
		resp = posts.filter(message__user__number=number, message__lft__gt=1)
		calls['resp'] = resp.count()
		calls['resp_app'] = resp.filter(status=Message_forum.STATUS_APPROVED).count()
		print(number+"\t"+str(calls['orig'])+" ("+str(calls['orig_app'])+" approved)\t"+str(calls['resp'])+" ("+str(calls['resp_app'])+" approved)")
		by_number[number] = calls
		
	return by_number
	
def caller_info(f, line, numbers, date_start=None, date_end=None):
	for number in numbers:
		# calls over time
		num_calls.get_calls(filename=f, destnum=str(line.number), phone_num_filter=[number], date_start=date_start, date_end=date_end)
		
		# call length over time
		call_duration.get_call_durations(filename=f, destnum=str(line.number), phone_num_filter=[number], date_start=date_start, date_end=date_end)
		
		# feature access breakdown over time
		num_calls.get_calls_by_feature(filename=f, destnum=str(line.number), phone_num_filter=[number], date_start=date_start, date_end=date_end)
		
		# broadcasts received
		print("Broadcasts received (and attempted)")
		d = date_start
		while d < date_end:
			calls = Call.objects.filter(survey__broadcast=True, date__gte=d, date__lt=d+timedelta(days=6), subject__number=number)
			n_attempted = calls.values('survey').distinct().count()
			# assumes one complete call per survey
			n_completed = calls.filter(complete=True).count()
			print(otalo_utils.date_str(d) +":\t"+str(n_completed)+" ("+str(n_attempted)+" attempted)")
			d += timedelta(days=6)
		
		# response calls attempted/received
		print("Response calls received (and attempted)")
		d = date_start
		while d < date_end:
			calls = Call.objects.filter(survey__name__contains=Survey.ANSWER_CALL_DESIGNATOR, date__gte=d, date__lt=d+timedelta(days=6), subject__number=number)
			n_attempted = calls.values('survey').distinct().count()
			# assumes one complete call per survey
			n_completed = calls.filter(complete=True).count()
			print(otalo_utils.date_str(d) +":\t"+str(n_completed)+" ("+str(n_attempted)+" attempted)")
			d += timedelta(days=7)
		
		# calls made within X days of bcast, response call

def repeat_callers(f, line, start, window_end, end, incr, min=False, max=False):
	calls = calls_by_caller(f, line, min=min, max=max, date_start=start, date_end=window_end)
	numbers = calls.keys()
	matrix = {}
	for num in numbers:
		matrix[num] = []
	
	d = start
	header = "\t"
	while d < end:
		header += otalo_utils.date_str(d) +"\t"
		calls = stats_by_phone_num.get_calls_by_number(filename=f, destnum=line.number, date_start=d, date_end=d+incr, quiet=True)
		for num in numbers:
			if num in [key for key,val in calls]:
				for num2, tot in calls:
					if num2 == num:
						matrix[num].append(tot)
			else:
				matrix[num].append(0)
		d += incr
	
	print(header)
	for num in matrix:
		calls = matrix[num]
		calls_str = num+"\t"+"\t".join([str(tot) for tot in calls])
		print(calls_str)

def regular_callers(f, line, start, incr, end, min=False, max=False):
	calls = calls_by_caller(f, line, min=min, max=max, date_start=start, date_end=start+incr)
	numbers = calls.keys()
	matrix = {}
	for num in numbers:
		matrix[num] = []
	
	d = start
	header = "\t"
	while d < end:
		header += otalo_utils.date_str(d) +"\t"
		calls = calls_by_caller(f, line, min=min, max=max, date_start=d, date_end=d+incr)
		for num in numbers:
			if num in calls and num in matrix:
				matrix[num].append(calls[num])
			elif num in matrix:
				print("deleting "+num)
				del matrix[num]
		d += incr
	
	print(header)
	for num in matrix:
		calls = matrix[num]
		calls_str = num+"\t"+"\t".join([str(tot) for tot in calls])
		print(calls_str)

def turn_around_time(line, date_start=False, date_end=False):
	questions = Message_forum.objects.filter(message__date__gte=date_start, message__date__lt=date_end, message__lft=1, forum__line=line)
	
	response_calls = Call.object.filter(survey__number__in=[line.number, line.outbound_number], survey__name__contains=Survey.ANSWER_CALL_DESIGNATOR, date__gte=date_start, date__lt=date_end)
	
	# number of posted questions
	# number of responses (unique questions)
	# number of E2Es
	# of those E2Es, average response time
	
def response_call_recievers(f, line, date_start, window_end, date_end=False):
	# get people who picked up a response call
	receivers = Subject.objects.filter(call__survey__name__contains=Survey.ANSWER_CALL_DESIGNATOR, call__complete=True, call__date__gte=date_start, call__date__lt=window_end).distinct()
	numbers = [subj.number for subj in receivers]
	calls = stats_by_phone_num.get_calls_by_number(f, line.number, date_start=date_start, date_end=window_end, quiet=True)
	others = list(set([num for num,tot in calls ]) - set(numbers))
	
	print("n_recievers is " + str(len(numbers)) + "; n_others is "+ str(len(others)))
	# calculate their calling and posting
	calls = num_calls.get_calls(f, line.number, phone_num_filter=numbers, date_start=date_start, date_end=date_end, quiet=True)
	dates = calls.keys()
	dates.sort()
	n_receivers = len(numbers)
	print("Calls by response call receivers")
	print("Date\tCalls\tCalls per Caller")
	for date in dates:
		print(otalo_utils.date_str(date) +"\t"+str(calls[date])+"\t"+str(float(calls[date])/float(n_receivers)))
	
	print("Posting by response call receivers")
	print("Date\tPosts\tOriginal\tApproved\tUnique Posters\tPosts per Poster")
	for date in dates:
		msgs = Message_forum.objects.filter(message__user__number__in=numbers, message__date__gte=date, message__date__lt=date+timedelta(days=7), forum__line=line)
		n_total = msgs.count()
		n_orig = msgs.filter(message__lft=1).count()
		n_approved = msgs.filter(status=Message_forum.STATUS_APPROVED).count()
		n_unique = msgs.values('message__user').distinct().count()
		print(otalo_utils.date_str(date) +"\t"+str(n_total)+"\t"+str(n_orig)+"\t"+str(n_approved)+"\t"+str(n_unique)+"\t"+str(float(n_total)/float(len(numbers))))
		
	# compare it to non-receivers
	calls = num_calls.get_calls(f, line.number, phone_num_filter=others, date_start=date_start, date_end=date_end, quiet=True)
	dates = calls.keys()
	dates.sort()
	n_others = len(others)
	print("Calls by non-receivers")
	print("Date\tCalls\tCalls per Caller")
	for date in dates:
		print(otalo_utils.date_str(date) +"\t"+str(calls[date])+"\t"+str(float(calls[date])/float(n_others)))
		
	print("Posting by non-receivers")
	print("Date\tPosts\tOriginal\tApproved\tUnique Posters\tPosts per Poster")
	for date in dates:
		msgs = Message_forum.objects.filter(message__date__gte=date, message__date__lt=date+timedelta(days=7), forum__line=line).exclude(message__user__number__in=numbers)
		n_total = msgs.count()
		n_orig = msgs.filter(message__lft=1).count()
		n_approved = msgs.filter(status=Message_forum.STATUS_APPROVED).count()
		n_unique = msgs.values('message__user').distinct().count()
		print(otalo_utils.date_str(date) +"\t"+str(n_total)+"\t"+str(n_orig)+"\t"+str(n_approved)+"\t"+str(n_unique)+"\t"+str(float(n_total)/float(len(others))))
	
def main():
	if len(sys.argv) < 3:
		print("Wrong")
	else:
		f = sys.argv[1]
		lineid = sys.argv[2]
		line = Line.objects.get(pk=int(lineid))
	#calls_by_caller(f,line)
	#posts_by_caller(line)
	start = datetime(year=2010, month=7, day=1)
	window_end = datetime(year=2010, month=8, day=1)
	end = datetime(year=2011, month=4, day=1)
	#repeat_callers(f, line, start, window_end, end, timedelta(days=30), min=4)
	#regular_callers(f,line,start,timedelta(days=30),start+timedelta(90),min=4)
	#num_calls.get_calls(f, line.number)
	#call_duration.get_call_durations(f, line.number, transfer_calls=True)
	#num_calls.get_calls_by_feature(f, line.number)
	#num_calls.get_features_within_call(f, line.number)
	#num_calls.get_listens_within_call(f, line.number)
	#num_calls.get_calls(f, line.number, log="okyourreplies", date_start=start, date_end=end)
	
	#stats_by_phone_num.get_calls_by_number(f, destnum=line.number)
	#stats_by_phone_num.new_and_repeat_callers(f,line.number)
	#response_call_recievers(f, line, start, start+timedelta(days=90))
	
	#num_calls.get_num_qna(line,1, start)
	#forums = Forum.objects.filter(line=line, posting_allowed='y')
	#num_calls.get_lurking_and_posting(f, line.number, forums)
	stats_by_phone_num.get_posts_by_caller(line,date_start=start)
	
main()