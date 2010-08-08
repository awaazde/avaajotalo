import sys
from datetime import datetime, timedelta
import otalo_utils, survey_stats
from otalo.surveys.models import Subject, Survey, Call

def main():
	if len(sys.argv) < 1:
		print("Wrong")
	else:
		f = sys.argv[1]
	
	now = datetime.now()
	# reset to beginning of day
	today = datetime(year=now.year, month=now.month, day=now.day)
	oneday = timedelta(days=1)
	
	print("<html>")
	print("<div> Below is today's experiment report. </div>")
	# num subjects
	nsubjects = Call.objects.values('subject').distinct().count()
	print("<br/><div>")
	print("<b>Number of subjects:</b> ")
	print(nsubjects)
	print("</div>")
	
	# num connected calls
	ncomplete = Call.objects.filter(date__gte=today, complete=1).count()
	print("<br/><div>")
	print("<b>Number of calls completed:</b> ")
	print(ncomplete)
	print("</div>")
	
	# num followups
	print("<div><h4>Followups by info source</h4></div>")
	print("<table>")

	followups = survey_stats.get_followups(filename=f, date_start=today, date_end=today+oneday, quiet=True)
	for source, ncalls in followups.items():
		print("<tr>")
		print("<td width='40px'>"+str(source)+"</td>")
		print("<td>"+str(ncalls)+"</td>")
		print("</tr>")
		
	
	# num followups
	print("<div><h4>Overall</h4></div>")
	print("<table>")

	exp_start = datetime(year=2010, month=7, day=31)
	followups = survey_stats.get_followups(filename=f, date_start=exp_start, quiet=True)
	for source, ncalls in followups.items():
		print("<tr>")
		print("<td width='40px'>"+str(source)+"</td>")
		print("<td>"+str(ncalls)+"</td>")
		print("</tr>")
	
	print("</table>")
	
	print("</html>")

main()
