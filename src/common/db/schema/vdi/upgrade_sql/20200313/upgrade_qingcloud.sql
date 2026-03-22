ALTER TABLE desktop_group_user DROP COLUMN is_lock;
ALTER TABLE delivery_group_user DROP COLUMN is_lock;
ALTER TABLE apply ADD COLUMN approve_status varchar(50) DEFAULT '' NOT NULL;
ALTER TABLE apply ADD COLUMN apply_group_id varchar(50) DEFAULT '' NOT NULL;
ALTER TABLE apply ADD COLUMN approve_group_id varchar(50) DEFAULT '' NOT NULL;