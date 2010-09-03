import sys
from datetime import datetime, timedelta
from django.db.models import Count
import otalo_utils, num_calls, stats_by_phone_num, call_duration
from otalo.AO.models import Message, Message_forum, Line, User, Message_responder
from otalo.AO.views import LISTEN_THRESH

def main():
	if len(sys.argv) < 2:
		print("Wrong")
	else:
		f = sys.argv[1]
		lineid = sys.argv[2]
	
	now = datetime.now()
	# reset to beginning of day
	today = datetime(year=now.year, month=now.month, day=now.day)
	#today = datetime(year=2010, month=1, day=15);
	oneday = timedelta(days=1)
	line = Line.objects.get(pk=int(lineid))
	
	print("<html>")
	print("<div> Below are basic usage statistics for " + str(line.name) + " over the last four days, starting with today. </div>")
	# calls
	print("<div><h4>Number of Calls</h4></div>")
	print("<table>")
	
	for i in range (0,4):
		calls = num_calls.get_calls(filename=f, destnum=str(line.number), date_filter=today-oneday*i, quiet=True)
		ncalls = calls[calls.keys()[0]] if calls else 0
		print("<tr>")
		print("<td width='60px'>"+otalo_utils.date_str(today-oneday*i)+"</td>")
		# since a single day's calls can only be bucketed into a single week
		print("<td>"+str(ncalls)+"</td>")
		print("</tr>")
	
	print("</table>")
	
	# calls by caller
	print("<div><h4>Who called today?</h4></div>")
	print("<table>")
	
	calls = stats_by_phone_num.get_calls_by_number(filename=f, destnum=str(line.number), date_start=today, date_end=today+oneday, quiet=True)
	calls_sorted = sorted(calls.iteritems(), key=lambda(k,v): (v,k))
	calls_sorted.reverse()
	for num, tot in calls_sorted:
		print("<tr>")
		print("<td width='100px'>"+num+"</td>")
		print("<td>"+str(tot)+"</td>")
		print("</tr>")
	
	print("</table>")
	
	# feature access
	print("<div><h4>Today's calls by number of feature accesses</h4></div>")
	print("<table>")

	calls = num_calls.get_features_within_call(filename=f, destnum=str(line.number), date_filter=today, quiet=True)
	feature_calls = calls[calls.keys()[0]] if calls else {}
	features_hist = {}
	for call in feature_calls:
		features_tot = call['q'] + call['a'] + call['r'] + call['e']
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
	durations = call_duration.get_call_durations(filename=f, destnum=str(line.number), date_filter=today, quiet=True)
	durs_by_call = durations[durations.keys()[0]] if durations else {}
	durs = [dur[1].seconds for dur in durs_by_call] 
	
	avg_dur = str(sum(durs)/len(durs)) if durs else "n/a"
	
	print("<br/><div>")
	print("<b>Average call duration (secs):</b> ")
	print(avg_dur)
	print("</div>")
	
	# questions
	print("<div><h4>Number of Questions</h4></div>")
	print("<table>")
	
	for i in range (0,4):
		ncalls = Message_forum.objects.filter(message__date__gte=today-oneday*i, message__date__lt=oneday+today-oneday*i, forum__line=line, message__lft=1).count()
		print("<tr>")
		print("<td width='60px'>"+otalo_utils.date_str(today-oneday*i)+"</td>")
		# since a single day's calls can only be bucketed into a single week
		print("<td>"+str(ncalls)+"</td>")
		print("</tr>")
	
	print("</table>")
	
	# answers
	print("<div><h4>Number of Answers</h4></div>")
	print("<table>")
	
	for i in range (0,4):
		ncalls = Message_forum.objects.filter(message__date__gte=today-oneday*i, message__date__lt=oneday+today-oneday*i, forum__line=line, message__lft__gt=1).count()
		print("<tr>")
		print("<td width='60px'>"+otalo_utils.date_str(today-oneday*i)+"</td>")
		# since a single day's calls can only be bucketed into a single week
		print("<td>"+str(ncalls)+"</td>")
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
	responders = User.objects.filter(forum__line=line, message__date__gte=today-oneweek, message__lft__gt=1).annotate(nresponses=Count('message')).order_by('-nresponses') | User.objects.filter(forum__line=line)
	
	for responder in responders:
		print("<tr>")
		print("<td>"+responder.name+"</td>")
		
		# get active assigments only
		nassigned = Message_responder.objects.filter(user=responder, assign_date__gte=today-oneweek, passed_date__isnull=True, listens__lte=LISTEN_THRESH).count()
		print("<td>"+str(nassigned)+"</td>")
		
		# count the answers whether they have been approved or not
		nresponses = Message_forum.objects.filter(message__date__gte=today-oneweek, message__user=responder, message__lft__gt=1).count()
		print("<td>"+str(nresponses)+"</td>")
		print("</tr>")
	
	print("</table>")
	
	print("</html>")

main()
