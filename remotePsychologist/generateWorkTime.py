#!/usr/bin/python2.6

import os
import psycopg2 as psycopg
from settings import *
import sys
from datetime import date, datetime, timedelta

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'usage: generateWorkTime.py <start date> <end date>'
        sys.exit(1)

    start_date = sys.argv[1].split('.')
    start_date = date(year=int(start_date[2]), month=int(start_date[1]), day=int(start_date[0]))

    end_date = sys.argv[2].split('.')
    end_date = date(year=int(end_date[2]), month=int(end_date[1]), day=int(end_date[0]))

    if start_date > end_date:
        print 'start date must be lower then end time'
        print start_date, end_date
        sys.exit(2)

    conn = psycopg.connect(database=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT)
    cursor = conn.cursor()

    try:
        current_day = start_date
        while True:
            cursor.execute("SELECT count(id) FROM rp_worktime WHERE start_worktime > %s AND stop_worktime < %s", (datetime(current_day.year, current_day.month, current_day.day), datetime(current_day.year, current_day.month,current_day.day,23,59)) )

            data = cursor.fetchone()

            if data[0]:
                print 'Skiping day: %s'%current_day
            else:
                print 'Generating day: %s'%current_day
                for region in WORK_WINDOW:
                    start = datetime(current_day.year, current_day.month, current_day.day, hour=region[0][0], minute=region[0][1])
                    end = datetime(current_day.year, current_day.month, current_day.day, hour=region[1][0], minute=region[1][1])

                    cursor.execute('INSERT INTO rp_worktime (start_worktime, stop_worktime) VALUES (%s, %s)', (start, end))

            if current_day == end_date:
                break

            current_day += timedelta(1)

        conn.commit()
    except Exception, err:
        print 'ERROR: %s'%err
    finally:
        conn.close()
