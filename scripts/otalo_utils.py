from datetime import datetime

blacklist = ["9537165413", "5303044777", "1000", "1001", "1002", "1003", "401", "4044", "4049", "9586550654", "9723037029", "9427263092", "9723149575", "9714785932", "9327572297", "9974852923", "9904259110","2847271618"]

class PhoneNumException(Exception):
	pass

def get_phone_num(line):
	data = line.split('\t')
	# get last 10 digits only
	num = data[1][-10:]
	
	if num in blacklist:
		raise PhoneNumException
	
	return num

def get_destination(line, legacy_log=False):
	if not legacy_log:
		data = line.split('\t')
		num = data[2]
		
		return num
	else:
		return -1;

def get_date(line, legacy_log=False):
	data = line.split('\t')
	if not legacy_log:
		ts = int(data[3])
	else:
		ts = int(data[2])
		
	d = datetime.fromtimestamp(ts)

	return d

def is_prompt(line, legacy_log=False):
	data = line.split('\t')
	if not legacy_log:
		type = data[4]
	else:
		type = data[3]
	
	return type == "Prompt"

def get_prompt(line, legacy_log=False):
	data = line.split('\t')
	if not legacy_log:
		prompt = data[5]
	else:
		prompt = data[4]
		
	return prompt
	
def get_time(line):
	data = line.split('\t')
	ts = int(data[3])
	d = datetime.fromtimestamp(ts)

	return d
	
def date_str(date):
	#return date.strftime('%Y-%m-%d')
	return date.strftime('%b %d, %Y')
	
def time_str(time):
	return time.strftime("%I:%M:%S %p")

def get_content_number(line):
	data = line.split(',')
	date_plus_number = data[0]
	num_plus_prefix = date_plus_number[:date_plus_number.index('_')]
	num = num_plus_prefix[-10:]
	
	return(num.strip())
	
def get_content_date(line):
	data = line.split(',')
	date_plus_number = data[0]
	full_date = date_plus_number[date_plus_number.index('_')+1:]
	# hardcode year 2009 (also assumes september is not encoded as 09, which is a big if)
	if full_date.find('09') != -1:
		date = full_date[:full_date.index('09')]
		# the month comes as two numbers that must be summed together
		# to get the actual month (do not ask why, we have no idea why Java did this)
		month_sum = date[-2:]
		month = int(month_sum[0]) + int(month_sum[1])
		day = date[:-2]
		year = '2009'
	else: #no elif because it's either 08 or 09; throw ValueError otherwise
		date = full_date[:full_date.index('08')]
		month_sum = date[-3:]
		month = int(month_sum[0]) + int(month_sum[1:])
		day = date[:-3]
		year = '2008'
	
	d = datetime.strptime(year+'-'+str(month)+'-'+day, "%Y-%m-%d")
	return d
	
def get_content_length(line):
	data = line.split(',')
	time = data[1]
	mins = time[:time.index(':')]
	secs = time[time.index(':')+1:]
	return int(mins)*60 + int(secs)
	
def get_content_type(line):
	data = line.split(',')
	return data[2]
	
def get_content_name(line):
	data = line.split(',')
	return data[3]

def get_content_village(line):
	data = line.split(',')
	return data[4]

def get_content_transcript(line):
	data = line.split(',')
	return data[5]

def get_content_crop(line):
	data = line.split(',')
	return data[6]
	
def get_content_topic(line):
	data = line.split(',')
	return data[7]

geography_map = {}
age_map = {20:[], 25:[], 30:[], 35:[], 40:[], 45:[], 50:[], 65:[], 'NONE SPECIFIED':[]}
education_map = {6:[], 8:[], 10:[], 12:[], 'B':[], 'M.A.':[], 'NONE SPECIFIED':[]}
farm_size_map = {2:[], 5:[], 8:[], 12:[], 15:[], 20:[], 30:[], 60:[], 'NONE SPECIFIED':[]}

def load_demographics(filename):
	f = open(filename)
		
	while(True):
		line = f.readline()
		if not line:
			break
			
		try:
			data = line.split(',')
			phone_num = data[5]
			if phone_num == '':
				continue
			
			#getting district for now
			location = data[4]
			
			age = data[7]
			education = data[8]
			farm_size = data[9]		
			
			if location in geography_map.keys():
				geography_map[location].append(phone_num) 
			else:
				geography_map[location] = [phone_num]
			
			bucket = min([b for b in age_map.keys() if int(age) <= b]) if not age == '' else 'NONE SPECIFIED'
			age_map[bucket].append(phone_num)
			
			if education == 'B' or education == 'M.A.':
				bucket = education
			else:
				bucket = min([b for b in education_map.keys() if int(education) <= b]) if not education == '' else 'NONE SPECIFIED'  
			education_map[bucket].append(phone_num)
			
			bucket = min([b for b in farm_size_map.keys() if int(farm_size) <= b]) if not age == '' else 'NONE SPECIFIED'
			farm_size_map[bucket].append(phone_num)
					
		except ValueError as err:
			continue
			
def get_geo_map():
	return geography_map

def get_age_map():
	return age_map

def get_edu_map():
	return edu_map

def get_farm_size_map():
	return farm_size_map()
	
content_blacklist = []
def load_content_blacklist(filename):
	f = open(filename)
			
	while(True):
		line = f.readline()
		if not line:
			break
		line = line.strip('\n')
		content_blacklist.append(line)
		content_blacklist.append(line+'.')

def is_keyword(w):
	return not w.lower() in content_blacklist
