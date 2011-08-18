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

    NODES = {}
    rows = dbconn.select("SELECT hostname, id FROM nm_node")
    for row in rows:
        NODES[row[0]] = row[1]

    while True:
        in_line = sys.stdin.readline()

        if not in_line: #EOF occured
            break

        host, facility, priority, level, tag, program, isodate, msg = in_line.split('[-]')

        host = host.strip()
        node_id = NODES.get(host, None)

        if node_id is None:
            rows = dbconn.select("SELECT id FROM nm_node WHERE hostname=%s",(host,))
            if rows:
                NODES[host] = rows[0][0]
                node_id = rows[0][0]

        dbconn.modify("INSERT INTO logs (node_id, host, facility, priority, level, tag, program, log_timestamp, msg) \
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (node_id, host, facility.strip(), priority.strip(),
                            level.strip(), tag.strip(), program.strip(), isodate.strip(), msg.strip()))




if __name__ == "__main__":
    try:
        writer_loop()
        logger.info('Log writer exiting...')
    except Exception, ex:
        logger.error("log writer main loop caught exception: %s" % ex)
        sys.exit(1)

