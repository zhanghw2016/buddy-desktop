/* alter snapshot_resource*/
ALTER TABLE snapshot_resource RENAME COLUMN desktop_resource TO desktop_resource_id;
ALTER TABLE snapshot_resource DROP COLUMN curr_chain;
ALTER TABLE snapshot_resource DROP COLUMN snapshot_count;
ALTER TABLE snapshot_resource ADD COLUMN snapshot_group_snapshot_id varchar(50) DEFAULT '' NOT NULL;
ALTER TABLE snapshot_resource ADD COLUMN ymd varchar(20) DEFAULT '' NOT NULL;
ALTER TABLE snapshot_resource DROP CONSTRAINT snapshot_resource_pkey;
ALTER TABLE snapshot_resource ADD PRIMARY KEY(desktop_snapshot_id, desktop_resource_id);

/* alter desktop_snapshot*/
ALTER TABLE desktop_snapshot ADD COLUMN head_chain integer DEFAULT 0 NOT NULL;
ALTER TABLE desktop_snapshot RENAME COLUMN desktop_resource TO desktop_resource_id;
ALTER TABLE desktop_snapshot DROP COLUMN snapshot_scope;
ALTER TABLE desktop_snapshot ALTER COLUMN desktop_resource_id SET DEFAULT '';

/* alter snapshot_group*/
ALTER TABLE snapshot_group ADD COLUMN transition_status varchar(50) DEFAULT '' NOT NULL;
ALTER TABLE snapshot_group ADD COLUMN status varchar(50) DEFAULT 'normal' NOT NULL;

/* alter snapshot_group_resource*/
ALTER TABLE snapshot_group_resource DROP COLUMN desktop_snapshot_id;
ALTER TABLE snapshot_group_resource RENAME COLUMN resource_id TO desktop_resource_id;


/* create table snapshot_group_snapshot*/
CREATE TABLE snapshot_group_snapshot
(
    snapshot_group_snapshot_id varchar(50) PRIMARY KEY NOT NULL,
    snapshot_group_id varchar(50) DEFAULT '' NOT NULL,
    transition_status varchar(50) DEFAULT '' NOT NULL,
    status varchar(50) DEFAULT 'normal' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    owner varchar(255) NOT NULL,
    zone varchar(50) DEFAULT '' NOT NULL

);

/*update zone_config*/
UPDATE zone_config SET max_snapshot_count=7;
