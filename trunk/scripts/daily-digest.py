import sys
from datetime import datetime, timedelta
from django.db.models import Count
from django.conf import settings
import otalo_utils, num_calls, stats_by_phone_num, call_duration
from otalo.AO.models import Message, Message_forum, Line, User, Message_responder
from otalo.surveys.models import Survey, Call, Subject, Input
from otalo.AO.views import LISTEN_THRESH

def main():
	if len(sys.argv) < 1:
		print("Wrong")
	else:
		lineid = sys.argv[1]
		f = settings.INBOUND_LOG_ROOT + lineid + '.log'
	
	now = datetime.now()
	# reset to beginning of day
	today = datetime(year=now.year, month=now.month, day=now.day)
	oneday = timedelta(days=1)
	#today = today - oneday
	line = Line.objects.get(pk=int(lineid))
	
	print("<html>")
	print("<div> Below are basic usage statistics for " + str(line.name) + " over the last four days, starting with today. </div>")
	# calls
	print("<div><h4>Number of Incoming Calls</h4></div>")
	print("<table>")
	
	for i in range (0,4):
		calls = num_calls.get_calls(filename=f, destnum=str(line.number), date_start=today-oneday*i, date_end=today-oneday*(i-1), quiet=True)
		ncalls = calls[calls.keys()[0]] if calls else 0
		print("<tr>")
		print("<td width='100px'>"+otalo_utils.date_str(today-oneday*i)+"</td>")
		# since a single day's calls can only be bucketed into a single week
		print("<td>"+str(ncalls)+"</td>")
		print("</tr>")
	
	print("</table>")
	
	# calls by caller
	print("<div><h4>Who called today?</h4></div>")
	print("<table>")
	
	calls = stats_by_phone_num.get_calls_by_number(filename=f, destnum=str(line.number), date_start=today, date_end=today+oneday, quiet=True)
	for num, tot in calls:
		print("<tr>")
		print("<td width='100px'>"+num+"</td>")
		print("<td>"+str(tot)+"</td>")
		print("</tr>")
	
	print("</table>")
	
	# feature access
	print("<div><h4>Today's calls by number of feature accesses</h4></div>")
	print("<table>")

	calls = num_calls.get_features_within_call(filename=f, destnum=str(line.number), date_start=today, date_end=today+oneday, quiet=True)
	feature_calls = calls[calls.keys()[0]] if calls else {}
	features_hist = {}
	for call in feature_calls:
		features_tot = 0
		for feature in call:
			if feature != 'order' and feature != 'feature_chosen' and feature != 'start' and feature != 'last':
				features_tot += call[feature]
		if features_tot in features_hist:
			features_hist[features_tot] += 1 
		else: 
			features_hist[features_tot] = 1
	
	sorted_items = features_hist.items()
	sorted_items.sort()
	for accesses, ncalls in sorted_items:
		print("<tr>")
		print("<td width='80px'>"+str(accesses)+" accesses</td>")
		print("<td>"+str(ncalls)+"</td>")
		print("</tr>")
	
	print("</table>")
	
		
	# call duration
	durations = call_duration.get_call_durations(filename=f, destnum=str(line.number), date_start=today, date_end=today+oneday, quiet=True)
	durs_by_call = durations[durations.keys()[0]] if durations else {}
	durs = [dur[1].seconds for dur in durs_by_call] 
	
	avg_dur = str(sum(durs)/len(durs)) if durs else "n/a"
	
	print("<br/><div>")
	print("<b>Average call duration (secs):</b> ")
	print(avg_dur)
	print("</div>")
	
	# questions
	print("<div><h4>Number of Original Messages</h4></div>")
	print("<table>")
	
	for i in range (0,4):
		msgs = Message_forum.objects.filter(message__date__gte=today-oneday*i, message__date__lt=oneday+today-oneday*i, forum__line=line, message__lft=1)
		n_approved = msgs.filter(status = Message_forum.STATUS_APPROVED).count()
		print("<tr>")
		print("<td width='100px'>"+otalo_utils.date_str(today-oneday*i)+"</td>")
		# since a single day's calls can only be bucketed into a single week
		print("<td>"+str(msgs.count())+" (" + str(n_approved) + " approved) </td>")
		print("</tr>")
	
	print("</table>")
	
	# answers
	print("<div><h4>Number of Responses</h4></div>")
	print("<table>")
	
	for i in range (0,4):
		msgs = Message_forum.objects.filter(message__date__gte=today-oneday*i, message__date__lt=oneday+today-oneday*i, forum__line=line, message__lft__gt=1)
		n_approved = msgs.filter(status = Message_forum.STATUS_APPROVED).count()
		print("<tr>")
		print("<td width='100px'>"+otalo_utils.date_str(today-oneday*i)+"</td>")
		# since a single day's calls can only be bucketed into a single week
		print("<td>"+str(msgs.count())+" (" + str(n_approved) + " approved) </td>")
		print("</tr>")
	
	print("</table>")
	
	# answers by responder
	print("<div><h4>Number of Responses by Responder (last 7 days)</h4></div>")
	print("<table>")
	print("<tr>")
	print("<td width='100px'><u>Responder</u></td><td width='100px'><u>Assigned</u></td><td width='100px'><u>Responses</u></td>")
	print("</tr>")
	
	oneweek = timedelta(days=7)
	# get responders ordered by number of responses
	responders = User.objects.filter(forum__line=line).distinct()
	responder_counts = {}
	for responder in responders:
		# get active assignments only
		nassigned = Message_responder.objects.filter(user=responder, assign_date__gte=today-oneweek, passed_date__isnull=True, listens__lte=LISTEN_THRESH).count()		
		# count the answers whether they have been approved or not
		nresponses = Message_forum.objects.filter(message__date__gte=today-oneweek, message__user=responder, message__lft__gt=1).count()
		responder_counts[responder] = [nassigned, nresponses]
	
	# sort by number of responses
	responder_counts = sorted(responder_counts.iteritems(), key=lambda(k,v): v[1], reverse=True)	
		
	for responder,counts in responder_counts:
		print("<tr>")
		print("<td>"+responder.name+"</td>")
		print("<td>"+str(counts[0])+"</td>")
		print("<td>"+str(counts[1])+"</td>")
		print("</tr>")
	
	print("</table>")
	
	# Answer Calls
	answercalls = Call.objects.filter(survey__name__contains=Survey.ANSWER_CALL_DESIGNATOR, survey__number__in=[line.number, line.outbound_number], date__gte=today, date__lt=today+oneday)
	unique_answercalls = answercalls.values('subject', 'survey').distinct()
	n_recipients = 0
	n_completed = 0
	for answercall in unique_answercalls:
		if answercalls.filter(subject=answercall['subject'], survey=answercall['survey'], complete=True):
			n_recipients += 1
			n_completed += 1
		elif Call.objects.filter(subject=answercall['subject'], survey=answercall['survey'], complete=True).count() == 0:
			n_recipients += 1
	n_response_to_response = Input.objects.filter(call__in=answercalls).count()
	
	print("<br/><div>")
	print("<b>Response calls attempted:</b> ")
	print(n_recipients)
	print("<br/>")
	print("<b>Response calls matured:</b> ")
	print(n_completed)
	print("<br/>")
	print("<b>Responses to response:</b> ")
	print(n_response_to_response)
	print("</div>")
	
	print("<div><h4>Today's Broadcasts</h4></div>")
	print("<table>")
	print("<tr>")
	print("<td width='500px'><u>Broadcasts</u></td><td width='150px'><u>Recipients</u></td><td width='100px'><u>Matured</u></td>")
	print("</tr>")
	
	# Announcements
	actives = Survey.objects.filter(broadcast=True, number__in=[line.number, line.outbound_number], call__date__gt=today, call__date__lt=today+oneday).order_by('-id').distinct()
	
	# For each survey, get the number of subjects that are set to get a call today
	for survey in actives:
		subjects = Subject.objects.filter(call__survey=survey).distinct()
		n_subjects = 0
		calls_attempted = 0
		calls_completed = 0
		for subject in subjects:			
			calls = Call.objects.filter(subject=subject, survey=survey)
			calls_today = calls.filter(date__gte=today, date__lt=today+oneday)
			# check if this survey has been completed for this subj
			# ASSUMES that the same survey does not have multiple P1s
			# WHY? Because if we account for this then the ordering of P1s wrt P2s
			# matters. The consequence is that if a survey is reused, then these
			# numbers will underestimate the actual since it will not consider future P1s
			if bool(calls_today.filter(complete=True)):
				n_subjects += 1
				calls_completed += 1
				completed_today = calls_today.filter(complete=True)[0]
				tilldate = completed_today.date				
				calls_attempted += calls_today.filter(date__lte=tilldate).count()
			# if the call has not been completed at *any time*, add the call attempts for today
			elif calls.filter(complete=True).count() == 0:
				n_subjects += 1
				calls_attempted += calls_today.count()
		
		print("<tr>")
		print("<td>"+survey.name+"</td>")
		print("<td>"+str(n_subjects)+" (" + str(calls_attempted) +" attempts)</td>")
		print("<td>"+str(calls_completed)+"</td>")
		print("</tr>")
          	
                	
	print("</table>")
	
	print("</html>")

main()
