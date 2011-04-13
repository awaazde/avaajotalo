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
	#call_duration.get_call_durations(f, line.number)
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
	#stats_by_phone_num.get_posts_by_caller(line,date_start=start)
	
	ao_call = ['9909840752', '9724709731', '9537843296', '9978719198', '9624918600', '9909189931', '9624372044', '9428897286', '9427524506', '9723645086', '9723175486', '9978383329', '9913611102', '9974641216', '9925828770', '9725729441', '9725691201', '9824522845', '9824387276', '9429078455', '9327747776', '9925660140', '9909650510', '9726061931', '9723712092', '9687696771', '9662380410', '9327939212', '9016639062', '9978401316', '9978184796', '9924188507', '9913468462', '9898925850', '9879319268', '9726610575', '9726050841', '9712120200', '9638252561', '9428557642', '9428478402', '8140128125', '7930020473', '9983947293', '9978731064', '9924227064', '9909847737', '9879273225', '9737489668', '9725864258', '9725328757', '9624123165', '9624077894', '9429709493', '9428984967', '9427751940', '9427670549', '8347212846', '8264191139', '9998633663', '9979898556', '9974484853', '9925357301', '9924355148', '9913927711', '9909225834', '9909178954', '9824367539', '9824216031', '9725971997', '9725450210', '9687416096', '9662681414', '9586532932', '9586371150', '9537111226', '9510729514', '9428024460', '9426698620', '9099430828', '9016638646', '8140676832', '8140634129', '7567401431', '4082476797', '9998925115', '9998884123', '9998142436', '9979766707', '9978348436', '9978304580', '9974305873', '9974096352', '9924865703', '9924834046', '9913453976', '9913217067', '9909479881', '9909464228', '9904316554', '9904230893', '9879128855', '9825855832', '9824967764', '9824655191', '9737371597', '9727696899', '9726719779', '9726567243', '9725691334', '9724754900', '9723547764', '9723202471', '9712896313', '9712756833', '9662194285', '9638991597', '9601567245', '9586955158', '9574433611', '9558662363', '9429775562', '9429323243', '9428173588', '9427745224', '9427044242', '9426930855', '9327538732', '9327013636', '8980853187', '8980675869', '8460850693', '8347934710', '8140437612', '8128381829', '7874439283', '7874093215', '2742295194']
	ao_rec = ['9429723855', '9974747129', '8980370299', '9978719704', '9979314531', '7567462909', '9227352190', '9998952575', '7940073682', '9724994419', '9687148790', '9374692168', '9712123049', '8905129801', '9924494961', '9725993296', '9558350208', '9824991658', '9723484025', '9624453030', '8460615131', '9925729923', '9909224149', '9824419679', '9723177485', '9714827176', '9558486097', '9428313498', '8511626412', '9979780231', '9978164261', '9925095361', '9913416184', '9898947264', '9824082538', '9726800134', '9723944338', '9714736647', '9574707387', '9537410339', '9427379911', '9033618693', '7874419626', '9978561710', '9924258467', '9904839930', '9898101498', '9727304678', '9726659436', '9725317885', '9624671576', '9601813165', '9537170017', '9428979812', '9428063295', '9427330743', '8511867385', '8140292899', '2735244041', '9979169306', '9974572646', '9925257554', '9924938878', '9913614301', '9909525638', '9909104758', '9825772077', '9737023720', '9726356814', '9724877658', '9714382944', '9662243269', '9586641932', '9574459813', '9537252436', '9429718191', '9428826155', '9426373684', '9228231519', '8511903176', '8347212844', '8094178238', '7874131429', '2852634234', '2230372600', '9998488871', '9998149693', '9979383298', '9978351259', '9978113367', '9974719483', '9925796808', '9925191483', '9924500374', '9913492428', '9909837097', '9909505783', '9904972036', '9904442351', '9904170697', '9879314437', '9825458993', '9824980123', '9824092447', '9737456751', '9727603175', '9726813036', '9726537942', '9725756167', '9724494513', '9723686232', '9714299629', '9714142563', '9712408031', '9662358808', '9638656680', '9624235420', '9586724472', '9574548758', '9537877440', '9429801307', '9428826158', '9428372037', '9427640129', '9427384096', '9426783156', '9374154767', '9228488236', '8980899080', '8980209697', '8511397915', '8347212426', '8140754606', '8128292264', '7927540664', '7600748475', '2749278168', '2652370489']
	ao_rate = ['9974540063', '9714025302', '9725638832', '8140743653', '9974075854', '9737317218', '8530027163', '2828296960', '9727907002', '9624045636', '9428987491', '9687032987', '9429140966', '9824836342', '9727998007', '9909689369', '9879841603', '9687756510', '9662062754', '2737291211', '9979273464', '9904665168', '9879188943', '9723150230', '9723003872', '9510936577', '9428485129', '8128253081', '7698016581', '9974664975', '9925220911', '9904825353', '9904714990', '9727539593', '9727105210', '9723701860', '9723332236', '9558935262', '9558637694', '9328544455', '9099470522', '7600983150', '2652243153', '9974664111', '9925671933', '9898997060', '9898338885', '9727064281', '9726717766', '9723647374', '9714267499', '9574519710', '9558301208', '9428971440', '9428138438', '9426971968', '8866755767', '8140188158', '8128385808', '9978790056', '9974959374', '9925189361', '9925145434', '9909759893', '9909666361', '9904822007', '9898530403', '9727610591', '9727548155', '9724774625', '9724469854', '9662132248', '9586943624', '9549447133', '9537420909', '9429352624', '9428826157', '9426314344', '9408169422', '8511860573', '8347475583', '7930613783', '7927418420', '2791234377', '2735222394', '9998483785', '9998318554', '9979087320', '9978421160', '9974836209', '9974762694', '9925618145', '9925577906', '9924057403', '9913565061', '9909748436', '9909520594', '9904889475', '9904516849', '9904121072', '9879639737', '9825363929', '9825312792', '9737987925', '9737873631', '9727112264', '9726827932', '9726487561', '9725876825', '9723887815', '9723746757', '9714246198', '9714240289', '9712294627', '9687973434', '9624859879', '9624671521', '9586168612', '9574850087', '9537319808', '9537293638', '9428826154', '9428568904', '9427601786', '9427601785', '9426185118', '9375511851', '9016807601', '9016638632', '8758189497', '8530316974', '8141728419', '8141409658', '8000706977', '7928282828', '2862918188', '2772278302', '2735245790']
	
	#num_calls.get_calls(f,line.number,phone_num_filter=ao_call)
	#num_calls.get_calls(f,line.number,phone_num_filter=ao_rec)
	#num_calls.get_calls(f,line.number,phone_num_filter=ao_rate)
	
	num_calls.get_num_qna(line,1, start, phone_num_filter=ao_call)
	#num_calls.get_num_qna(line,1, start, phone_num_filter=ao_rec)
	#num_calls.get_num_qna(line,1, start, phone_num_filter=ao_rate)
main()