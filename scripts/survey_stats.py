import otalo_utils
import sys
from datetime import datetime

SOURCES = ["E1", "E2", "P1", "P2"]

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
			total += calls[source]
			print(source +": "+str(calls[source]))

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
			holds = ''
			for pair in calls[source]:
				num = pair.keys()[0]
				holds += str(pair[num]) + ', '
			
			print(source+": "+holds[:-2])
	
	return calls
	
def main():
	if not len(sys.argv) > 1:
		print("Wrong")
	else:
		f = sys.argv[1]
	
	#get_followups_by_number(f)
	get_hold_times(f, "T8")
			
main()
