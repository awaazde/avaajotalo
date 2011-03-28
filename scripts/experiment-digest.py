import sys, os
from datetime import datetime, timedelta
from django.db.models import Min, Max
import otalo_utils, num_calls
from otalo.surveys.models import Subject, Survey, Prompt, Call, Input
from otalo.AO.models import Line, Message_forum

# only start calling after free call bug fix
STUDY_START1 = datetime(year=2011, month=3, day=9)
STUDY_START2 = datetime(year=2011, month=3, day=3)
blacklist_nums = ['9596550654', '9173911854', '9726537942', '7940086740', '9893966806', '7554078142', '9755195845']
blacklist = Subject.objects.filter(number__in=blacklist_nums)

def print_digest(inbound_log, bang, motiv=None):
	now = datetime.now()
	today = datetime(year=now.year, month=now.month, day=now.day)
	oneday = timedelta(days=1)
	thisweek = today - timedelta(days=today.weekday())
	oneweek = timedelta(days=6)
	
	print("<html>")
	print("<div><h2>This week's experiment results</h3></div>")
	print("<div><h3>Experiment 1: Free Access vs. Free Contribution </h4></div>")
	print_bcast_table(inbound_log, bang, ['CALL', 'REC', 'RATE'], STUDY_START1)
	
	thisweeks_bcasts = Survey.objects.filter(broadcast=True, number__in=[bang.number, bang.outbound_number], call__date__gt=thisweek, call__date__lt=today+oneday).distinct()
	bcast_prompts = Prompt.objects.filter(survey__in=thisweeks_bcasts, order=3)
	bcast_prompt_files = [os.path.basename(pair.values()[0]) for pair in bcast_prompts.values('file')]
	unique_bcasts = Message_forum.objects.filter(message__content_file__in=bcast_prompt_files)
	all_bcasts = Survey.objects.filter(broadcast=True, number__in=[bang.number, bang.outbound_number], call__date__gt=STUDY_START1, call__date__lt=today+oneday).distinct()
	
	print("<div><h4>Rating Results</h4></div>")
	print("<table>")
	print("<tr>")
	exp1_header = "<td width='100px'><u>Condition</u></td>"
	for bcast_msg in unique_bcasts:
		exp1_header += "<td width='250px'><u>"+str(bcast_msg)+"</u></td>"
	exp1_header += "<td width='250px'><u>Overall</u></td>"
	print(exp1_header)
	print("</tr>")
	
	ratings = []
	for bcast_msg in unique_bcasts:
		rating = {}
		bcast_surveys = thisweeks_bcasts.filter(prompt__file__contains=bcast_msg.message.content_file)
		
		rating['verygood_vg'] = Input.objects.filter(call__survey__in=bcast_surveys, call__survey__name__contains='_verygood_', input="1").exclude(call__subject__in=blacklist).distinct().count()
		rating['verygood_gd'] = Input.objects.filter(call__survey__in=bcast_surveys, call__survey__name__contains='_verygood_', input="2").exclude(call__subject__in=blacklist).distinct().count()
		rating['verygood_ok'] = Input.objects.filter(call__survey__in=bcast_surveys, call__survey__name__contains='_verygood_', input="3").exclude(call__subject__in=blacklist).distinct().count()
		
		rating['goodbad_gd'] = Input.objects.filter(call__survey__in=bcast_surveys, call__survey__name__contains='_goodbad_', input="1").exclude(call__subject__in=blacklist).distinct().count()
		rating['goodbad_ok'] = Input.objects.filter(call__survey__in=bcast_surveys, call__survey__name__contains='_goodbad_', input="2").exclude(call__subject__in=blacklist).distinct().count()
		rating['goodbad_bd'] = Input.objects.filter(call__survey__in=bcast_surveys, call__survey__name__contains='_goodbad_', input="3").exclude(call__subject__in=blacklist).distinct().count()
		
		ratings.append(rating)
	
	# overall numbers
	rating = {}
	rating['verygood_vg'] = Input.objects.filter(call__survey__in=all_bcasts, call__survey__name__contains='_verygood_', input="1").exclude(call__subject__in=blacklist).distinct().count()
	rating['verygood_gd'] = Input.objects.filter(call__survey__in=all_bcasts, call__survey__name__contains='_verygood_', input="2").exclude(call__subject__in=blacklist).distinct().count()
	rating['verygood_ok'] = Input.objects.filter(call__survey__in=all_bcasts, call__survey__name__contains='_verygood_', input="3").exclude(call__subject__in=blacklist).distinct().count()
	
	rating['goodbad_gd'] = Input.objects.filter(call__survey__in=all_bcasts, call__survey__name__contains='_goodbad_', input="1").exclude(call__subject__in=blacklist).distinct().count()
	rating['goodbad_ok'] = Input.objects.filter(call__survey__in=all_bcasts, call__survey__name__contains='_goodbad_', input="2").exclude(call__subject__in=blacklist).distinct().count()
	rating['goodbad_bd'] = Input.objects.filter(call__survey__in=all_bcasts, call__survey__name__contains='_goodbad_', input="3").exclude(call__subject__in=blacklist).distinct().count()
	
	ratings.append(rating)
	
	print("<tr>")
	print("<td>VeryGood</td>")
	for rating in ratings:
		print("<td>"+str(rating['verygood_vg'])+" very good; "+str(rating['verygood_gd'])+" good; "+str(rating['verygood_ok'])+" ok</td>")
	print("</tr>")
	
	print("<tr>")
	print("<td>GoodBad</td>")
	for rating in ratings:
		print("<td>"+str(rating['goodbad_gd'])+" good; "+str(rating['goodbad_ok'])+" ok; "+str(rating['goodbad_bd'])+" bad</td>")
	print("</tr>")
	
	print("</table>")
	
	if motiv:
		print("<div><h3>Experiment 2: Self vs. Group Motivation </h4></div>")
		print_bcast_table(inbound_log, motiv, ['SELF', 'GROUP', 'NONE'], STUDY_START2)
		
	
	print("</html>")

def print_bcast_table(inbound_log, line, conditions, study_start):
	now = datetime.now()
	today = datetime(year=now.year, month=now.month, day=now.day)
	oneday = timedelta(days=1)
	thisweek = today - timedelta(days=today.weekday())
	oneweek = timedelta(days=6)
	
	print("<div><h4>This week's broadcasts</h4></div>")
	print("<table>")
	print("<tr>")
	
	thisweeks_bcasts = Survey.objects.filter(broadcast=True, number__in=[line.number, line.outbound_number], call__date__gt=thisweek, call__date__lt=today+oneday).distinct()
	bcast_prompts = Prompt.objects.filter(survey__in=thisweeks_bcasts, order=3)
	bcast_prompt_files = [os.path.basename(pair.values()[0]) for pair in bcast_prompts.values('file')]
	unique_bcasts = Message_forum.objects.filter(message__content_file__in=bcast_prompt_files)
	all_bcasts = Survey.objects.filter(broadcast=True, number__in=[line.number, line.outbound_number], call__date__gt=study_start, call__date__lt=today+oneday).distinct()
	
	exp1_header = "<td width='100px'><u>Condition</u></td>"
	for bcast_msg in unique_bcasts:
		exp1_header += "<td width='250px'><u>"+str(bcast_msg)+"</u></td>"
	exp1_header += "<td width='250px'><u>Overall</u></td>"
	print(exp1_header)
	print("</tr>")
	
	call_tots = []
	for bcast_msg in unique_bcasts:
		bcast_calls = {}
		bcast_surveys = thisweeks_bcasts.filter(prompt__file__contains=bcast_msg.message.content_file)
		
		for condition in conditions:
			bcast_calls[condition+'_recipients'] = Call.objects.filter(survey__in=bcast_surveys, survey__name__contains='_'+condition+'_').exclude(subject__in=blacklist).values('subject').distinct().count()
			bcast_calls[condition+'_completed'] = Call.objects.filter(survey__in=bcast_surveys, survey__name__contains='_'+condition+'_', complete=True).exclude(subject__in=blacklist).values('subject').distinct().count()
			
			if condition != 'CALL':
				bcast_calls[condition+'_behavior'] = Input.objects.filter(call__survey__in=bcast_surveys, call__survey__name__contains='_'+condition+'_').exclude(call__subject__in=blacklist).distinct().count()			
			else:
				# only count sessions that have at least one feature access
				n_one_plus_sessions = 0
				for survey in bcast_surveys:
					numbers = Subject.objects.filter(call__survey=survey).exclude(number__in=blacklist_nums).distinct().values('number')
					numbers = [pair.values()[0] for pair in numbers]
					calls = Call.objects.filter(survey=survey)
					firstcalldate = calls.aggregate(Min('date'))
					firstcalldate = firstcalldate.values()[0]
					lastcalldate = calls.aggregate(Max('date'))
					lastcalldate = lastcalldate.values()[0]
				    
					calls = num_calls.get_features_within_call(filename=inbound_log, destnum=str(line.number), phone_num_filter=numbers, date_start=firstcalldate, date_end=lastcalldate, quiet=True, transfer_calls=True)
					feature_calls = calls[calls.keys()[0]] if calls else {}
					features_hist = {}
					for call in feature_calls:
						features_tot = call['q'] + call['a'] + call['r'] + call['e']
						if features_tot > 0:
							n_one_plus_sessions += 1
							
				bcast_calls[condition+'_behavior'] = n_one_plus_sessions
				
		call_tots.append(bcast_calls)
	
	# overall numbers
	bcast_calls = {}
	for condition in conditions:
		bcast_calls[condition+'_recipients'] = 0
		bcast_calls[condition+'_completed'] = 0
		bcast_calls[condition+'_behavior'] = 0

	for survey in all_bcasts:
		for condition in conditions:
			if '_'+condition+'_' in survey.name:
				bcast_calls[condition+'_recipients'] += Call.objects.filter(survey=survey).exclude(subject__in=blacklist).values('subject').distinct().count()
				bcast_calls[condition+'_completed'] += Call.objects.filter(survey=survey, complete=True).exclude(subject__in=blacklist).values('subject').distinct().count()
				if condition != 'CALL':
					bcast_calls[condition+'_behavior'] += Input.objects.filter(call__survey=survey, call__survey__name__contains='_'+condition+'_').exclude(call__subject__in=blacklist).distinct().count()
				else:
					# only count sessions that have at least one feature access
					n_one_plus_sessions = 0
					numbers = Subject.objects.filter(call__survey=survey).exclude(number__in=blacklist_nums).distinct().values('number')
					numbers = [pair.values()[0] for pair in numbers]
					calls = Call.objects.filter(survey=survey)
					firstcalldate = calls.aggregate(Min('date'))
					firstcalldate = firstcalldate.values()[0]
					lastcalldate = calls.aggregate(Max('date'))
					lastcalldate = lastcalldate.values()[0]
				    
					calls = num_calls.get_features_within_call(filename=inbound_log, destnum=str(line.number), phone_num_filter=numbers, date_start=firstcalldate, date_end=lastcalldate, quiet=True, transfer_calls=True)
					feature_calls = calls[calls.keys()[0]] if calls else {}
					features_hist = {}
					for call in feature_calls:
						features_tot = call['q'] + call['a'] + call['r'] + call['e']
						if features_tot > 0:
							n_one_plus_sessions += 1
								
					bcast_calls[condition+'_behavior'] += n_one_plus_sessions
					
	call_tots.append(bcast_calls)
	
	for condition in conditions:
		print("<tr>")
		print("<td>"+condition+"</td>")
		for bcast in call_tots:
			print("<td>"+str(bcast[condition+'_completed'])+" of "+str(bcast[condition+'_recipients'])+" completed; "+str(bcast[condition+'_behavior'])+" actions</td>")
		print("</tr>")

	print("</table>")
	
	print("<div><h4>Inbound Calling</h4></div>")
	print("<table>")
	print("<tr>")
	print("<td width='100px'><u>Condition</u></td><td width='250px'><u>This week</u></td><td width='250px'><u>Total</u></td>")
	print("</tr>")
		
	for condition in conditions:
		print("<tr>")
		print("<td>"+condition+"</td>")
		subjects = Subject.objects.filter(call__survey__in=thisweeks_bcasts, call__survey__name__contains='_'+condition+'_').exclude(number__in=blacklist_nums).distinct()
		numbers = [subj.number for subj in subjects]
		calls = num_calls.get_calls(filename=inbound_log, destnum=str(line.number), phone_num_filter=numbers, date_start=thisweek, quiet=True)
		n_thisweek = calls[calls.keys()[0]] if calls else 0
		posts = Message_forum.objects.filter(message__date__gte=thisweek, message__date__lt=today+oneday, forum__line=line, message__user__number__in=numbers)
		n_approved = posts.filter(status = Message_forum.STATUS_APPROVED).count()
		print("<td>"+str(n_thisweek)+" calls; "+str(posts.count())+" posts ("+str(n_approved)+" approved)</td>")
		
		# Total
		calls = num_calls.get_calls(filename=inbound_log, destnum=str(line.number), phone_num_filter=numbers, date_start=study_start, quiet=True)
		n_total = calls[calls.keys()[0]] if calls else 0
		posts = Message_forum.objects.filter(message__date__gte=study_start, message__date__lt=today+oneday, forum__line=line, message__user__number__in=numbers)
		n_approved = posts.filter(status = Message_forum.STATUS_APPROVED).count()
		print("<td>"+str(n_total)+" calls; "+str(posts.count())+" posts ("+str(n_approved)+" approved)</td>")


		print("</tr>")
			
	print("</table>")

def main():
	if len(sys.argv) < 3:
		print("Wrong")
	else:
		f = sys.argv[1]
		bangid = sys.argv[2]
		bang = Line.objects.get(pk=int(bangid))	
		motiv = None
		if len(sys.argv) > 3:
			motivid = sys.argv[3]
			motiv = Line.objects.get(pk=int(motivid))
	
	print_digest(f, bang, motiv)
    
main()
