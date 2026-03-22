ALTER TABLE file_share_service ADD COLUMN loaded_clone_instance_ip varchar(255) DEFAULT '' NOT NULL;

CREATE TABLE api_limit
(
   api_action varchar(50) PRIMARY KEY NOT NULL,
   enable integer DEFAULT 0 NOT NULL,
   refresh_interval integer DEFAULT 60 NOT NULL,
   refresh_time integer DEFAULT 5 NOT NULL
);
insert into api_limit(api_action,enable,refresh_interval,refresh_time) values('DescribePasswordPromptHaveAnswer',0,60,5);