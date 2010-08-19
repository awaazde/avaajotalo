import sys
from datetime import datetime, timedelta
import otalo_utils, survey_stats
from otalo.surveys.models import Subject, Survey, Call

def print_digest(f, date):
	oneday = timedelta(days=1)
	
	print("<html>")
	print("<div> Below is today's experiment report. </div>")
	# num subjects
	nsubjects = Call.objects.filter(date__gte=date).values('subject').distinct().count()
	print("<br/><div>")
	print("<b>Number of subjects:</b> ")
	print(nsubjects)
	print("</div>")
	
	# num connected calls
	ncomplete = Call.objects.filter(date__gte=date, complete=1).count()
	print("<br/><div>")
	print("<b>Number of calls completed:</b> ")
	print(ncomplete)
	print("</div>")
	
	# num followups
	print("<div><h4>Followups by info source (with phone numbers)</h4></div>")
	print("<table>")

	followups = survey_stats.get_followups(filename=f, date_start=date, date_end=date+oneday, quiet=True)
	for source, calllst in followups.items():
		print("<tr>")
		print("<td width='40px'>"+str(source)+"</td>")
		print("<td>"+str(len(calllst))+"</td>")
		print("<td>"+str(calllst)+"</td>")
		print("</tr>")
		
	
	# num followups
	print("<div><h4>Overall</h4></div>")
	print("<table>")

	exp_start = datetime(year=2010, month=7, day=31)
	followups = survey_stats.get_followups(filename=f, date_start=exp_start, quiet=True)
	for source, calllst in followups.items():
		print("<tr>")
		print("<td width='40px'>"+str(source)+"</td>")
		print("<td>"+str(len(calllst))+"</td>")
		print("</tr>")
	
	print("</table>")
	
	print("</html>")

def main():
	if len(sys.argv) < 2:
		print("Wrong")
	else:
		f = sys.argv[1]
		if len(sys.argv) > 2:
			datestr = sys.argv[2]
			date = datetime.strptime(datestr, '%m-%d-%Y')
		else:
			now = datetime.now()
			date = datetime(year=now.year, month=now.month, day=now.day)
	print_digest(f, date)
    
main()
