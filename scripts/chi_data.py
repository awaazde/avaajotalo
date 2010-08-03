import sys
from datetime import datetime
import otalo
import num_calls
import stats_by_phone_num
import call_duration
import content
import time_of_day

def content_stats(f):
	content.get_content_type_by_time(f, log="Question")
	content.get_content_type_by_time(f, log="Answer")
	
	content.get_type_by_number(f, log="answer")
		
	content.get_content_type_by_time(f, log="Moderation")
	
	#categorization breakdown
	print('\nCategorization breakdown')
	content.get_categories(f)
	
	# number of people who left contact info
	content.get_identified_qs_by_time(f)
	
	#number of mods by number
	content.get_type_by_number(f, log="moderation")

def pilot_stats(f):
	num_calls.get_calls(f)
	num_calls.get_calls(f, log="QuestionWhat : enter")
	num_calls.get_calls(f, log="Radio: enter")
	num_calls.get_calls(f, log="Announcements: enter")
	
	call_duration.get_call_durations(f)
	
	stats_by_phone_num.get_calls_by_number(f)


def weekly_stats(f):
	time_of_day.num_calls_within_week(f)
	time_of_day.num_calls_within_week(f, log="QuestionWhat : enter")
	time_of_day.num_calls_within_week(f, log="Radio: enter")
	time_of_day.num_calls_within_week(f, log="Announcements: enter")
	
def forum_stats(f):
	stats_by_phone_num.get_calls_by_number(f, log="QuestionWhat : enter")
	
	qa_accesses = stats_by_phone_num.get_calls_by_number(f, log="QuestionWhat : enter", quiet=True)
	records = stats_by_phone_num.get_calls_by_number(f, log="RecordQuestion: enter")
	hangups = stats_by_phone_num.get_calls_by_number(f, log="Question What: HANG UP", quiet=True)
	
	calls_sorted = sorted(qa_accesses.iteritems(), key=lambda(k,v): (v,k))
	calls_sorted.reverse()
	
	forum_accesses = {}
	
	tot_accesses = 0
	print("\nNumber of Forum accesses, by phone number:")
	for num, qa in calls_sorted:
		recs = records[num] if num in records else 0
		hu = hangups[num] if num in hangups else 0
		tot_accesses += qa-recs-hu
		forum_accesses[num] = qa-recs-hu

		print(num + ': ' + str(qa-recs-hu))

	print("total is " + str(tot_accesses))

	listens = stats_by_phone_num.get_calls_by_number(f, log="Caller is listening to", quiet=True)
	tot_listens = 0
	print('\nAverage number of listens per forum visit, by phone number')
	for num, visits in calls_sorted:
		l = listens[num] if num in listens else 0
		tot_listens += l
		print(num + ': ' + str(float(l)/float(visits)))

	print('Overall Average: ' + str(float(tot_listens)/float(tot_accesses)))

def stats_by_feature(f):
	qa = num_calls.get_calls(f, log="QuestionWhat : enter", quiet = True)
	radio = num_calls.get_calls(f, log="Radio: enter", quiet=True)
	ann = num_calls.get_calls(f, log="Announcements: enter", quiet=True)
	
	dates = qa.keys()
	dates.sort()
	
	tot = {}
	for date in dates:
		tot[date] = qa[date] + radio[date] + ann[date]
	
	print('\nQ&A forum accesses')
	for date in dates:
		d = tot[date]
		n = qa[date]
		
		print(otalo.date_str(date) + ': ' + str(n))
		
	print('\nRadio accesses as a percent of total calls')
	for date in dates:
		d = tot[date]
		n = radio[date]

		print(otalo.date_str(date) + ': ' + str(n))
		
	print('\nAnnouncement accesses as a percent of total calls')
	for date in dates:
		d = tot[date]
		n = ann[date]

		#print(otalo.date_str(date) + ': ' + str(float(n)/float(d)))
		print(otalo.date_str(date) + ': ' + str(n))

def call_splits(f):
	calls_by_num = stats_by_phone_num.get_calls_by_number(f, quiet=True)
	calls_sorted = sorted(calls_by_num.iteritems(), key=lambda(k,v): (v,k))
	calls_sorted.reverse()
	
	ten_or_more = []
	for num, tot in calls_sorted:
		if tot >= 10:
			ten_or_more.append(num)
	
	halfway = datetime.strptime('2009-04-15',"%Y-%m-%d")
	
	calls_h1 = {}
	calls_h2 = {}
	for num in ten_or_more:
		calls_h1[num] = 0
		calls_h2[num] = 0
		print("getting splits for " + num)
		c = num_calls.get_calls(f, phone_num_filter=[num], quiet=True)
		for date, tot in c.iteritems():
			if date < halfway:
				calls_h1[num] += tot
			else:
				calls_h2[num] += tot
	
	print('\nTotal calls in Half 1')
	for num, tot in calls_h1.iteritems():
		print(num + ': ' + str(tot))
		
	print('\nTotal calls in Half 2')
	for num, tot in calls_h2.iteritems():
		print(num + ': ' + str(tot))

def error_stats(f, trans=False):
	#call duration
	#call_duration.get_call_durations(f)
	
	#no match and no input errros over time as a percent of total calls
	input_errors(f)
	
	#re-records over time as a percent of total calls
	#re_records(f)
	
	#early hangups
	#early_hangups(f)
	
	#errors by phone number (ordered by number of calls)
	#input_errors_by_num(f)
	
	#re-records by phone number (ordered by number of calls)
	#re_records_by_num(f)
	
	#error splits for all callers more than 10
	#calls_by_num = stats_by_phone_num.get_calls_by_number(f, quiet=True)
	#calls_sorted = sorted(calls_by_num.iteritems(), key=lambda(k,v): (v,k))
	#calls_sorted.reverse()
	
	ten_or_more = []
	for num, tot in calls_sorted:
		if tot >= 10:
			ten_or_more.append(num)
	
	#splits ordered by heaviest access
	#error_splits_by_num(f, ten_or_more)

def error_splits_by_num(f, nums):
	splits_by_num = {}
	nm_splits_by_num = {}
	
	for num in nums:
		print('getting splits for ' + num)
		#splits = error_halves(f, num)
		nm_splits = no_match_splits(f, num)
		#splits_by_num[num] = splits
		nm_splits_by_num[num] = nm_splits
	
	print("\nHalf 1 no match rates by number")
	for num, splits in nm_splits_by_num.iteritems():
		print(num + ': ' + splits[0])
	
	print("\nHalf 2 no match rates by number")
	for num, splits in nm_splits_by_num.iteritems():
		print(num + ': ' + splits[1])
		
	#print("\nHalf 1 no input rates by number")
	#for num, splits in splits_by_num.iteritems():
	#	print(num + ': ' + splits[0])
		
	#print("\nHalf 2 no input rates by number")
	#for num, splits in splits_by_num.iteritems():
	#	print(num + ': ' + splits[1])
		
	#print("\nHalf 1 re-record rates by number")
	#for num, splits in splits_by_num.iteritems():
	#	print(num + ': ' + splits[2])
		
	#print("\nHalf 2 re-record rates by number")
	#for num, splits in splits_by_num.iteritems():
	#	print(num + ': ' + splits[3])
	
	#print("\nHalf 1 early hangup rates by number")
	#for num, splits in splits_by_num.iteritems():
	#	print(num + ': ' + splits[4])
		
	#print("\nHalf 2 early hangup rates by number")
	#for num, splits in splits_by_num.iteritems():
	#	print(num + ': ' + splits[5])	

def early_hangups(f):
	total_calls = num_calls.get_calls(f, quiet=True)
	early_hangups = num_calls.get_calls(f, log="Main Menu: HANG UP", quiet=True)
	
	dates = total_calls.keys()
	dates.sort()
	
	print("\nEarly hangups as a percentage of calls")
	for date in dates:
		tot = total_calls[date]
		ehs = early_hangups[date]
		
		print(otalo.date_str(date) + ": " + str(float(ehs)/float(tot)))

def re_records_by_num(f):
	total_calls = stats_by_phone_num.get_calls_by_number(f, quiet=True) 
	calls_sorted = sorted(total_calls.iteritems(), key=lambda(k,v): (v,k))
	calls_sorted.reverse()
	re_records = stats_by_phone_num.get_calls_by_number(f, log="RecordQuestionAgain", quiet=True)
	print("\nRe-records by phone num")
	for num, tot in calls_sorted:
		rr = re_records[num] if num in re_records else 0

		print(num + ': ' + str(float(rr)/float(tot)))
		
def input_errors_by_num(f):
	total_calls = stats_by_phone_num.get_calls_by_number(f, quiet=True) 
	calls_sorted = sorted(total_calls.iteritems(), key=lambda(k,v): (v,k))
	calls_sorted.reverse()
	no_match = stats_by_phone_num.get_calls_by_number(f, log="no match", quiet=True)
	nomatch = stats_by_phone_num.get_calls_by_number(f, log="nomatch", quiet=True)
	no_input = stats_by_phone_num.get_calls_by_number(f, log="no input", quiet=True)
	noinput = stats_by_phone_num.get_calls_by_number(f, log="noinput", quiet=True)
	
	print("\nNo match by phone num")
	for num, tot in calls_sorted:
		nm1 = no_match[num] if num in no_match else 0
		nm2 = nomatch[num] if num in nomatch else 0

		print(num + ': ' + str(float(nm1 + nm2)/float(tot)))

	print("\nNo input by phone num")
	for num, tot in calls_sorted:
		ni1 = no_input[num] if num in no_input else 0
		ni2 = noinput[num] if num in noinput else 0

		print(num + ': ' + str(float(ni1 + ni2)/float(tot)))

def no_match_splits(f, num):
	total_voice_calls = num_calls.get_calls(f, log = "Input mode: Voice", phone_num_filter=[num], quiet = True) 
	no_match = num_calls.get_calls(f, log="no match", phone_num_filter=[num], quiet = True)
	nomatch = num_calls.get_calls(f, log="nomatch", phone_num_filter=[num], quiet = True)
	
	halfway = datetime.strptime('2009-04-15',"%Y-%m-%d")
	
	dates = total_voice_calls.keys()
	dates.sort()

	half1_tot = .00001
	half2_tot = .00001

	half1_nm = 0
	half2_nm = 0
	
	for date in dates:
		tot = total_voice_calls[date]
		nm1 = no_match[date] if date in no_match else 0
		nm2 = nomatch[date] if date in nomatch else 0

		if date < halfway:
			half1_tot += tot
			half1_nm += nm1 + nm2
		else:
			half2_tot += tot
			half2_nm += nm1 + nm2	
	
	h1 = str(float(half1_nm)/float(half1_tot) ) if half1_tot > 1 else 'N/A'
	h2 = str(float(half2_nm)/float(half2_tot) ) if half2_tot > 1 else 'N/A'
		
	return [h1, h2]
	
def error_halves(f, num):
	total_calls = num_calls.get_calls(f, phone_num_filter=[num], quiet = True) 	
	no_input = num_calls.get_calls(f, log="no inpu", phone_num_filter=[num], quiet = True)
	noinput = num_calls.get_calls(f, log="noinput", phone_num_filter=[num], quiet = True)
	
	re_records = num_calls.get_calls(f, log="RecordQuestionAgain", phone_num_filter=[num], quiet=True)
	
	early_hangups = num_calls.get_calls(f, log="Main Menu: HANG UP", phone_num_filter=[num], quiet=True)
	
	halfway = datetime.strptime('2009-04-15',"%Y-%m-%d")

	dates = total_calls.keys()
	dates.sort()
	
	half1_tot = .00001
	half2_tot = .00001
	
	half1_ni = 0
	half2_ni = 0
	
	half1_rr = 0
	half2_rr = 0
	
	half1_eh = 0
	half2_eh = 0
	
	for date in dates:
		tot = total_calls[date]
		
		ni1 = no_input[date] if date in no_input else 0
		ni2 = noinput[date] if date in noinput else 0
		
		rrs = re_records[date] if date in re_records else 0
		
		ehs = early_hangups[date] if date in early_hangups else 0

		if date < halfway:
			half1_tot += tot
			half1_ni += ni1 + ni2
			half1_rr += rrs
			half1_eh += ehs
		else:
			half2_tot += tot
			half2_ni += ni1 + ni2
			half2_rr += rrs
			half2_eh += ehs

	
	return [str(float(half1_ni)/float(half1_tot) ), str(float(half2_ni)/float(half2_tot) ), str(float(half1_rr)/float(half1_tot) ), str(float(half2_rr)/float(half2_tot) ) , str(float(half1_eh)/float(half1_tot) ), str(float(half2_eh)/float(half2_tot) )]


def input_errors(f):
	total_calls = num_calls.get_calls(f, quiet=True)
	no_match = num_calls.get_calls(f, log="no match", quiet=True)
	nomatch = num_calls.get_calls(f, log="nomatch", quiet=True)
	no_input = num_calls.get_calls(f, log="no input", quiet=True)
	noinput = num_calls.get_calls(f, log="noinput", quiet=True)

	dates = total_calls.keys()
	dates.sort()

	print("\nNo match per call by week")
	for date in dates:
		tot = total_calls[date]
		nm1 = no_match[date] if date in no_match else 0
		nm2 = nomatch[date] if date in nomatch else 0

		print(otalo.date_str(date) + ': ' + str(float(nm1 + nm2)/float(tot)))

	print("\nNo input per call by week")
	for date in dates:
		tot = total_calls[date]
		ni1 = no_input[date] if date in no_input else 0
		ni2 = noinput[date] if date in noinput else 0
			
		print(otalo.date_str(date) + ': ' + str(float(ni1 + ni2)/float(tot)))
		
def re_records(f):	
	total_calls = num_calls.get_calls(f, quiet=True)
	re_records = num_calls.get_calls(f, log="RecordQuestionAgain", quiet=True)
	
	dates = total_calls.keys()
	dates.sort()
	
	print("\nRe-records per call by week")
	for date in dates:
		tot = total_calls[date]
		rr = re_records[date] if date in re_records else 0
				
		print(otalo.date_str(date) + ': ' + str(float(rr)/float(tot)))
		

def input_mode_stats(f):
	#number of each over time
	num_calls.get_calls(f, log="Input mode: DTMF")
	num_calls.get_calls(f, log="Input mode: Voice")

	#get number of callers with 10+ calls
	calls_by_num = stats_by_phone_num.get_calls_by_number(f, quiet=True)
	calls_sorted = sorted(calls_by_num.iteritems(), key=lambda(k,v): (v,k))
	calls_sorted.reverse()
	ten_or_more = []
	for num, tot in calls_sorted:
		if tot >= 10:
			ten_or_more.append(num)
	
	#find out how many of them used voice 33% of the time or more
	percent_voice_by_number(f, ten_or_more)
	
		

def voice_freqs_halves(f, num, quiet=False):
	dtmf_calls = num_calls.get_calls(f, log="Input mode: DTMF", phone_num_filter=[num], quiet = True)
	voice_calls = num_calls.get_calls(f, log="Input mode: Voice", phone_num_filter=[num], quiet = True)
	halfway = datetime.strptime('2009-04-15',"%Y-%m-%d")
	
	dates = dtmf_calls.keys()
	dates.sort()
	half1_dtmf = .001
	half1_voice = 0
	
	half2_dtmf = .001
	half2_voice = 0
	
	for date in dates:
		num_dtmf = dtmf_calls[date] if date in dtmf_calls else 0
		num_voice = voice_calls[date] if date in voice_calls else 0
		
		if date < halfway:
			half1_dtmf += num_dtmf
			half1_voice += num_voice
		else:
			half2_dtmf += num_dtmf
			half2_voice += num_voice
	
	if not quiet:
		print("\nProportion of voice calls for " + num + ":")
		print ("Half 1: " + str(float(half1_voice)/float(half1_dtmf + half1_voice) ) + "\t(dtmf=" + str(half1_dtmf) + ", voice=" + str(half1_voice) +")")
		print ("Half 2: " + str(float(half2_voice)/float(half2_dtmf + half2_voice) ) + "\t(dtmf=" + str(half2_dtmf) + ", voice=" + str(half2_voice) +")")
	
	h1 = str(float(half1_voice)/float(half1_dtmf + half1_voice) ) if half1_dtmf + half1_voice > 1 else 'N/A'
	h2 = str(float(half2_voice)/float(half2_dtmf + half2_voice) ) if half2_dtmf + half2_voice > 1 else 'N/A'
	return [h1, h2 ]
	
def percent_voice_by_number(f, nums):
	dtmf_calls = stats_by_phone_num.get_calls_by_number(f, log="Input mode: DTMF", quiet = True)
	voice_calls = stats_by_phone_num.get_calls_by_number(f, log="Input mode: Voice", quiet = True)

	print("Percent of voice calls, by number:")

	for num in nums:
		num_dtmf = dtmf_calls[num] if num in dtmf_calls else .00001
		num_voice = voice_calls[num] if num in voice_calls else 0
		prop_voice = float(num_voice) / float(num_dtmf + num_voice)
		
		print (num + ": " + str(prop_voice) + "\t(dtmf=" + str(num_dtmf) + ", voice=" + str(num_voice) +")")
		
def main():
	if len(sys.argv) < 2:
		print("Wrong")
	else:
		f = sys.argv[1]
		trans = 0
		if len(sys.argv) == 3:
			trans = sys.argv[2]
	
	#error_stats(f)
	#stats_by_feature(f)
	#forum_stats(f)
	#call_splits(f)
	#weekly_stats(f)
	#pilot_stats(f)
	#content_stats(f)
	input_mode_stats(f)

main()