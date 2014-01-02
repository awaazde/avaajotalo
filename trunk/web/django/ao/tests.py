import sys
from django.test import TestCase
from datetime import datetime, timedelta
from django.contrib.auth.models import User as AuthUser
from otalo.ao.models import *
from otalo.surveys.models import *
from otalo.ao import tasks
import broadcast
from awaazde.streamit import streamit

class BcastTest(TestCase):
    INTERVAL_MINS = 10
    
    def setUp(self):
        d1 = Dialer.objects.create(base_number=5002, type=Dialer.TYPE_PRI, max_nums=10, max_parallel_out=4, dialstring_prefix='user/', interval_mins=self.INTERVAL_MINS)                
    
    def test_bcast(self):
        dialers = Dialer.objects.all()
        
        subjects = []
        for i in range(20):
            s = Subject.objects.create(name='s'+str(i), number=str(i))
            subjects.append(s)
        
        now = datetime.now()
        nextyear = now.year+1
        d = datetime(year=nextyear, month=1, day=1, hour=10, minute=40)
        
        # Create a template
        line = Line.objects.create(number='5002', name='TEST', language='eng')
        for dialer in dialers:
            line.dialers.add(dialer)
        template = Survey.objects.create(number=line.number, template=True, created_on=d, name='TEST_TEMPLATE')
        
        # create bcast
        broadcast.regular_bcast(line, template, subjects, 0, d)
        
        # schedule bcasts
        tasks.schedule_bcasts.delay(time=d, dialers=dialers)
        self.assertEqual(Call.objects.filter(date=d).count(), 4)
        
        d += timedelta(minutes=self.INTERVAL_MINS)
        tasks.schedule_bcasts.delay(time=d, dialers=dialers)
        self.assertEqual(Call.objects.filter(date=d).count(), 4)
         
        d += timedelta(minutes=self.INTERVAL_MINS)
        tasks.schedule_bcasts.delay(time=d, dialers=dialers)
        self.assertEqual(Call.objects.filter(date=d).count(), 4)
         
        d += timedelta(minutes=self.INTERVAL_MINS)
        tasks.schedule_bcasts.delay(time=d, dialers=dialers)
        self.assertEqual(Call.objects.filter(date=d).count(), 4)
         
        d += timedelta(minutes=self.INTERVAL_MINS)
        tasks.schedule_bcasts.delay(time=d, dialers=dialers)
        self.assertEqual(Call.objects.filter(date=d).count(), 4)
         
        d += timedelta(minutes=self.INTERVAL_MINS)
        tasks.schedule_bcasts.delay(time=d, dialers=dialers)
        self.assertEqual(Call.objects.filter(date=d).count(), 0)
         
        # complete some calls
        completed = [10,11,12,13,14]
        Call.objects.filter(subject__number__in=completed).update(complete=True, duration=60)
        self.assertEqual(Call.objects.filter(complete=True).count(), 5)
        
'''
****************************************************************************
*************************** COMMAND LINE TESTS *****************************
****************************************************************************
'''

if __name__=="__main__":
    if "--create_bcasts" in sys.argv:
        lineid = sys.argv[2]
        templateid = sys.argv[3]
        subjectids = sys.argv[4].split(',')
        
        bcast_date = None
        if len(sys.argv) > 5:
            bcast_date = datetime.strptime(sys.argv[5], "%m-%d-%Y")
        
        line = Line.objects.get(pk=int(lineid))
        template = Survey.objects.get(pk=int(templateid))
        subjects = Subject.objects.filter(pk__in=subjectids)
        
        
        # create bcast
        result = tasks.regular_bcast.delay(line, template, subjects, 0, bcast_date)
        self.assertTrue(result.successful())
    elif "--schedule_bcasts" in sys.argv:
        dialerids = sys.argv[2].split(',')
        dialers = Dialer.objects.filter(pk__in=dialerids)
        
        d = None
        if len(sys.argv) > 3:
            d = datetime.strptime(sys.argv[3], "%m-%d-%Y")
            
        tasks.schedule_bcasts.delay(dialers=dialers, time=d)
    elif "--blank_template" in sys.argv:
        number = sys.argv[2]
        lang = sys.argv[3]
        prefix = sys.argv[4]
        suffix = ''
        if len(sys.argv) > 5:
            suffix = sys.argv[5]
        blank_template(number, lang)