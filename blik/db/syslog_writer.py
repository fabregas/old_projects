#!/usr/bin/python

import sys
import os
from blik.utils.databaseConnection import DatabaseConnection
from blik.utils.logger import logger


def writer_loop():
    """ The main loop.

    $HOST_FROM,$FACILITY,$PRIORITY,$LEVEL,$TAG,$PROGRAM,$ISODATE,$MSG

    Please see http://www.balabit.com/sites/default/files/documents/syslog-ng-admin-guide_en.html/reference_macros.html
    for a description of the macros used above.
    """
    dbconn = DatabaseConnection()

    while True:
        in_line = sys.stdin.readline()

        if not in_line: #EOF occured
            break

        host, facility, priority, level, tag, program, isodate, msg = in_line.split('[-]')

        dbconn.modify("INSERT INTO logs (host, facility, priority, level, tag, program, log_timestamp, msg) \
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", ( host, facility, priority, level, tag, program, isodate, msg))




if __name__ == "__main__":
    try:
        writer_loop()
    except Exception, ex:
        logger.error("log writer main loop caught exception: %s" % ex)
        sys.exit(1)

