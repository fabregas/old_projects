#!/bin/sh

TEST_DB_GENERATOR=./tests/testDB.py

/usr/bin/python $TEST_DB_GENERATOR



TEST_SET="
./tests/nodesManager/friClientLibrary_test.py
./tests/nodesManager/operationsEngine_test.py
./tests/nodesManager/dbusAgent_test.py
./tests/nodesManager/nodesMonitor_test.py
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
