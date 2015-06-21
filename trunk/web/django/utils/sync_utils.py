import os
from os import listdir
from os.path import isfile, join
from otalo.ao.models import Line, Dialer
from otalo import tasks


'''
' Sync audio file from master server in the slave machine
' file parameter is a full file path e.g. /home/awaazde/media/forum/sefc_hindi/listen.wav or stream file
' like /home/awaazde/media/2015/01/01/2015_02922323.wav
'''
def sync_file(file, dialers):
    machine_ids = get_unique_machines(dialers)
    for mid in machine_ids:
        tasks.sync_audio_file.s().delay(file, mid)
        
        

'''
' Sync all files from given folder from master server in the slave machine
'
'''
def sync_folder(filedir, dialers):
    machine_ids = get_unique_machines(dialers)
    #getting files
    files = [ join(filedir,f) for f in listdir(filedir) if isfile(join(filedir,f)) and os.path.splitext(join(filedir,f))[1] != '.zip' ]   
    
    
    #running task on every machine for every file 
    for file in files:
        for mid in machine_ids:
            tasks.sync_audio_file.s().delay(file, mid)



'''
' Sync all files from given survey from master server in the slave machine
'
'''
def sync_survey_files(survey):
    machine_ids = get_unique_machines(survey.dialers.all())
    
    for mid in machine_ids:
        tasks.sync_survey_audio.s().delay(survey, mid)

'''
This method returns machines from dialers 
'''
def get_unique_machines(dialers):
    machine_ids = []
    
    for d in dialers:
        machine_ids.append(d.machine_id[0] if d.machine_id else None)
        machine_ids = list(set(machine_ids))
    
    return machine_ids