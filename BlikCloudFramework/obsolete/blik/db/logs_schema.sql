
CREATE TABLE logs (
	id serial NOT NULL, 
    node_id bigint default NULL,
    host varchar(64) NOT NULL,
    facility varchar(10) default NULL,
    priority varchar(10) default NULL,
    level varchar(10) default NULL,
    tag varchar(10) default NULL,
    log_timestamp timestamp default NULL,
    program varchar(64) default NULL,
    msg text,
    PRIMARY KEY (id)
);

ALTER TABLE logs ADD CONSTRAINT FK_LOGS_NODE_ID
	FOREIGN KEY (node_id) REFERENCES NM_NODE (id);
