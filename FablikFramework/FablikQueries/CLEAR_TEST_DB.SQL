
DROP DATABASE fablik_queries_test;

BEGIN;

\c fablik_base


DELETE FROM bf_sql_result WHERE query_id=666;
DELETE FROM bf_sql_filter WHERE query_id=666;
DELETE FROM bf_sql_query WHERE ID=666;
DELETE FROM bf_applicationinterface WHERE ID=666;


END;
