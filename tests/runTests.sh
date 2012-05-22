#!/bin/sh

TEST_DB_GENERATOR=./tests/testDB.py

PYTHONPATH="." /usr/bin/python $TEST_DB_GENERATOR



TEST_SET="
blik/management/tests/cust_cluster_type_test.py
"

for PY in $TEST_SET ; do
    echo "* Run $PY"
    /usr/bin/python "$PY"
    rc=$?
    if [ $rc -ne 0 ] ; then
        echo "*** unit tests failed ***"
        exit $rc
    fi
done


