#!/usr/bin/python2.6

import os
import sys
from datetime import date, datetime, timedelta

N = 14

if __name__ == '__main__':
    if len(sys.argv) > 2:
        print 'usage: generateWorkDaysFromCurrent.py [<days count>]'
        sys.exit(1)

    if len(sys.argv) == 2:
        days_count = int(sys.argv[1])
    else:
        days_count = 14

    cur_day = datetime.today() + timedelta(N)


    if cur_day.weekday() in [5,6]: #Saturday and Sunday
        sys.exit(0)

    day = '%i.%i.%i'%(cur_day.day, cur_day.month, cur_day.year)
    print 'generating %s' % day

    os.system('python2.6 /root/remotePsychologist/generateWorkTime.py %s %s'%(day, day))
