ALTER TABLE desktop_user ADD COLUMN reset_password integer DEFAULT 0 NOT NULL;
ALTER TABLE zone_user DROP COLUMN reset_password;
ALTER TABLE  apply_group_user ADD COLUMN user_type varchar(50) DEFAULT 'user' NOT NULL;

