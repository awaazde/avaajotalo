import sys
from datetime import datetime, timedelta
from django.db.models import Count
import otalo_utils, num_calls, stats_by_phone_num, call_duration
from otalo.surveys.models import Survey, Call, Subject, Input
from otalo.AO.models import User, Line, Forum, Message_forum

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

def ratings(f, line, numbers):
	results = Input.objects.filter(call__subject__number__in=numbers, call__survey__name__contains="RATE")
	n_results = results.count()
	n_ones = results.filter(input='1').count()
	n_twos = results.filter(input='2').count()
	n_threes = results.filter(input='3').count()
	
	results = results.values('input')
	results = [int(pair.values()[0]) for pair in results]
	
	mean = float(sum(results))/len(results)
	med = median(results)

	print('tot ratings='+str(n_results)+'; ones='+str(n_ones)+'; twos='+str(n_twos)+'; threes='+str(n_threes))
	print('Mean='+str(mean)+'; Median='+str(med))
	
def median(numericValues):
  theValues = sorted(numericValues)

  if len(theValues) % 2 == 1:
    return theValues[(len(theValues)+1)/2-1]
  else:
    lower = theValues[len(theValues)/2-1]
    upper = theValues[len(theValues)/2]

    return (float(lower + upper)) / 2  

def ratings_by_caller(f, line, prompt, numbers):
	ratings = {}
	prompts = {}
	calls = stats_by_phone_num.get_calls_by_number(f, line.number, phone_num_filter=numbers, log=prompt, quiet=True, transfer_calls=True)
	for num, tot in calls:
		prompts[num] = tot
		
	for num in numbers:
		n_prompts = prompts[num]
		counts = Input.objects.filter(call__subject__number=num)
		count1 = counts.filter(input='1').count()
		count2 = counts.filter(input='2').count()
		count3 = counts.filter(input='3').count()
		ratings[num] = [n_prompts,count1,count2,count3]
		
	print("Ratings by number")
	for num,counts in ratings.iteritems():
		print(num+"\t"+str(counts[0])+"\t"+str(counts[1])+"\t"+str(counts[2])+"\t"+str(counts[3]))

def approval_rate(line, numbers, start_date, end_date):
	if numbers:
		users = User.objects.filter(number__in=numbers)
	else:
		users = User.objects.all()
		
	msgs = Message_forum.objects.filter(forum__line=line, message__user__in=users,message__date__gte=start_date, message__date__lt=end_date)
	print("Total messages: " + str(msgs.count()))
	approved = msgs.filter(status=Message_forum.STATUS_APPROVED)
	rejected = msgs.filter(status=Message_forum.STATUS_REJECTED)
	print("Approved: " + str(approved.count()))
	rate = float(approved.count())/float(msgs.count())
	print("Rate: " + str(rate))
	for msg in rejected:
		print(str(msg))
		
def get_completed_bcasts(number, date_start=False, date_end=False):
	surveys = Survey.objects.filter(broadcast=True)
	
	if date_start:
		surveys = surveys.filter(call__date__gte=date_start)
		
	if date_end:
		surveys = surveys.filter(call__date__lt=date_end)
	else:
		now = datetime.now()
		date_end = datetime(now.year, now.month, now.day)
		
	oneday = timedelta(days=1)
	dt = date_start
	result = ''
	
	while dt < date_end:
		n_calls = Call.objects.filter(date__gte=dt, date__lt=dt+oneday, survey__in=surveys, complete=True).count()
		result += otalo_utils.date_str(dt)+'\t'+str(n_calls)+'\n'
		dt += oneday 
	
	print("Number of outbound bcast calls received")
	print(result)
	
def answer_call_effect(f, line, date_start=False, date_end=False):
	nums = stats_by_phone_num.get_calls_by_number(f,line.number, date_start=date_start, date_end=date_end, quiet=True)
	
	for num, tot in nums:
		# get number of picked up answer calls
		n_answer_calls = Call.objects.filter(subject__number=num, survey__name__contains=Survey.ANSWER_CALL_DESIGNATOR, complete=True).count()
		print(num +"\t"+str(tot)+"\t"+str(n_answer_calls))
		
def topics(line, date_start=False, date_end=False):
	cropcounts = {}
	topiccounts = {}
	messages = Message_forum.objects.filter(forum__line=line)
	
	if date_start:
		messages = messages.filter(message__date__gte=date_start)
	
	if date_end:
		messages = messages.filter(message__date__lt=date_end)
	
	for msg in messages:
		for t in msg.tags.all():
			if t.type == 'agri-crop':
				if t.tag in cropcounts:
					cropcounts[t.tag] += 1
				else:
					cropcounts[t.tag] = 1
			elif t.type == 'agri-topic':
				if t.tag in topiccounts:
					topiccounts[t.tag] += 1
				else:
					topiccounts[t.tag] = 1
					
	print('crop counts')
	srted = sorted(cropcounts.iteritems(), key=lambda(k,v): (v,k), reverse=True)
	for tag, count in srted:
		print(tag+'\t'+str(count))
	
	print('topic counts')
	srted = sorted(topiccounts.iteritems(), key=lambda(k,v): (v,k), reverse=True)
	for tag, count in srted:
		print(tag+'\t'+str(count))

def main():
	if len(sys.argv) < 3:
		print("Wrong")
	else:
		f = sys.argv[1]
		lineid = sys.argv[2]
		line = Line.objects.get(pk=int(lineid))
	#calls_by_caller(f,line)
	#posts_by_caller(line)
	start = datetime(year=2011, month=1, day=1)
	window_end = datetime(year=2011, month=3, day=1)
	end = datetime(year=2011, month=5, day=20)
	#repeat_callers(f, line, start, end, end, timedelta(days=30), min=1)
	#regular_callers(f,line,start,timedelta(days=30),start+timedelta(90),min=4)
	num_calls.get_calls(f, line.number)
	#num_calls.get_calls(f, line.number, legacy_log=True)
	#call_duration.get_call_durations(f, line.number)
	#num_calls.get_calls_by_feature(f, line.number, date_start=start)
	#num_calls.get_features_within_call(f, line.number)
	#num_calls.get_listens_within_call(f, line.number)
	#num_calls.get_calls(f, line.number, log="okyourreplies", date_start=start, date_end=end)
	
	#stats_by_phone_num.get_calls_by_number(f, destnum=line.number)
	#stats_by_phone_num.new_and_repeat_callers(f,line.number)
	#response_call_recievers(f, line, start, start+timedelta(days=90))
	
	#num_calls.get_num_qna(f, line, date_start=start)
	#forums = Forum.objects.filter(line=line, posting_allowed='y')
	#num_calls.get_lurking_and_posting(f, line.number, forums)
	#stats_by_phone_num.get_posts_by_caller(line,date_start=start)
	
	ao_call = ['9909840752', '9724709731', '9537843296', '9978719198', '9624918600', '9909189931', '9624372044', '9428897286', '9427524506', '9723645086', '9723175486', '9978383329', '9913611102', '9974641216', '9925828770', '9725729441', '9725691201', '9824522845', '9824387276', '9429078455', '9327747776', '9925660140', '9909650510', '9726061931', '9723712092', '9687696771', '9662380410', '9327939212', '9016639062', '9978401316', '9978184796', '9924188507', '9913468462', '9898925850', '9879319268', '9726610575', '9726050841', '9712120200', '9638252561', '9428557642', '9428478402', '8140128125', '7930020473', '9983947293', '9978731064', '9924227064', '9909847737', '9879273225', '9737489668', '9725864258', '9725328757', '9624123165', '9624077894', '9429709493', '9428984967', '9427751940', '9427670549', '8347212846', '8264191139', '9998633663', '9979898556', '9974484853', '9925357301', '9924355148', '9913927711', '9909225834', '9909178954', '9824367539', '9824216031', '9725971997', '9725450210', '9687416096', '9662681414', '9586532932', '9586371150', '9537111226', '9510729514', '9428024460', '9426698620', '9099430828', '9016638646', '8140676832', '8140634129', '7567401431', '4082476797', '9998925115', '9998884123', '9998142436', '9979766707', '9978348436', '9978304580', '9974305873', '9974096352', '9924865703', '9924834046', '9913453976', '9913217067', '9909479881', '9909464228', '9904316554', '9904230893', '9879128855', '9825855832', '9824967764', '9824655191', '9737371597', '9727696899', '9726719779', '9726567243', '9725691334', '9724754900', '9723547764', '9723202471', '9712896313', '9712756833', '9662194285', '9638991597', '9601567245', '9586955158', '9574433611', '9558662363', '9429775562', '9429323243', '9428173588', '9427745224', '9427044242', '9426930855', '9327538732', '9327013636', '8980853187', '8980675869', '8460850693', '8347934710', '8140437612', '8128381829', '7874439283', '7874093215', '2742295194']
	ao_rec = ['9429723855', '9974747129', '8980370299', '9978719704', '9979314531', '7567462909', '9227352190', '9998952575', '7940073682', '9724994419', '9687148790', '9374692168', '9712123049', '8905129801', '9924494961', '9725993296', '9558350208', '9824991658', '9723484025', '9624453030', '8460615131', '9925729923', '9909224149', '9824419679', '9723177485', '9714827176', '9558486097', '9428313498', '8511626412', '9979780231', '9978164261', '9925095361', '9913416184', '9898947264', '9824082538', '9726800134', '9723944338', '9714736647', '9574707387', '9537410339', '9427379911', '9033618693', '7874419626', '9978561710', '9924258467', '9904839930', '9898101498', '9727304678', '9726659436', '9725317885', '9624671576', '9601813165', '9537170017', '9428979812', '9428063295', '9427330743', '8511867385', '8140292899', '2735244041', '9979169306', '9974572646', '9925257554', '9924938878', '9913614301', '9909525638', '9909104758', '9825772077', '9737023720', '9726356814', '9724877658', '9714382944', '9662243269', '9586641932', '9574459813', '9537252436', '9429718191', '9428826155', '9426373684', '9228231519', '8511903176', '8347212844', '8094178238', '7874131429', '2852634234', '2230372600', '9998488871', '9998149693', '9979383298', '9978351259', '9978113367', '9974719483', '9925796808', '9925191483', '9924500374', '9913492428', '9909837097', '9909505783', '9904972036', '9904442351', '9904170697', '9879314437', '9825458993', '9824980123', '9824092447', '9737456751', '9727603175', '9726813036', '9726537942', '9725756167', '9724494513', '9723686232', '9714299629', '9714142563', '9712408031', '9662358808', '9638656680', '9624235420', '9586724472', '9574548758', '9537877440', '9429801307', '9428826158', '9428372037', '9427640129', '9427384096', '9426783156', '9374154767', '9228488236', '8980899080', '8980209697', '8511397915', '8347212426', '8140754606', '8128292264', '7927540664', '7600748475', '2749278168', '2652370489']
	ao_rate = ['9974540063', '9714025302', '9725638832', '8140743653', '9974075854', '9737317218', '8530027163', '2828296960', '9727907002', '9624045636', '9428987491', '9687032987', '9429140966', '9824836342', '9727998007', '9909689369', '9879841603', '9687756510', '9662062754', '2737291211', '9979273464', '9904665168', '9879188943', '9723150230', '9723003872', '9510936577', '9428485129', '8128253081', '7698016581', '9974664975', '9925220911', '9904825353', '9904714990', '9727539593', '9727105210', '9723701860', '9723332236', '9558935262', '9558637694', '9328544455', '9099470522', '7600983150', '2652243153', '9974664111', '9925671933', '9898997060', '9898338885', '9727064281', '9726717766', '9723647374', '9714267499', '9574519710', '9558301208', '9428971440', '9428138438', '9426971968', '8866755767', '8140188158', '8128385808', '9978790056', '9974959374', '9925189361', '9925145434', '9909759893', '9909666361', '9904822007', '9898530403', '9727610591', '9727548155', '9724774625', '9724469854', '9662132248', '9586943624', '9549447133', '9537420909', '9429352624', '9428826157', '9426314344', '9408169422', '8511860573', '8347475583', '7930613783', '7927418420', '2791234377', '2735222394', '9998483785', '9998318554', '9979087320', '9978421160', '9974836209', '9974762694', '9925618145', '9925577906', '9924057403', '9913565061', '9909748436', '9909520594', '9904889475', '9904516849', '9904121072', '9879639737', '9825363929', '9825312792', '9737987925', '9737873631', '9727112264', '9726827932', '9726487561', '9725876825', '9723887815', '9723746757', '9714246198', '9714240289', '9712294627', '9687973434', '9624859879', '9624671521', '9586168612', '9574850087', '9537319808', '9537293638', '9428826154', '9428568904', '9427601786', '9427601785', '9426185118', '9375511851', '9016807601', '9016638632', '8758189497', '8530316974', '8141728419', '8141409658', '8000706977', '7928282828', '2862918188', '2772278302', '2735245790']
	ao_verygood= ['9974540063', '9714025302', '9725638832', '8140743653', '9974075854', '9737317218', '8530027163', '2828296960', '9727907002', '9624045636', '9428987491', '9687032987', '9429140966', '9824836342', '9727998007', '9909689369', '9879841603', '9687756510', '9662062754', '2737291211', '9979273464', '9904665168', '9879188943', '9723150230', '9723003872', '9510936577', '9428485129', '8128253081', '7698016581', '9974664975', '9925220911', '9904825353', '9904714990', '9727539593', '9727105210', '9723701860', '9723332236', '9558935262', '9558637694', '9328544455', '9099470522', '7600983150', '2652243153', '9974664111', '9925671933', '9898997060', '9898338885', '9727064281', '9726717766', '9723647374', '9714267499', '9574519710', '9558301208', '9428971440', '9428138438', '9426971968', '8866755767', '8140188158', '8128385808', '9978790056', '9974959374', '9925189361', '9925145434', '9909759893', '9909666361', '9904822007', '9898530403', '9727610591', '9727548155', '9726537942']
	ao_good = ['9724774625', '9724469854', '9662132248', '9586943624', '9549447133', '9537420909', '9429352624', '9428826157', '9426314344', '9408169422', '8511860573', '8347475583', '7930613783', '7927418420', '2791234377', '2735222394', '9998483785', '9998318554', '9979087320', '9978421160', '9974836209', '9974762694', '9925618145', '9925577906', '9924057403', '9913565061', '9909748436', '9909520594', '9904889475', '9904516849', '9904121072', '9879639737', '9825363929', '9825312792', '9737987925', '9737873631', '9727112264', '9726827932', '9726487561', '9725876825', '9723887815', '9723746757', '9714246198', '9714240289', '9712294627', '9687973434', '9624859879', '9624671521', '9586168612', '9574850087', '9537319808', '9537293638', '9428826154', '9428568904', '9427601786', '9427601785', '9426185118', '9375511851', '9016807601', '9016638632', '8758189497', '8530316974', '8141728419', '8141409658', '8000706977', '7928282828', '2862918188', '2772278302', '2735245790', '9726537942'] 
	
	uks_self=['9425408718', '9479463105', '9425142355', '7879795383', '9424359772', '9617495057', '8989081463', '9407387714', '9688091261', '9658673799', '9955762806', '9324583271', '9165027738', '9685128577', '9617502415', '9850832904', '2242602555', '9095015859', '9046470359', '8895548775', '9993477177', '9303504613', '8014471674', '9589472035', '9303503671', '9936588955', '9685924670', '8085778508', '9984826067', '9839366040', '9669346636', '9630380751', '9406773938', '9009474371', '8521710358', '2240385500', '9972786101', '9903967969', '9806710948', '9752771256', '9680241419', '9641333970', '9618250596', '9559782833', '9423439482', '9325717173', '8120567044', '7898282760', '9977376721', '9893157371', '9835492842', '9767306758', '9691282252', '9651088261', '9635406526', '9621121121', '9589942486', '9552019902', '9337455247', '9308970634', '9272579655', '9090494439', '9002211987', '8889715991', '8698039387', '8120163814', '7869084523', '4312432224', '2241027000', '9987082017', '9985019606', '9981062252', '9973056409', '9960049033', '9935876562', '9926416875', '9907112298', '9897786891', '9893119306', '9873012615', '9856594168', '9827947014', '9774960794', '9753765895', '9752548594', '9713907086', '9685124998', '9669051154', '9636614610', '9617590655', '9600583469', '9575800503', '9546303813', '9480367695', '9442277086', '9422846505', '9406773279', '9368285257', '9313968447', '9303503649', '9259965040', '9213934622', '9039807397', '9005544833', '8977595318', '8957412965', '8895816935', '8874128952', '8769865944', '8435427970', '8087491175', '8052231422', '7898283428', '7875865888', '7830818050', '7699457974', '7504934283', '7259992262', '2964230503', '2240710300']
	uks_group=['7879444919', '9425823322', '9575372547', '9165550473', '9977557037', '8120012298', '9752149646', '9862621335', '9617502439', '9938646770', '9009572884', '9630376865', '9917528314', '9985472254', '9893966806', '9425012148', '9198915523', '9755195845', '9749739837', '8120449247', '8014087015', '9166304603', '8095484520', '9589179834', '9413459495', '9893498002', '9777876824', '8002842506', '9998249088', '9792564759', '9761087004', '9621881739', '9425831038', '9005601026', '8982063789', '2229650918', '9998249505', '9893506365', '9869616115', '9752547242', '9717000918', '9635119446', '9627834041', '9475119437', '9470614765', '9044334552', '8670031413', '2241027400', '2240385300', '9880002112', '9871167533', '9728387581', '9703781328', '9641860035', '9639989019', '9617721370', '9589999742', '9479148463', '9424976141', '9303417153', '9300802621', '9035409760', '9031179929', '8889421921', '8888456260', '7875580680', '7869187935', '2242517200', '2241027200', '9986874821', '9986628191', '9976199501', '9974946903', '9948376948', '9937088277', '9924415809', '9917772786', '9893778480', '9893170803', '9867712320', '9860774476', '9824944931', '9778714472', '9753479231', '9752914480', '9696052674', '9687405297', '9668218851', '9654932451', '9617590082', '9612267630', '9566657622', '9555743805', '9465703465', '9450519168', '9421722741', '9407975913', '9359845917', '9320953357', '9301244522', '9261103669', '9211511270', '9177720970', '9001425011', '8983081240', '8906304585', '8899215274', '8873581297', '8859460650', '8239577563', '8103530074', '8007777686', '8002979416', '7869534672', '7860879975', '7644234665', '7505941231', '4962502983', '4024533405', '2240385850']
	uks_none=['9425605215', '9691791988', '9425141977', '9754795214', '9165022098', '9630803487', '9303734405', '8509623245', '9758195613', '8120063907', '9774910104', '9589405565', '8125103146', '9755734448', '9527951380', '8889184220', '9685968899', '9525725753', '9019489227', '8969922379', '9589379438', '9369941255', '7898333155', '7898282923', '7869738905', '1594348240', '9596659367', '9165517362', '9862502103', '9862437606', '9631134561', '9630602150', '9212322162', '9028095760', '8171193481', '7898327228', '9955514782', '9926431357', '9795005848', '9760546281', '9671832758', '9650806532', '9617674453', '9571840227', '9407834226', '9369005414', '8051496477', '7940090918', '9945422205', '9893617370', '9785887074', '9778206443', '9678396104', '9661811233', '9630390843', '9621291908', '9583678561', '9558060435', '9335317110', '9309317651', '9201057476', '9158148747', '8974504099', '8962603691', '8670030698', '8127204189', '7566423618', '7504737435', '2240385600', '1141881037', '9981716576', '9981339083', '9960799112', '9960226407', '9935210519', '9928659104', '9898051076', '9897934183', '9887019377', '9884495383', '9845636041', '9836056718', '9774524015', '9754503488', '9734527701', '9723720750', '9679391580', '9671405226', '9636507197', '9627400067', '9584791377', '9579543876', '9507444378', '9492553972', '9424989132', '9424385371', '9389103925', '9386280612', '9305620171', '9305207513', '9258912274', '9249737771', '9028681000', '9009637244', '8974677608', '8959410680', '8889004717', '8878885836', '8755714806', '8604143700', '8087202505', '8058269913', '7893198158', '7879140371', '7795953961', '7742949366', '7412405195', '7276094085', '2412451516', '2241026800']

	# delete responders	
	responders = ['9662062754','9428826158','9824991658', '9009572884', '9893966806']
	for r in responders:
		if r in ao_call:
			ao_call.remove(r)
		if r in ao_rec:
			ao_rec.remove(r)
		if r in ao_rate:
			ao_rate.remove(r)
		if r in ao_verygood:
			ao_verygood.remove(r)
		if r in ao_good:
			ao_good.remove(r)
		if r in uks_self:
			uks_self.remove(r)
		if r in uks_group:
			uks_group.remove(r)
		if r in uks_none:
			uks_none.remove(r) 
			
	#num_calls.get_calls(f,date_start=start,phone_num_filter=ao_call)
	#num_calls.get_calls(f,date_start=start,phone_num_filter=ao_rec)
	#num_calls.get_calls(f,date_start=start,phone_num_filter=ao_rate)
	
	#num_calls.get_calls(f,date_start=start,phone_num_filter=uks_self, transfer_calls="TRANSER_ONLY")
	#num_calls.get_calls(f,date_start=start,phone_num_filter=uks_group, transfer_calls="TRANSER_ONLY")
	#num_calls.get_calls(f,date_start=start,phone_num_filter=uks_none, transfer_calls="TRANSER_ONLY")

	#num_calls.get_calls(f,line.number,date_start=start,phone_num_filter=uks_self)
	#num_calls.get_calls(f,line.number,date_start=start,phone_num_filter=uks_group)
	#num_calls.get_calls(f,line.number,date_start=start,phone_num_filter=uks_none)
	
	#for total calls on voicebox
	#num_calls.get_calls(f)
	
	#call_duration.get_online_time(f, date_start=start,phone_num_filter=ao_call)
	#call_duration.get_online_time(f, date_start=start,phone_num_filter=ao_rec)
	#call_duration.get_online_time(f, date_start=start,phone_num_filter=ao_rate)
	
	#call_duration.get_online_time(f, date_start=start,phone_num_filter=uks_self)
	#call_duration.get_online_time(f, date_start=start,phone_num_filter=uks_group)
	#call_duration.get_online_time(f, date_start=start,phone_num_filter=uks_none)
	
	#AO
	blanks={'9662243269':datetime(year=2011,month=3,day=22),"9725317885":datetime(year=2011,month=3,day=24),"9909505783":datetime(year=2011,month=3,day=25),"9725993296":datetime(year=2011,month=3,day=31),"9574459813":datetime(year=2011,month=4,day=1),"9727603175":datetime(year=2011,month=4,day=1)}
	blanks.update({'9009474371':datetime(year=2011,month=3,day=3),'9617721370':datetime(year=2011,month=3,day=3),'9369005414':datetime(year=2011,month=3,day=3),'8957412965':datetime(year=2011,month=3,day=4),'8888456260':datetime(year=2011,month=3,day=4),'9752547242':datetime(year=2011,month=3,day=7),'7940086740':datetime(year=2011,month=3,day=8),'9960049033':datetime(year=2011,month=3,day=11),'8889421921':datetime(year=2011,month=3,day=11),'9630602150':datetime(year=2011,month=3,day=14),'9009474371':datetime(year=2011,month=3,day=17),'8889421921':datetime(year=2011,month=3,day=18),'8889421921':datetime(year=2011,month=3,day=22),'7869738905':datetime(year=2011,month=3,day=28),'9617721370':datetime(year=2011,month=3,day=31),'9423439482':datetime(year=2011,month=3,day=31)})
	outbound = "/Users/neil/Documents/survey.log"
	#num_calls.get_posts(f,outbound,blanks,line, date_start=start,phone_num_filter=ao_call)
	#num_calls.get_posts(f,outbound,blanks,line, date_start=start,phone_num_filter=ao_rec)
	#num_calls.get_posts(f,outbound,blanks,line, date_start=start,phone_num_filter=ao_rate)
	
	#num_calls.get_posts(f,outbound,blanks,line, date_start=start,phone_num_filter=uks_self, daily_data=True)
	#num_calls.get_posts(f,outbound,blanks,line, date_start=start,phone_num_filter=uks_group, daily_data=True)
	#num_calls.get_posts(f,outbound,blanks,line, date_start=start,phone_num_filter=uks_none, daily_data=True)
	
	#forums = Forum.objects.filter(line=line, posting_allowed='y')
	#num_calls.get_lurking_and_posting(f, line.number, line.forums, phone_num_filter=uks_self)
	#num_calls.get_lurking_and_posting(f, line.number, line.forums,phone_num_filter=uks_group)
	#num_calls.get_lurking_and_posting(f, line.number, line.forums,phone_num_filter=uks_none)
	
	#num_calls.get_num_qna(f, line, date_start=start,phone_num_filter=uks_self)
	#num_calls.get_num_qna(f, line, date_start=start,phone_num_filter=uks_group)
	#num_calls.get_num_qna(f, line, date_start=start,phone_num_filter=uks_none)

	# Post-experiment data only
	exp_start = datetime(year=2011,month=3,day=9)
	exp_end = datetime(year=2011,month=4,day=13)
	# need to run this once for inbound and once for outbound log
	#stats_by_phone_num.get_online_time(f, date_start=exp_start,phone_num_filter=ao_call)
	#stats_by_phone_num.get_online_time(f, date_start=exp_start,phone_num_filter=ao_rec)
	#stats_by_phone_num.get_online_time(f, date_start=exp_start,phone_num_filter=ao_rate)
	
	#num_calls.get_posts_by_number(f,outbound,blanks,line, date_start=exp_start,phone_num_filter=ao_call)
	#num_calls.get_posts_by_number(f,outbound,blanks,line, date_start=exp_start,phone_num_filter=ao_rec)
	#num_calls.get_posts_by_number(f,outbound,blanks,line, date_start=exp_start,phone_num_filter=ao_rate)
	
	# 8/3: pre-post posting
	#num_calls.get_posts_by_number(f,outbound,blanks,line, date_start=start, date_end=exp_start,phone_num_filter=ao_call)
	#num_calls.get_posts_by_number(f,outbound,blanks,line, date_start=start, date_end=exp_start,phone_num_filter=ao_rec)
	#num_calls.get_posts_by_number(f,outbound,blanks,line, date_start=start, date_end=exp_start,phone_num_filter=ao_rate)
	
	#num_calls.get_posts_by_number(f,outbound,blanks,line, date_start=exp_start, date_end=exp_end,phone_num_filter=ao_call)
	#num_calls.get_posts_by_number(f,outbound,blanks,line, date_start=exp_start, date_end=exp_end,phone_num_filter=ao_rec)
	#num_calls.get_posts_by_number(f,outbound,blanks,line, date_start=exp_start, date_end=exp_end,phone_num_filter=ao_rate)
	
	# pre-post calling
	#stats_by_phone_num.get_calls_by_number(f,date_start=start,date_end=exp_start,phone_num_filter=ao_call)
	#stats_by_phone_num.get_calls_by_number(f,date_start=start,date_end=exp_start,phone_num_filter=ao_rec)
	#stats_by_phone_num.get_calls_by_number(f,date_start=start,date_end=exp_start,phone_num_filter=ao_rate)
	
	#stats_by_phone_num.get_calls_by_number(f,date_start=exp_start,date_end=exp_end,phone_num_filter=ao_call)
	#stats_by_phone_num.get_calls_by_number(f,date_start=exp_start,date_end=exp_end,phone_num_filter=ao_rec)
	#stats_by_phone_num.get_calls_by_number(f,date_start=exp_start,date_end=exp_end,phone_num_filter=ao_rate)
	#print("days between start and exp_start: "+str((exp_start-start).days))
	#print("days between exp_start and exp_end: "+str((exp_end-exp_start).days))
	
	#UKS
	#exp_start = datetime(year=2011,month=3,day=3)
	#stats_by_phone_num.get_calls_by_number(f,date_start=exp_start,date_end=exp_end,phone_num_filter=uks_self)
	#stats_by_phone_num.get_calls_by_number(f,date_start=exp_start,date_end=exp_end,phone_num_filter=uks_group)
	#stats_by_phone_num.get_calls_by_number(f,date_start=exp_start,date_end=exp_end,phone_num_filter=uks_none)
	
	#num_calls.get_posts_by_number(f,outbound,blanks,line,uks_self, date_start=exp_start)
	#num_calls.get_posts_by_number(f,outbound,blanks,line,uks_group, date_start=exp_start)
	#num_calls.get_posts_by_number(f,outbound,blanks,line,uks_none, date_start=exp_start)
	
	#num_calls.get_calls(f,line.number,date_start=exp_start,date_end=exp_end,phone_num_filter=uks_self, daily_data=True)
	#num_calls.get_calls(f,line.number,date_start=exp_start,date_end=exp_end,phone_num_filter=uks_group, daily_data=True)
	#num_calls.get_calls(f,line.number,date_start=exp_start,date_end=exp_end,phone_num_filter=uks_none, daily_data=True)
	
	#stats_by_phone_num.get_num_listens(f, line.number, phone_num_filter=uks_self, date_start=exp_start,date_end=exp_end)
	#stats_by_phone_num.get_num_listens(f, line.number, phone_num_filter=uks_group, date_start=exp_start,date_end=exp_end)
	#stats_by_phone_num.get_num_listens(f, line.number, phone_num_filter=uks_none, date_start=exp_start,date_end=exp_end)
	
	#num_calls.get_listens_within_call(f, line.number, phone_num_filter=uks_self, date_start=exp_start,date_end=exp_end, daily_data=True)
	#num_calls.get_listens_within_call(f, line.number, phone_num_filter=uks_group, date_start=exp_start,date_end=exp_end, daily_data=True)
	#num_calls.get_listens_within_call(f, line.number, phone_num_filter=uks_none, date_start=exp_start,date_end=exp_end, daily_data=True)
	
	#ratings_by_caller(outbound, line, 'Prompt	/usr/local/freeswitch/scripts/AO/sounds/survey/guj/likert', ao_verygood)
	#ratings_by_caller(outbound, line, 'Prompt	/usr/local/freeswitch/scripts/AO/sounds/survey/guj/likert', ao_good)
	
	#approval_rate(line, ao_call, exp_start, exp_end)
	#approval_rate(line, ao_rec, exp_start, exp_end)
	#approval_rate(line, ao_rate, exp_start, exp_end)
	
	#stats_by_phone_num.get_calls_by_number(f,destnum=line.number)
	#num_calls.get_calls(f,destnum=line.number,date_start=start)
	#call_duration.get_call_durations(f,destnum=line.number,date_start=start)
	#pilot_participants = ['9909840770', '9979627746', '9428500603', '9979426355', '9898346338', '9879022537', '9924974308', '9904542967', '9979448854', '9723861596', '9979383300', '9824519045', '9925513986', '9825592055', '9978395789', '9978171766', '9909195611', '9427249402', '9429051838', '9824006909', '9904068359', '9974572646', '9725102377', '9428854035', '9724367143', '9925664025', '9898682517', '9904063407', '9727229188', '9925778755', '9428348425', '9825154390', '9228123644', '9904133985', '9998540911', '9913039299', '9974540063', '9712394006', '9818011346', '9198180113', '9909164849', '9810702847', '9723419830', '9427374736', '9909066119', '9825772077', '9601195509']
	#num_calls.get_calls(f,destnum=line.number,date_start=start,phone_num_filter=pilot_participants)

	#ratings(f, line, ao_verygood)
	#ratings(f, line, ao_good)
	
	# correlation between number of outbound and inbound
	#get_completed_bcasts(line.number, date_start=start)
	#num_calls.get_calls(f,date_start=start,daily_data=True)
	
	#answer_call_effect(f, line, date_start=start)
	
	#approval_rate(line, None, start, exp_start)
	
	#num_calls.get_listens_within_call(f, line.number, phone_num_filter=ao_call, date_start=exp_start, date_end=exp_end)
	#num_calls.get_listens_within_call(f, line.number, phone_num_filter=ao_rec, date_start=exp_start, date_end=exp_end)
	#num_calls.get_listens_within_call(f, line.number, phone_num_filter=ao_rate, date_start=exp_start, date_end=exp_end)
	
	#num_calls.get_lurking_and_posting(f, line.number, line.forums, phone_num_filter=ao_call)
	#num_calls.get_lurking_and_posting(f, line.number, line.forums,phone_num_filter=ao_rec)
	#num_calls.get_lurking_and_posting(f, line.number, line.forums,phone_num_filter=ao_rate)
	
	#num_calls.get_lurking_and_posting(f, line.number, line.forums, phone_num_filter=ao_call,date_start=exp_start, date_end=exp_end, transfer_calls=True)
	#topics(line, start)
	
main()