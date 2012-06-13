import os, sys, csv, shutil
from datetime import datetime, timedelta
from django.conf import settings
from otalo.surveys.models import Subject, Survey, Prompt, Option, Param, Call, Input
from otalo.AO.models import Line, Forum, Message_forum
import otalo_utils, num_calls, stats_by_phone_num, call_duration

'''
****************************************************************************
******************* CONSTANTS **********************************************
****************************************************************************
'''
NUMBER='7961907766'
BLOOD_OUTPUT_DIR = ''
PREFIX='freetdm/grp1/a/0'
SUFFIX=''

'''
****************************************************************************
******************* Reporting **********************************************
****************************************************************************
'''
    
def daily_digest(number):
     
    f = settings.LOG_ROOT + 'blood_'+NUMBER[-8:]+'.log'
    now = datetime.now()
    # reset to beginning of day
    today = datetime(year=now.year, month=now.month, day=now.day)
    oneday = timedelta(days=1)
    #today = today - oneday
    
    print("<html>")
    print("<head><STYLE TYPE='text/css'> .smalltable TD, .smalltable TR {font-family: Arial; font-size: 10pt;} </STYLE></head>")
    print("<div> Below are basic usage statistics for IBD PhoneBank over the last four days, starting with today. </div>")
    # calls
    print("<div><h4>Number of Incoming Calls</h4></div>")
    print("<table>")
    
    for i in range (0,4):
        calls = num_calls.get_calls(filename=f, destnum=number, date_start=today-oneday*i, date_end=today-oneday*(i-1), quiet=True,transfer_calls='INBOUND_ONLY')
        ncalls = calls[calls.keys()[0]] if calls else 0
        print("<tr>")
        print("<td width='100px'>"+otalo_utils.date_str(today-oneday*i)+"</td>")
        # since a single day's calls can only be bucketed into a single week
        print("<td>"+str(ncalls)+"</td>")
        print("</tr>")
        
    # call duration
    durations = call_duration.get_call_durations(filename=f, destnum=number, date_start=today, date_end=today+oneday, quiet=True, transfer_calls='INBOUND_ONLY')
    durs_by_call = durations[durations.keys()[0]] if durations else {}
    durs = [dur[1].seconds for dur in durs_by_call] 
    
    avg_dur = str(sum(durs)/len(durs)) if durs else "n/a"
    
    print("<br/><div>")
    print("<b>Average call duration (secs):</b> ")
    print(avg_dur)
    print("</div>")
    
    
    # detailed info by call
    print("<div><h4>Detailed call info</h4></div>")
    print("<table class='smalltable'>")
    print("<tr>")
    print("<td width='110px'><b>Number</b></td>")
    print("<td width='110px'><b>Call Time</b></td>")
    print("<td width='70px'><b>Language</b></td>")
    print("<td width='90px'><b>Duration (s)</b></td>")
    print("<td width='70px'><b>STD</b></td>")
    print("<td width='70px'><b>Blood Group</b></td>")
    print("<td width='70px'><b>STD repeats</b></td>")
    print("<td width='70px'><b>BG repeats</b></td>")
    print("</tr>")
    calls = get_call_info(f, date_start=today, date_end=today+oneday, quiet=True)
    for call in calls:
        print("<tr>")
        for elt in call:
            print("<td>"+str(elt)+"</td>")
        print("</tr>")
    print("</table>")
          
    print("</html>")
    
def get_call_info(filename, phone_num_filter=False, date_start=False, date_end=False, quiet=False):
    all_calls = []
    open_calls = {}
    
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
            
            if phone_num_filter and not phone_num in phone_num_filter:
                continue
                
            if date_start:
                if date_end:
                    if not (current_date >= date_start and current_date < date_end):
                        continue
                    if current_date > date_end:
                        break
                else:
                    if not current_date >= date_start:
                        continue
    
            if line.find("Start call") != -1:
                # check to see if this caller already has one open
                if phone_num in open_calls:
                    # close out call                
                    call = open_calls[phone_num]
                    dur = current_date - call['start']
                    # may not be there if it's an old number
                    stdrepeats = call['std_repeats'] if call['std_repeats'] > 0 else 'N/A'
                    bgrepeats = call['std_repeats'] if call['bg_repeats'] > 0 else 'N/A'
                    call_info = [phone_num,date_str(call['start']),str(dur.seconds),call['lang'],call['std'],call['bgid'], stdrepeats,bgrepeats]
                    
                    all_calls.append(call_info)
                    del open_calls[phone_num]
                    
                # add new call
                #print("adding new call: " + phone_num)
		# start repeat counts 1 back in order to not count the first play as a repeat
                open_calls[phone_num] = {'std':'','bgid':'', 'start':current_date,'std_repeats':-1,'bg_repeats':-1, 'lang':''}
                
            elif line.find("End call") != -1:
                if phone_num in open_calls:
                    # close out call                
                    call = open_calls[phone_num]
                    dur = current_date - call['start']
                    # may not be there if it's an old number
                    stdrepeats = call['std_repeats'] if call['std_repeats'] > 0 else 'N/A'
                    bgrepeats = call['std_repeats'] if call['bg_repeats'] > 0 else 'N/A'
                    call_info = [phone_num,date_str(call['start']),str(dur.seconds),call['lang'],call['std'],call['bgid'], stdrepeats,bgrepeats]

                    
                    all_calls.append(call_info)
                    del open_calls[phone_num]
            elif phone_num in open_calls:
                call = open_calls[phone_num]
                if line.find("dtmf") != -1 :
                    input = line[line.rfind('.wav')+4:].strip()
                    if line.find("std.wav") != -1:
                        call['std'] = input
                    elif line.find("bloodgroup.wav") != -1:
                        call['bgid'] = input
                    elif line.find("welcome.wav") != -1:
                        call['lang'] = 'hin' if input == '1' else 'eng'
                elif line.find("Prompt") != -1:
                    if line.find("std.wav") != -1:
                        call['std_repeats'] += 1
                    elif line.find("bloodgroup.wav") != -1:
                        call['bg_repeats'] += 1
                    
        except KeyError as err:
            #print("KeyError: " + phone_num + "-" + otalo.date_str(current_date))
            raise
        except ValueError as err:
            #print("ValueError: " + line)
            continue
        except IndexError as err:
            continue
        except otalo_utils.PhoneNumException:
            #print("PhoneNumException: " + line)
            continue
    
    if not quiet:    
        header = ['number','date','duration','std','std repeats', 'bgid', 'bg repeats']
        if date_start:
            outfilename='blood_'+str(date_start.day)+'-'+str(date_start.month)+'-'+str(date_start.year)[-2:]+'.csv'
        else:
            outfilename='blood.csv'
        outfilename = BLOOD_OUTPUT_DIR+outfilename
        output = csv.writer(open(outfilename, 'wb'))
        output.writerow(header)
        output.writerows(all_calls)
    
    return all_calls
    
'''
****************************************************************************
******************* UTILS **************************************************
****************************************************************************
'''    
def date_str(date):
    #return date.strftime('%Y-%m-%d')
    return date.strftime('%b-%d-%y')

def time_str(date):
    #return date.strftime('%Y-%m-%d')
    return date.strftime('%m-%d-%y %H:%M')
    
'''
****************************************************************************
******************* MAIN ***************************************************
****************************************************************************
'''
def main():
    if '--report' in sys.argv:
        f = settings.LOG_ROOT + 'blood_'+NUMBER[-8:]+'.log'
        #get_call_info(f)
        daily_digest(NUMBER)
   
main()
