import otalo_utils
import sys
from datetime import datetime

SOURCES = ["E1", "E2", "P1", "P2"]

def get_followups(filename, destnum=False, prompt_filter=False, phone_num_filter=0, date_filter=0, quiet=False):
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
			
			if date_filter and (current_date.year != date_filter.year or current_date.month != date_filter.month or current_date.day != date_filter.day):
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
								calls[source] += 1
							else:
								calls[source] = 1
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
    
def get_followups_by_number(filename, destnum=False, phone_num_filter=0, date_filter=0, quiet=False):
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
            
            if date_filter and (current_date.year != date_filter.year or current_date.month != date_filter.month or current_date.day != date_filter.day):
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
	
	
def main():
	if not len(sys.argv) > 1:
		print("Wrong")
	else:
		f = sys.argv[1]
	
	get_followups_by_number(f)
			
#main()
