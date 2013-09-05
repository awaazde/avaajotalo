import otalo_utils
import sys
from datetime import datetime, timedelta
from otalo.surveys.models import Subject, Call

SOURCES = ["E1", "E2", "P1", "P2"]
GROUPS = [["REMINDER_DUMMY","E1","E2","P1","P2","E1","P1","E2","P2"], ["REMINDER_DUMMY","E2","E1","P2","P1","E2","P2","E1","P1"], ["REMINDER_DUMMY","P1","P2","E1","E2","P1","E1","P2","E2"], ["REMINDER_DUMMY","P2","P1","E2","E1","P2","E2","P1","E1"]]

def get_followups(filename, destnum=False, prompt_filter=False, phone_num_filter=0, date_start=False, date_end=False, quiet=False):
	calls = {}
	calls_by_caller = {}
	current_week_start = 0
	total = 0
	
	f = open(filename)
	
	while(True):
		line = f.readline()
		if not line:
			break
		try:
		
		#################################################
		## Use the calls here to determine what pieces
		## of data must exist for the line to be valid.
		## All of those below should probably always be.
		
			phone_num = otalo_utils.get_phone_num(line)
			current_date = otalo_utils.get_date(line)
			dest = otalo_utils.get_destination(line)			
		##
		################################################
			#print(phone_num + ': dest = ' + dest)
			
			if phone_num_filter and not phone_num in phone_num_filter:
				continue
			
			if date_start:
				if date_end:
					 if not (current_date >= date_start and current_date < date_end):
						continue
				else:
					if not current_date >= date_start:
						continue

			if destnum and destnum.find(dest) == -1:
				continue

			if not phone_num in calls_by_caller:
				calls_by_caller[phone_num] = []
			
			if otalo_utils.is_prompt(line):
				prompt = otalo_utils.get_prompt(line)
				if (not prompt_filter) or prompt.find(prompt_filter) != -1:
					for source in SOURCES:
						# don't count duplicate accesses by the same caller
						if prompt.find(source) != -1 and not prompt in calls_by_caller[phone_num]:
							if source in calls:
								calls[source].append(phone_num)
							else:
								calls[source] = [phone_num]
							calls_by_caller[phone_num].append(prompt)
					
					
		except ValueError as err:
			#print("ValueError: " + line)
			continue
		except IndexError as err:
			#print("IndexError: " + line)
			continue
		except otalo_utils.PhoneNumException:
			#print("PhoneNumException: " + line)
			continue
	
	if not quiet:
		if phone_num_filter:
			print("Data for phone numbers: " + str(phone_num_filter))

		print("Number of followups, by source:")
		sources = calls.keys()
		for source in sources:
			total += len(calls[source])
			print(source +": "+str(len(calls[source])))

		print("total is " + str(total))
	
	return calls
    
def get_followups_by_number(filename, destnum=False, phone_num_filter=0, date_start=False, date_end=False, quiet=False):
    calls = {}
    calls_by_caller = {}
    current_week_start = 0
    total = 0
    
    f = open(filename)
    
    while(True):
        line = f.readline()
        if not line:
            break
        try:
        
        #################################################
        ## Use the calls here to determine what pieces
        ## of data must exist for the line to be valid.
        ## All of those below should probably always be.
        
            phone_num = otalo_utils.get_phone_num(line)
            current_date = otalo_utils.get_date(line)
            dest = otalo_utils.get_destination(line)            
        ##
        ################################################
            #print(phone_num + ': dest = ' + dest)
            
            if phone_num_filter and not phone_num in phone_num_filter:
                continue
            
            if date_start:
				if date_end:
					 if not (current_date >= date_start and current_date < date_end):
						continue
				else:
					if not current_date >= date_start:
						continue

            if destnum and destnum.find(dest) == -1:
                continue

            if not phone_num in calls_by_caller:
                calls_by_caller[phone_num] = []
            
            if otalo_utils.is_prompt(line):
                prompt = otalo_utils.get_prompt(line)
                for source in SOURCES:
                    # don't count duplicate accesses by the same caller
                    if prompt.find(source) != -1 and not prompt in calls_by_caller[phone_num]:
                        if phone_num in calls:
                            calls[phone_num] += 1
                        else:
                            calls[phone_num] = 1
                        calls_by_caller[phone_num].append(prompt)
                    
                    
        except ValueError as err:
            #print("ValueError: " + line)
            continue
        except IndexError as err:
            #print("IndexError: " + line)
            continue
        except otalo_utils.PhoneNumException:
            #print("PhoneNumException: " + line)
            continue
    
    if not quiet:
        if phone_num_filter:
            print("Data for phone numbers: " + str(phone_num_filter))

        print("Number of followups, by phone number:")
        calls_sorted = sorted(calls.iteritems(), key=lambda(k,v): (v,k))
        calls_sorted.reverse()
        total = 0
        for num, tot in calls_sorted:
            total += tot
            print(num +": "+str(tot))
            
        print('total is ' + str(total));
    
    return calls
   
def get_hold_times(filename, hold_task, destnum=False, phone_num_filter=0, date_start=False, date_end=False, quiet=False):
	calls = {}
	callers_by_source = {}
	hold_starts = {}
	current_week_start = 0
	total = 0
	
	f = open(filename)
	
	while(True):
		line = f.readline()
		if not line:
			break
		try:
		
		#################################################
		## Use the calls here to determine what pieces
		## of data must exist for the line to be valid.
		## All of those below should probably always be.
		
			phone_num = otalo_utils.get_phone_num(line)
			current_date = otalo_utils.get_date(line)
			dest = otalo_utils.get_destination(line)			
		##
		################################################
			#print(phone_num + ': dest = ' + dest)
			
			if phone_num_filter and not phone_num in phone_num_filter:
				continue
			
			if date_start:
				if date_end:
					 if not (current_date >= date_start and current_date < date_end):
						continue
				else:
					if not current_date >= date_start:
						continue

			if destnum and destnum.find(dest) == -1:
				continue
			
			if otalo_utils.is_prompt(line):
				prompt = otalo_utils.get_prompt(line)
			else:
				prompt = ''
			
			#print ("prompt is " + prompt)
			# register caller by source; ignore subsequent registrations
			if prompt.find(hold_task + '_tip') != -1 and not phone_num in callers_by_source:
				#print ('adding caller ' + phone_num + ' with sourceline ' + prompt)
				callers_by_source[phone_num] = prompt
			
			# start counting from when the hold prompt plays;
			# override previous starts since hold prompt can be repeated
			if prompt.find('hold') != -1 and phone_num in callers_by_source:
				#print ('adding hold start: ' + phone_num)
				hold_starts[phone_num] = current_date
					
			if phone_num in hold_starts and (prompt.find(hold_task + '_solution') != -1 or line.find('End call') != -1):
				hold_secs = (current_date - hold_starts[phone_num]).seconds
				source_line = callers_by_source[phone_num]
				
				for source in SOURCES:
					if source_line.find(source) != -1:
						# don't override previous entries in case a stray end call or solution prompt plays
						if not source in calls :
							#print("creating lst for " + source + 'with ' + phone_num + ' (' + str(hold_secs) )	
							calls[source] = [{phone_num:hold_secs}]
						elif not phone_num in [pair.keys()[0] for pair in calls[source]]:						
							#print("appending " + phone_num + ' (' + str(hold_secs) + ') to src ' + source )
							calls[source].append({phone_num:hold_secs})
					
					
		except ValueError as err:
			#print("ValueError: " + line)
			continue
		except IndexError as err:
			#print("IndexError: " + line)
			continue
		except otalo_utils.PhoneNumException:
			#print("PhoneNumException: " + line)
			continue
	
	if not quiet:
		if phone_num_filter:
			print("Data for phone numbers: " + str(phone_num_filter))

		print("Hold times for each phone number, in seconds, by source:")
		sources = calls.keys()
		for source in sources:
			holds = ''
			for pair in calls[source]:
				num = pair.keys()[0]
				holds += num +"-"+str(pair[num]) + ', '
			
			print(source+": "+holds[:-2])
		
		print("Hold times, in seconds, by source:")
		sources = calls.keys()
		for source in sources:
			print(source)
			holds = ''
			for pair in calls[source]:
				num = pair.keys()[0]
				#holds += str(pair[num]) + ', '
				print(str(pair[num]))
			#print(source+": "+holds[:-2])
	
	return calls

def print_tips_by_num(numbers):
	print('Number\t\tT1\tT2\tT3\tT4\tT5\tT6\tT7\tT8')
	for num in numbers:
		subject = Subject.objects.get(number=str(num))
		group = subject.group
		tip_str = str(num) + '\t'
		for i in range(1,len(GROUPS[0])):
			tip_str += GROUPS[group][i] + '\t'
		print(tip_str)

def print_completed_by_num(numbers, date_start, date_end, ninterval):
	print('Number\t\tT1\tT2\tT3\tT4\tT5\tT6\tT7\tT8')
	interval = timedelta(ninterval)
	for num in numbers:
		subject = Subject.objects.get(number=str(num))
		completed_str = str(num) + '\t'
		date = date_start
		while date < date_end:
			completed = Call.objects.filter(date__gt=date, date__lt=date+interval, complete=True, subject=subject)
			if completed:
				completed_str += '\t'
			else:
				completed_str += 'N/A\t'
			date += interval
		print(completed_str)

def print_followup_by_num(f, numbers, date_start, date_end, ninterval):
	print('Number\t\tT1\tT2\tT3\tT4\tT5\tT6\tT7\tT8')
	interval = timedelta(ninterval)
	for num in numbers:
		#subject = Subject.objects.get(number=str(num))
		called_str = str(num) + '\t'
		date = date_start
		while date < date_end:
			cnt = 0
			#completed = Call.objects.filter(date__gt=date, date__lt=date+interval, complete=True, subject=subject)
			completed = True
			if completed:	
				calls = get_followups(f, phone_num_filter=str(num),date_start=date, date_end=date+interval, quiet=True)
				if calls:
					for (x,y) in calls.iteritems():
						cnt += len(y)
					#called_str += str(cnt) + '\t'
					called_str += '1\t'
				else:
					called_str += '0\t'
			else:
				called_str += 'N/A\t'
			date += interval
		print(called_str)

def print_holds_by_num(f, numbers, hold_task, date_start, date_end, ninterval):
	#print('Number\t\tT1\tT2\tT3\tT4\tT5\tT6\tT7\tT8')
	print('Number\t\tT8')
	interval = timedelta(ninterval)
	for num in numbers:
		subject = Subject.objects.get(number=str(num))
		called_str = str(num) + '\t'
		date = date_start
		while date < date_end:
			hold_str = ''
			holds = get_hold_times(f, hold_task, phone_num_filter=[str(num)], date_start=date, date_end=date+interval, quiet=True)
			if holds:
				for (x,y) in holds.iteritems():
					for pair in y:
						hold_str += str(pair[pair.keys()[0]]) + ','
				called_str += hold_str[:-1] + '\t'
			else:
				called_str += 'N/A\t'
			date += interval
		print(called_str)
def main():
	if not len(sys.argv) > 1:
		print("Wrong")
	else:
		f = sys.argv[1]
	
	#get_followups_by_number(f)
	#date_start = datetime(month=8,day=16,year=2010)
	#date_end = datetime(month=8,day=30,year=2010)
	#get_followups(f,date_start=date_start,date_end=date_end)
	#get_hold_times(f, "T8", date_start=date_start)
	numbers = [9978063662,
9974961909,
9974122869,
9925795859,
9925310504,
9924885762,
9924773951,
9913991823,
9913127379,
9909484864,
9909480769,
9909397629,
9904689792,
9904075323,
9898836049,
9898533546,
9879732707,
9825875631,
9909189931,
9824829592,
9737232762,
9727281416,
9726660105,
9725850145,
9725729441,
9725102377,
9724774625,
9724537977,
9714959731,
9714736647,
9714560511,
9714327015,
9714246198,
9714148023,
9687433392,
9638391892,
9624779381,
9624086950,
9601145413,
9586312853,
9574978416,
9574416890,
9574188431,
9574013934,
9904001667,
9537559883,
9537293638,
9429943304,
9429609357,
9429527617,
9429352624,
9429140966,
9427667496,
9427535277,
9327477984,
9228064441,
9227352190,
8140877835,
9904622685,
9879337160,
9879350157,
9925684373,
9687193246,
9974572646,
9979314531,
9428984533,
9327538732,
9974669323,
9824262550,
9638844584,
9428671603,
9978383329,
9723332236,
9998664234,
9723887815,
9427145486,
9426373684,
9428500591,
8140252102,
9099193500,
9726485205,
9974641216,
9727128162,
9427330743,
9978163140,
9925525663,
9904634418,
9726659436,
9726356814,
9725331043,
9723658772,
9429269788,
9426554773,
9276502212,
9979711961,
9979459741,
9979087320,
9978564476,
9879318158,
9724632394,
9723181832,
9714001359,
9586058070,
9429218227,
9428568904,
9016638646,
9979273464,
9978719704,
9978305087,
9974541880,
9925618145,
9925508550,
9925316417,
9924834046,
9924284505,
9913282079,
9913213272,
9909893827,
9909847737,
9909621073,
9904925740,
9904575420,
9879841603,
9879069329,
9825524687,
9825378326,
9825279001,
9726046695,
9726074838,
9726186380,
9726477492,
9726489610,
9726665628,
9726883910,
9879879905,
9727281261,
9727424483,
9727608301,
9727641947,
9727642827,
9727689590,
9727722178,
9727696645,
9737362944,
9737369863,
9737389044,
9737583425,
9737694692,
9737871915,
9824241614,
9824784871,
9824928848,
9824992905,
9879632462,
9879319268,
9879274611,
9879188943,
9879099378,
9879044080,
9879022533,
9825951687,
9825336919,
9824967764,
9737622557,
9737386565,
9737125763,
9727307784,
9726668506,
9726592014,
9726492370,
9726406074,
9726384118,
9726324249,
9725061283,
9725040752,
9724522159,
9723684923,
9723011177,
9712756833,
9638099359,
7567331806,
2877222260,
2737236315,
9998952575,
9974540063,
9924500374,
9913921466,
9825578331,
9824171748,
9724700753,
9714934982,
9925716672,
9925513984,
9723800850,
9427379911,
2744253277,
2697342397,
9428126906,
9016249969,
9924341087,
9909759893,
9726331577,
9726592964,
9726051598,
9724884238,
9624820573,
9429251501,
9428557642,
9228816198,
9099514664,
8140437612,
8140255231,
2833295141,
7567164618,
9925364656,
9913398273,
9726061931,
9624372044,
9601567245,
9586132465,
9426320340,
9998318554,
9624045636,
9978173169,
9925660140,
9879876394,
9825726214,
9727696899,
9726814182,
9726766913,
9638346557,
8980271921,
9925583401,
9712198296,
9824367539,
9724443284,
9427249401,
9016840997,
8141847594,
9909233817,
9724581388,
9624451766,
9913332272,
9427555857,
9638660663,
9924355148,
9428987491,
2742295194,
9428241676,
9428136567,
9428063295,
9427564859,
8000688598,
9998088731,
9979625862,
9974484853,
9925880755,
9925145434,
9925546520,
9924528796,
9924584010,
9913657611,
9913422018,
9912011936,
9909839117,
9909492653,
9909399897,
9909070236,
9904622512]
	numbers =[ 
9624699647,
9429513066,
9824836342,
9429797456,
9375847394,
9737706947,
8140644028,
9429271905]
	numbers_strs = [str(num) for num in numbers]
	#print_tips_by_num(numbers)		 
	start = datetime(month=8,day=16,year=2010)
	end = datetime(month=9,day=1,year=2010)
	#print_completed_by_num(numbers, start, end, 2)
	print_followup_by_num(f, numbers, start, end, 2)
	#print_holds_by_num(f, numbers, "T8", start, end, 2)
	#get_followups(f, phone_num_filter=numbers_strs, date_start=start, date_end=end)
main()
