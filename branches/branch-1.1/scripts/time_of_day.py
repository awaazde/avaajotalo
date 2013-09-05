import otalo
import sys
	
#index [0(Monday),6], default is no day specified
def num_calls_within_day(filename, day_idx=-1, log="Start call"):
	calls = [0,0,0,0,0,0]
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

			phone_num = otalo.get_phone_num(line)
			current_date = otalo.get_date(line)		
		##
		################################################

			time = otalo.get_time(line)

			if line.find(log) != -1 and (current_date.weekday() == day_idx or day_idx == -1):
				if time.hour < 4:
					calls[0] += 1
				elif time.hour < 8:
					calls[1] += 1
				elif time.hour < 12:
					calls[2] += 1
				elif time.hour < 16:
					calls[3] += 1
				elif time.hour < 20:
					calls[4] += 1
				elif time.hour < 24:
					calls[5] += 1

		except ValueError:
			#print("ValueError: " + str(err.args))
			continue
		except IndexError:
			continue
		except otalo.PhoneNumException:
			continue

	print("Number of calls within day_idx " + str(day_idx) + ":")
	print("From midnight to 4am: " + str(calls[0]))
	print("From 4am to 8am: " + str(calls[1]))
	print("From 8am to 12pm: " + str(calls[2]))
	print("From 12pm to 4pm: " + str(calls[3]))
	print("From 4pm to 8pm: " + str(calls[4]))
	print("From 8pm to midnight: " + str(calls[5]))

def num_calls_within_week(filename, log="Start call"):
	calls = {}
	current_week_start = 0
	current_week_calls = 0
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

			phone_num = otalo.get_phone_num(line)
			current_date = otalo.get_date(line)		
		##
		################################################
			if not current_week_start:
				current_week_calls = 0				
				current_week_start = current_date
				calls[current_week_start] = [0,0,0,0,0,0,0]

			delta = current_date - current_week_start

			if delta.days > 6:
				#call_percents = [float(d) / float(current_week_calls) for d in calls[current_week_start] ]
				#calls[current_week_start] = call_percents
				current_week_calls = 0				
				current_week_start = current_date
				calls[current_week_start] = [0,0,0,0,0,0,0]

			if line.find(log) != -1:
				current_week_calls += 1
				calls[current_week_start][current_date.weekday()] += 1

		except ValueError:
			#print("ValueError: " + str(err.args))
			continue
		except IndexError:
			continue
		except otalo.PhoneNumException:
			continue
			
	# process percents for final week
	#call_percents = [float(d) / float(current_week_calls) for d in calls[current_week_start] ]
	#calls[current_week_start] = call_percents
	
	print("Number of " + log + "'s by day of the week (0 is Monday):")
	total = [0,0,0,0,0,0,0]
	dates = calls.keys()
	dates.sort()
	mon_wed = {}
	fri_sun = {}
	for date in dates:
		calls_by_week = calls[date]
		new_total = [total[i] + calls_by_week[i] for i in range(len(total))]
		total = new_total
		
		mon_wed[date] = str(sum(calls_by_week[:3]))
		fri_sun[date] = str(sum(calls_by_week[4:]))
	
	print('Calls Mon-Wed:')
	for date in dates:
		print(otalo.date_str(date) + ': ' + mon_wed[date])
		
	print('Calls Fri-Sun:')
	for date in dates:
		print(otalo.date_str(date) + ': ' + fri_sun[date])
		
	print("Total:")
	for i in range(len(total)):
		print("Day " + str(i) + ": " + str(total[i]))

def main():
	if not len(sys.argv) > 1:
		print("Wrong")
	else:
		f = sys.argv[1]
		idx = -1
		if len(sys.argv) == 3:
			idx = sys.argv[2]

		num_calls_within_day(f)
		num_calls_within_week(f)

			
main()
