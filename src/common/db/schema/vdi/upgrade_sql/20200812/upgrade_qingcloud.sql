ALTER TABLE file_share_service ADD COLUMN scope varchar(50) DEFAULT 'part_roles' NOT NULL;
ALTER TABLE file_share_group_user ADD COLUMN file_share_group_dn text DEFAULT '' NOT NULL;