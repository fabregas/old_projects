
CREATE DATABASE fablik_queries_test;

BEGIN;

\c fablik_queries_test

CREATE TABLE TEST_USER (
	id serial NOT NULL,
	firstname varchar(50) NOT NULL,
	lastname varchar(50) NOT NULL,
	age integer NOT NULL,
	birthday timestamp NOT NULL,
	work_position varchar(50) NOT NULL,
	description varchar(1024)
);


INSERT INTO test_user (firstname, lastname, age, birthday, work_position, description) VALUES  ('Konstantin', 'Andrusenko', 22, '11.03.1987' ,'Atchitect', 'it is read user...I am...');

INSERT INTO test_user (firstname, lastname, age, birthday, work_position, description) VALUES  ('Oleg', 'Andrusenko', 21, '07.13.1989' ,'student', 'it is read user...my brother...');

INSERT INTO test_user (firstname, lastname, age, birthday, work_position, description) VALUES  ('TestName1', 'TestName2', 50, '02.12.1960' ,'test_position', 'it is not read user...');

INSERT INTO test_user (firstname, lastname, age, birthday, work_position, description) VALUES  ('TestName3', 'TestName4', 30, '02.12.1980' ,'test_position2', 'it is not read user...');


\c fablik_base

INSERT INTO bf_applicationinterface (id, db_connect_string , sid) VAlues (666, 'host=127.0.0.1 user=postgres dbname=fablik_queries_test','test_db');

INSERT INTO  bf_sql_query (id, interface_id, sid, query, modify_datetime) Values (666, 666, 'test_sql_query', 'SELECT id, lastname FROM TEST_USER WHERE lastname like %(lastname)s ?AND age > %(gAge)s? ?AND age < %(lAge)s? ?AND work_position=%(workPosition)s?' ,current_timestamp);

END;
