
CREATE TABLE logs (
	id serial NOT NULL, 
    host varchar(64) default NULL,
    facility varchar(10) default NULL,
    priority varchar(10) default NULL,
    level varchar(10) default NULL,
    tag varchar(10) default NULL,
    log_timestamp timestamp default NULL,
    program varchar(64) default NULL,
    msg text,
    PRIMARY KEY (id)
);
