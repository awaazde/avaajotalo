import sys, os
from datetime import datetime, timedelta
from django.db.models import Min, Max
import num_calls, stats_by_phone_num
from otalo.surveys.models import Subject, Survey, Prompt, Call, Input
from otalo.AO.models import Line, Message_forum

# only start calling after free call bug fix
BANG_START = datetime(year=2011, month=3, day=9)
MOTIV_START = datetime(year=2011, month=3, day=3)
blacklist_nums = ['9596550654', '9173911854', '9726537942', '7940086740', '9893966806', '7554078142', '9755195845', '9824991658', '9662062754', '9428826158']
blacklist = Subject.objects.filter(number__in=blacklist_nums)

def print_digest(inbound_log, outbound_log, bang, motiv=None):
	now = datetime.now()
	today = datetime(year=now.year, month=now.month, day=now.day)
	oneday = timedelta(days=1)
	thisweek = today - timedelta(days=today.weekday())
	oneweek = timedelta(days=6)
	
	print("<html>")
	print("<div><h2>This week's experiment results</h3></div>")
	print("<div><h3>Experiment 1: Free Access vs. Free Contribution </h4></div>")
	print_bcast_table(inbound_log, outbound_log, bang, ['CALL', 'REC', 'RATE'], {'CALL':'guj/freecall', 'REC':'guj/recordmessage', 'RATE':'guj/likert'}, BANG_START)
	
	thisweeks_bcasts = Survey.objects.filter(broadcast=True, number__in=[bang.number, bang.outbound_number], call__date__gt=thisweek, call__date__lt=today+oneday).distinct()
	bcast_prompts = Prompt.objects.filter(survey__in=thisweeks_bcasts, order=3)
	bcast_prompt_files = [os.path.basename(pair.values()[0]) for pair in bcast_prompts.values('file')]
	unique_bcasts = Message_forum.objects.filter(message__content_file__in=bcast_prompt_files)
	all_bcasts = Survey.objects.filter(broadcast=True, number__in=[bang.number, bang.outbound_number], call__date__gt=BANG_START, call__date__lt=today+oneday).distinct()
	
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
		print_bcast_table(inbound_log, outbound_log, motiv, ['SELF', 'GROUP', 'NONE'], {'SELF':"hin/recordmessage", 'GROUP':"hin/recordmessage", 'NONE':"hin/recordmessage"}, MOTIV_START)
		
	
	print("</html>")

def print_bcast_table(inbound_log, outbound_log, line, conditions, manip_points, study_start):
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
		exp1_header += "<td width='300px'><u>"+str(bcast_msg)+"</u></td>"
	exp1_header += "<td width='300px'><u>Overall</u></td>"
	print(exp1_header)
	print("</tr>")
	
	call_tots = []
	for bcast_msg in unique_bcasts:
		bcast_calls = {}
		bcast_surveys = thisweeks_bcasts.filter(prompt__file__contains=bcast_msg.message.content_file)
		
		for condition in conditions:
			bcast_calls[condition+'_recipients'] = Call.objects.filter(survey__in=bcast_surveys, survey__name__contains='_'+condition+'_').exclude(subject__in=blacklist).values('subject').distinct().count()
			bcast_calls[condition+'_completed'] = Call.objects.filter(survey__in=bcast_surveys, survey__name__contains='_'+condition+'_', complete=True).exclude(subject__in=blacklist).values('subject').distinct().count()
			numbers = Subject.objects.filter(call__survey__in=bcast_surveys, call__survey__name__contains='_'+condition+'_').exclude(number__in=blacklist_nums).distinct().values('number')
			numbers = [pair.values()[0] for pair in numbers]
			# ASSUME: Broadcasts don't overlaop each other in time, so if a number got a bcast within 
			# the start and end window of this bcast, it was for this bcast only
			calls = Call.objects.filter(survey__in=bcast_surveys)
			firstcalldate = calls.aggregate(Min('date'))
			firstcalldate = firstcalldate.values()[0]
			lastcalldate = calls.aggregate(Max('date'))
			lastcalldate = lastcalldate.values()[0]
			listens = num_calls.get_calls(filename=outbound_log, destnum=line.number, log=manip_points[condition], phone_num_filter=numbers, date_start=firstcalldate, date_end=lastcalldate, quiet=True, transfer_calls=True)
			n_listens = 0
			for week in listens:
				n_listens += listens[week]
			bcast_calls[condition+'_listens'] = n_listens
			
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
						features_tot = 0
						for feature in call:
							if feature != 'order' and feature != 'feature_chosen' and feature != 'start' and feature != 'last':
								features_tot += call[feature]
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
		bcast_calls[condition+'_listens'] = 0

	for survey in all_bcasts:
		for condition in conditions:
			if '_'+condition+'_' in survey.name:
				bcast_calls[condition+'_recipients'] += Call.objects.filter(survey=survey).exclude(subject__in=blacklist).values('subject').distinct().count()
				bcast_calls[condition+'_completed'] += Call.objects.filter(survey=survey, complete=True).exclude(subject__in=blacklist).values('subject').distinct().count()
				
				numbers = Subject.objects.filter(call__survey=survey).exclude(number__in=blacklist_nums).distinct().values('number')
				numbers = [pair.values()[0] for pair in numbers]
				calls = Call.objects.filter(survey=survey)
				firstcalldate = calls.aggregate(Min('date'))
				firstcalldate = firstcalldate.values()[0]
				lastcalldate = calls.aggregate(Max('date'))
				lastcalldate = lastcalldate.values()[0]
					
				listens = num_calls.get_calls(filename=outbound_log, destnum=line.number, log=manip_points[condition], phone_num_filter=numbers, date_start=firstcalldate, date_end=lastcalldate, quiet=True, transfer_calls=True)
				n_listens = 0
				for week in listens:
					n_listens += listens[week]
				bcast_calls[condition+'_listens'] += n_listens
				
				if condition != 'CALL':
					bcast_calls[condition+'_behavior'] += Input.objects.filter(call__survey=survey, call__survey__name__contains='_'+condition+'_').exclude(call__subject__in=blacklist).distinct().count()
				else:
					# only count sessions that have at least one feature access
					n_one_plus_sessions = 0	    
					calls = num_calls.get_features_within_call(filename=inbound_log, destnum=str(line.number), phone_num_filter=numbers, date_start=firstcalldate, date_end=lastcalldate, quiet=True, transfer_calls=True)
					feature_calls = calls[calls.keys()[0]] if calls else {}
					features_hist = {}
					for call in feature_calls:
						features_tot = 0
						for feature in call:
							if feature != 'order' and feature != 'feature_chosen' and feature != 'start' and feature != 'last':
								features_tot += call[feature]
						if features_tot > 0:
							n_one_plus_sessions += 1
								
					bcast_calls[condition+'_behavior'] += n_one_plus_sessions
					
	call_tots.append(bcast_calls)
	
	for condition in conditions:
		print("<tr>")
		print("<td>"+condition+"</td>")
		for bcast in call_tots:
			print("<td>"+str(bcast[condition+'_recipients'])+" attempts; "+str(bcast[condition+'_completed'])+" pickups; "+str(bcast[condition+'_listens'])+" action prompts; "+str(bcast[condition+'_behavior'])+" actions</td>")
		print("</tr>")

	print("</table>")
	
	print("<div><h4>Inbound Calling</h4></div>")
	print("<table>")
	print("<tr>")
	print("<td width='100px'><u>Condition</u></td><td width='300px'><u>This week</u></td><td width='300px'><u>Total</u></td>")
	print("</tr>")
		
	for condition in conditions:
		print("<tr>")
		print("<td>"+condition+"</td>")
		subjects = Subject.objects.filter(call__survey__in=all_bcasts, call__survey__name__contains='_'+condition+'_').exclude(number__in=blacklist_nums).distinct()
		numbers = [subj.number for subj in subjects]
		calls = stats_by_phone_num.get_calls_by_number(filename=inbound_log, destnum=line.number, date_start=thisweek, quiet=True)
		n_unique = 0
		n_thisweek = 0
		for number, tot in calls:
			if number in numbers:
				n_unique += 1
				n_thisweek += tot
		transfer_posts = num_calls.get_recordings(filename=inbound_log, destnum=line.number, date_start=study_start, transfer_calls=True)
		
		posts = Message_forum.objects.filter(message__date__gte=thisweek, message__date__lt=today+oneday, forum__line=line, message__user__number__in=numbers)
		n_tot_posts = posts.count()
		posts = posts.exclude(message__content_file__in=transfer_posts)
		n_approved = posts.filter(status = Message_forum.STATUS_APPROVED).count()
		n_unique_posters = posts.values('message__user').distinct().count()
		print("<td>"+str(n_thisweek)+" calls by "+str(n_unique)+ " callers; "+str(posts.count())+" posts by "+str(n_unique_posters)+" posters ("+str(n_approved)+" approved, "+str(n_tot_posts)+" incl. free sessions)</td>")
		
		# Total
		calls = stats_by_phone_num.get_calls_by_number(filename=inbound_log, destnum=line.number, date_start=study_start, quiet=True)
		n_unique = 0
		n_total = 0
		for number, tot in calls:
			if number in numbers:
				n_unique += 1
				n_total += tot
		posts = Message_forum.objects.filter(message__date__gte=study_start, message__date__lt=today+oneday, forum__line=line, message__user__number__in=numbers)
		n_tot_posts = posts.count()
		posts = posts.exclude(message__content_file__in=transfer_posts)
		n_approved = posts.filter(status = Message_forum.STATUS_APPROVED).count()
		n_unique_posters = posts.values('message__user').distinct().count()
		print("<td>"+str(n_total)+" calls by "+str(n_unique)+" callers; "+str(posts.count())+" posts by "+str(n_unique_posters)+" posters ("+str(n_approved)+" approved, "+str(n_tot_posts)+" incl. free sessions)</td>")


		print("</tr>")
			
	print("</table>")

def subject_stats(inbound_log, bang, motiv):
	now = datetime.now()
	today = datetime(year=now.year, month=now.month, day=now.day)
	oneday = timedelta(days=1)

	print("Bang Experiment")
	bang_conditions = ['CALL', 'REC', 'RATE']
	all_bcasts = Survey.objects.filter(broadcast=True, number__in=[bang.number, bang.outbound_number], call__date__gt=BANG_START, call__date__lt=today+oneday).distinct()
	
	for condition in bang_conditions:
		print(condition)
		print("Number\tPickups\tActions")
		subjects = Subject.objects.filter(call__survey__in=all_bcasts, call__survey__name__contains=condition).exclude(number__in=blacklist_nums).distinct()
		
		for subj in subjects:
			calls = Call.objects.filter(subject=subj, survey__in=all_bcasts)
			n_completed = calls.filter(complete=True).count()
			firstcalldate = calls.aggregate(Min('date'))
			firstcalldate = firstcalldate.values()[0]
			lastcalldate = calls.aggregate(Max('date'))
			lastcalldate = lastcalldate.values()[0]
			
			if condition != 'CALL':
				n_actions = Input.objects.filter(call__subject=subj).count()
			else:
				n_actions = 0	    
				transfers = num_calls.get_features_within_call(filename=inbound_log, destnum=bang.number, phone_num_filter=[subj.number], date_start=firstcalldate, date_end=lastcalldate, quiet=True, transfer_calls=True)
				for date in transfers:
					feature_calls = transfers[date]
					features_hist = {}
					for call in feature_calls:
						features_tot = 0
						for feature in call:
							if feature != 'order' and feature != 'feature_chosen' and feature != 'start' and feature != 'last':
								features_tot += call[feature]
						if features_tot > 0:
							n_actions += 1
			print(subj.number+"\t"+str(n_completed)+"\t"+str(n_actions))
	
	print("Motiv Experiment")
	motiv_conditions = ['SELF', 'GROUP', 'NONE']
	all_bcasts = Survey.objects.filter(broadcast=True, number__in=[motiv.number, motiv.outbound_number], call__date__gt=MOTIV_START, call__date__lt=today+oneday).distinct()
	
	for condition in motiv_conditions:
		print(condition)
		print("Number\tPickups\tActions")
		subjects = Subject.objects.filter(call__survey__in=all_bcasts, call__survey__name__contains=condition).exclude(number__in=blacklist_nums).distinct()
		
		for subj in subjects:
			calls = Call.objects.filter(subject=subj, survey__in=all_bcasts)
			n_completed = calls.filter(complete=True).count()
			n_actions = Input.objects.filter(call__subject=subj).count()
			
			print(subj.number+"\t"+str(n_completed)+"\t"+str(n_actions))
	
def main():
	if len(sys.argv) < 3:
		print("Wrong")
	else:
		f = sys.argv[1]
		survey = sys.argv[2]
		bangid = sys.argv[3]
		bang = Line.objects.get(pk=int(bangid))	
		motiv = None
		if len(sys.argv) > 4:
			motivid = sys.argv[4]
			motiv = Line.objects.get(pk=int(motivid))
	
	print_digest(f, survey, bang, motiv)
	#subject_stats(f, bang, motiv)
    
main()
