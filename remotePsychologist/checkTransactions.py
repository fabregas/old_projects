#!/usr/bin/python2.6

import sys
from django.conf import settings
import settings as cust_settings

settings.configure(cust_settings)
from remotepsy import views

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'usage: checkTransactions.py init|wait'
        sys.exit(1)

    check_type = sys.argv[1]

    if check_type not in ['init', 'wait']:
        print 'Unexpect check type: %s'%check_type
        sys.exit(1)

    views.check_transactions(check_type)

    print 'Transactions checked!'
